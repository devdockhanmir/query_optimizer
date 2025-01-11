# optimizer/cost_model.py

import json
import os
import re
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from .query_parser import LogicalScan, LogicalSelect, LogicalJoin

# ----------------------------
# Global state
# ----------------------------
MOCK_DATA = {}
TABLE_STATS = {}
ML_MODELS = {}
TRAINING_DATA = {}  # for partial retraining

# ----------------------------
# 1. Data loading
# ----------------------------
def load_mock_data(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    tables = data.get("tables", {})
    for tname, rows in tables.items():
        MOCK_DATA[tname] = rows
        TABLE_STATS[tname] = {
            "row_count": len(rows),
            "cost_per_row": 0.01
        }

def init_training_data():
    for tname, rows in MOCK_DATA.items():
        TRAINING_DATA[tname] = {"X": [], "y": []}

# ----------------------------
# 2. Build initial models
# ----------------------------
def build_initial_models():
    """
    For each table, pick numeric columns, generate a few thresholds,
    estimate fraction = (col < threshold).mean(),
    train a small RandomForest.
    """
    for tname, rows in MOCK_DATA.items():
        df = pd.DataFrame(rows)
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        X_train = []
        y_train = []

        if not numeric_cols:
            ML_MODELS[tname] = {"model": None, "numeric_cols": []}
            continue

        # 2 thresholds => min, max
        for col_idx, col_name in enumerate(numeric_cols):
            cmin, cmax = df[col_name].min(), df[col_name].max()
            thresholds = np.linspace(cmin, cmax, 2)
            for th in thresholds:
                fraction = (df[col_name] < th).mean()  # fraction passing col < th
                X_train.append([col_idx, th])
                y_train.append(fraction)

        if X_train:
            model = RandomForestRegressor(n_estimators=5, max_depth=5, random_state=42)
            model.fit(X_train, y_train)
            ML_MODELS[tname] = {"model": model, "numeric_cols": numeric_cols}

            TRAINING_DATA[tname]["X"].extend(X_train)
            TRAINING_DATA[tname]["y"].extend(y_train)
        else:
            ML_MODELS[tname] = {"model": None, "numeric_cols": numeric_cols}

# ----------------------------
# 3. Single-table row count estimation
# ----------------------------
def estimate_single_table_rows(tname, predicate=None):
    base_count = TABLE_STATS[tname]["row_count"]
    if not predicate:
        return base_count

    info = ML_MODELS.get(tname)
    if not info or not info["model"]:
        return base_count / 2.0  # fallback

    numeric_cols = info["numeric_cols"]
    model = info["model"]

    # parse something like "R.col1<50" or "col1<50"
    pattern = re.compile(r"(?:[A-Z0-9_]+\.)?([A-Z0-9_]+)([<>=])(\d+)", re.IGNORECASE)
    m = pattern.match(predicate)
    if not m:
        return base_count / 2.0

    col_str = m.group(1).lower()
    op = m.group(2)
    val = float(m.group(3))

    if op != "<":
        return base_count / 2.0  # we only trained for <

    if col_str not in numeric_cols:
        return base_count / 2.0

    col_idx = numeric_cols.index(col_str)
    fraction = model.predict([[col_idx, val]])[0]
    return max(0, fraction * base_count)

# ----------------------------
# 4. Multi-table join cardinality
# ----------------------------
def estimate_join_rows(left_count, right_count, join_condition):
    if not join_condition:
        # cross product
        return left_count * right_count
    # naive approach => half of min(left_count, right_count)
    return min(left_count, right_count) * 0.5

# ----------------------------
# 5. Cost estimation
# ----------------------------
def estimate_cost(expr):
    """
    If scan => cost = row_count * cost_per_row
    If select => cost of child + (pred_rows * 0.01)
    If join => cost(left) + cost(right) + (join_rows * 0.02)
    """
    if isinstance(expr, LogicalScan):
        tname = expr.table_name
        rc = TABLE_STATS[tname]["row_count"]
        cpr = TABLE_STATS[tname]["cost_per_row"]
        return rc * cpr

    elif isinstance(expr, LogicalSelect):
        child_cost = estimate_cost(expr.child)
        child_rc = get_cardinality(expr.child)
        if isinstance(expr.child, LogicalScan):
            tname = expr.child.table_name
            pred_rows = estimate_single_table_rows(tname, expr.predicate)
        else:
            # if child is a join, naive => half
            pred_rows = child_rc / 2.0

        cpr = 0.01
        return child_cost + (pred_rows * cpr)

    elif isinstance(expr, LogicalJoin):
        left_cost = estimate_cost(expr.left)
        right_cost = estimate_cost(expr.right)
        left_rc = get_cardinality(expr.left)
        right_rc = get_cardinality(expr.right)
        join_rc = estimate_join_rows(left_rc, right_rc, expr.join_condition)
        cpr = 0.02
        return left_cost + right_cost + (join_rc * cpr)

    return 9999999.0

def get_cardinality(expr):
    if isinstance(expr, LogicalScan):
        return TABLE_STATS[expr.table_name]["row_count"]
    elif isinstance(expr, LogicalSelect):
        if isinstance(expr.child, LogicalScan):
            tname = expr.child.table_name
            return estimate_single_table_rows(tname, expr.predicate)
        else:
            child_rc = get_cardinality(expr.child)
            return child_rc / 2.0
    elif isinstance(expr, LogicalJoin):
        left_rc = get_cardinality(expr.left)
        right_rc = get_cardinality(expr.right)
        return estimate_join_rows(left_rc, right_rc, expr.join_condition)
    else:
        return 1000.0

# ----------------------------
# 6. Toy executor
# ----------------------------
def execute_plan(expr):
    """
    Return the *actual* row count by "executing" the plan on MOCK_DATA.
    """
    if isinstance(expr, LogicalScan):
        tname = expr.table_name
        return len(MOCK_DATA[tname])

    elif isinstance(expr, LogicalSelect):
        rows = materialize_rows(expr.child)
        filtered = apply_filter(rows, expr.predicate)
        return len(filtered)

    elif isinstance(expr, LogicalJoin):
        left_rows = materialize_rows(expr.left)
        right_rows = materialize_rows(expr.right)
        joined = apply_join(left_rows, right_rows, expr.join_condition)
        return len(joined)

    return 0

def materialize_rows(expr):
    """Return full row set as a list of dicts for a plan node."""
    if isinstance(expr, LogicalScan):
        return MOCK_DATA[expr.table_name]
    elif isinstance(expr, LogicalSelect):
        base = materialize_rows(expr.child)
        return apply_filter(base, expr.predicate)
    elif isinstance(expr, LogicalJoin):
        left_rows = materialize_rows(expr.left)
        right_rows = materialize_rows(expr.right)
        return apply_join(left_rows, right_rows, expr.join_condition)
    return []

def apply_filter(rows, predicate):
    filtered = []
    pat = re.compile(r"(?:[A-Z0-9_]+\.)?([A-Z0-9_]+)([<>=])(\d+)", re.IGNORECASE)
    m = pat.match(predicate)
    if not m:
        return rows
    col_str = m.group(1).lower()
    op = m.group(2)
    val = float(m.group(3))

    for r in rows:
        if col_str not in r:
            continue
        cell_val = r[col_str]
        keep = False
        if op == "<":
            keep = (cell_val < val)
        elif op == ">":
            keep = (cell_val > val)
        elif op == "=":
            keep = (cell_val == val)
        if keep:
            filtered.append(r)
    return filtered

def apply_join(left_rows, right_rows, condition):
    if not condition:
        # cross product
        out = []
        for lr in left_rows:
            for rr in right_rows:
                out.append({**lr, **rr})
        return out

    # parse "R.col1=S.colA"
    pat = re.compile(r"(?:[A-Z0-9_]+\.)?([A-Z0-9_]+)=(?:[A-Z0-9_]+\.)?([A-Z0-9_]+)", re.IGNORECASE)
    m = pat.match(condition)
    if not m:
        return []
    left_key = m.group(1).lower()
    right_key = m.group(2).lower()

    out = []
    for lr in left_rows:
        lval = lr.get(left_key, None)
        for rr in right_rows:
            rval = rr.get(right_key, None)
            if lval == rval and lval is not None:
                out.append({**lr, **rr})
    return out

# ----------------------------
# 7. Partial re-training
# ----------------------------
def partial_retrain_if_needed(table_name, col_idx, val, actual_fraction):
    """
    If there's a large discrepancy between predicted fraction 
    and actual fraction, re-fit the model with the new point.
    """
    info = ML_MODELS.get(table_name, None)
    if not info or not info["model"]:
        return

    model = info["model"]
    pred_fraction = model.predict([[col_idx, val]])[0]

    # threshold
    if abs(pred_fraction - actual_fraction) > 0.9:
        TRAINING_DATA[table_name]["X"].append([col_idx, val])
        TRAINING_DATA[table_name]["y"].append(actual_fraction)

        # capping size to 50 to avoid unbounded growth
        MAX_SIZE = 50
        if len(TRAINING_DATA[table_name]["X"]) > MAX_SIZE:
            TRAINING_DATA[table_name]["X"].pop(0)
            TRAINING_DATA[table_name]["y"].pop(0)

        # Re-train
        X_new = np.array(TRAINING_DATA[table_name]["X"])
        y_new = np.array(TRAINING_DATA[table_name]["y"])
        model.fit(X_new, y_new)
