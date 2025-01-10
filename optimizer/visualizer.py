# optimizer/visualizer.py

from .query_parser import LogicalScan, LogicalSelect, LogicalJoin

def visualize_plan(plan, indent=0):
    prefix = "  " * indent
    if isinstance(plan, LogicalScan):
        print(f"{prefix}Scan({plan.table_name})")
    elif isinstance(plan, LogicalSelect):
        print(f"{prefix}Select [pred={plan.predicate}]")
        visualize_plan(plan.child, indent + 1)
    elif isinstance(plan, LogicalJoin):
        print(f"{prefix}Join [cond={plan.join_condition}]")
        print(f"{prefix}Left ->")
        visualize_plan(plan.left, indent + 2)
        print(f"{prefix}Right ->")
        visualize_plan(plan.right, indent + 2)
    else:
        print(f"{prefix}Unknown Node: {plan}")
