# main.py

import os
import sys

from optimizer.query_parser import parse_query, LogicalScan, LogicalSelect, LogicalJoin
from optimizer.optimizer import Optimizer
from optimizer.visualizer import visualize_plan
from optimizer.cost_model import (
    load_mock_data,
    init_training_data,
    build_initial_models,
    estimate_cost,
    execute_plan,
    partial_retrain_if_needed,
    ML_MODELS,
    TABLE_STATS,
    get_cardinality
)

def main():
    # 1. Load data
    data_path = os.path.join("data", "mock_data.json")
    load_mock_data(data_path)
    
    # 2. Init training data
    init_training_data()

    # 3. Build ML models
    build_initial_models()

    # 4. Create Optimizer
    opt = Optimizer()

    # 5. Read queries
    queries_file = os.path.join("data", "testqueries.sql")
    with open(queries_file, "r") as f:
        raw = f.read().strip()
    statements = [q.strip() for q in raw.split(";") if q.strip()]

    # 6. Process each query
    for idx, sql_str in enumerate(statements, start=1):
        print(f"\n=== Query #{idx}: {sql_str}")
        try:
            logical_plan = parse_query(sql_str)
        except Exception as e:
            print(f"Parse Error: {e}")
            continue

        # Optimize
        best_plan = opt.optimize(logical_plan)
        plan_cost = estimate_cost(best_plan)

        print("Chosen Plan:")
        visualize_plan(best_plan, 1)
        print(f"Predicted Cost: {plan_cost:.4f}")

        # Actual Execution
        actual_row_count = execute_plan(best_plan)
        print(f"Actual Row Count: {actual_row_count}")

        # If single-table filter, partial retraining
        # Or if you'd like to do multi-table partial training,
        # you'd need to measure sub-plan row counts. We keep it simple.
        do_feedback(best_plan, actual_row_count)

        print("----")


def do_feedback(plan, actual_rows):
    """
    Compare predicted row count vs actual for single-table filters 
    and call partial_retrain_if_needed if there's a big mismatch.
    """
    if isinstance(plan, LogicalSelect) and isinstance(plan.child, LogicalScan):
        # predicted row count
        tname = plan.child.table_name
        total_rows = TABLE_STATS[tname]["row_count"]
        predicted_rows = get_cardinality(plan)
        # actual fraction
        actual_fraction = actual_rows / total_rows if total_rows > 0 else 0.0

        # parse the predicate to get col_idx, val
        info = ML_MODELS.get(tname, None)
        if info and info["model"]:
            import re
            pat = re.compile(r"(?:[A-Z0-9_]+\.)?([A-Z0-9_]+)([<>=])(\d+)", re.IGNORECASE)
            m = pat.match(plan.predicate)
            if m and m.group(2) == "<":
                col_str = m.group(1).lower()
                val = float(m.group(3))
                numeric_cols = info["numeric_cols"]
                if col_str in numeric_cols:
                    col_idx = numeric_cols.index(col_str)
                    partial_retrain_if_needed(tname, col_idx, val, actual_fraction)

    elif isinstance(plan, LogicalJoin):
        # Optionally, you could measure sub-plan actual row counts if you want 
        # deeper feedback for multi-table. We keep it simple here.
        do_feedback(plan.left, actual_rows)
        do_feedback(plan.right, actual_rows)
    elif isinstance(plan, LogicalSelect):
        # There's a select on top of a join or another select
        do_feedback(plan.child, actual_rows)
    # If scan or unknown => no feedback


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted by user.")
        sys.exit(0)
