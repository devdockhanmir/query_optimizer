# optimizer/query_parser.py

import re

class LogicalScan:
    def __init__(self, table_name):
        self.table_name = table_name

    def __repr__(self):
        return f"LogicalScan({self.table_name})"

class LogicalSelect:
    def __init__(self, child, predicate=None):
        self.child = child
        self.predicate = predicate  # e.g. "R.col1<50"

    def __repr__(self):
        return f"LogicalSelect({self.child}, pred={self.predicate})"

class LogicalJoin:
    def __init__(self, left, right, join_condition=None):
        self.left = left
        self.right = right
        self.join_condition = join_condition  # e.g. "R.col1=S.colA"

    def __repr__(self):
        return f"LogicalJoin({self.left}, {self.right}, cond={self.join_condition})"

def parse_query(sql_str):
    """
    Very simple parser handling:
    - Single table: FROM R [WHERE col < val]
    - Two tables: FROM R, S [WHERE R.col1 = S.col2 [AND R.colX < val]]
    """
    sql_str = sql_str.strip().upper()

    # Find tables in FROM
    from_pat = re.compile(r"FROM\s+([A-Z0-9_]+)(?:\s*,\s*([A-Z0-9_]+))?")
    m = from_pat.search(sql_str)
    if not m:
        raise ValueError("Could not parse table references.")
    t1 = m.group(1)
    t2 = m.group(2)  # might be None

    # Build base plan
    if t2 is None:
        # single table
        base_plan = LogicalScan(t1)
    else:
        # two-table
        left_scan = LogicalScan(t1)
        right_scan = LogicalScan(t2)
        # Check for equi-join: R.col1 = S.colA
        join_match = re.search(r"WHERE\s+([A-Z0-9_.]+)\s*=\s*([A-Z0-9_.]+)", sql_str)
        cond_str = None
        if join_match:
            left_expr = join_match.group(1)
            right_expr = join_match.group(2)
            cond_str = f"{left_expr}={right_expr}"
        base_plan = LogicalJoin(left_scan, right_scan, join_condition=cond_str)

    # Check if there's a filter "AND R.col2 < val" or single "WHERE col < val"
    # We'll parse second filter portion: (AND|WHERE) col < val
    filter_match = re.search(r"(AND|WHERE)\s+([A-Z0-9_.]+)\s*([<>=])\s*(\d+)", sql_str)
    if filter_match:
        col_str = filter_match.group(2)
        op_str = filter_match.group(3)
        val_str = filter_match.group(4)
        predicate = f"{col_str}{op_str}{val_str}"
        return LogicalSelect(base_plan, predicate)

    return base_plan
