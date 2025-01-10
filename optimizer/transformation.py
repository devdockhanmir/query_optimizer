# optimizer/transformation.py

from .query_parser import LogicalJoin, LogicalScan, LogicalSelect

def apply_join_commutativity(expr):
    """
    If expr is LogicalJoin(R,S), produce LogicalJoin(S,R).
    Preserve the same join_condition if possible, 
    but we might have to flip references from R.col to S.col, etc. 
    We'll keep it simple: just swap the child nodes, keep cond the same.
    """
    if not isinstance(expr, LogicalJoin):
        return []
    # swap children
    swapped = LogicalJoin(expr.right, expr.left, expr.join_condition)
    return [swapped]

def get_logical_transformations(expr):
    """Collect all transformations for an expression (and sub-expressions)."""
    new_exprs = []

    if isinstance(expr, LogicalSelect):
        # transformations on the child
        child_transforms = get_logical_transformations(expr.child)
        new_exprs.extend(
            [LogicalSelect(ct, expr.predicate) for ct in child_transforms]
        )
        # no direct rule for select yet
    elif isinstance(expr, LogicalJoin):
        # commutativity
        new_exprs.extend(apply_join_commutativity(expr))

        # transformations on sub-children
        left_trans = get_logical_transformations(expr.left)
        right_trans = get_logical_transformations(expr.right)

        # gather new combos
        for lt in left_trans:
            new_exprs.append(LogicalJoin(lt, expr.right, expr.join_condition))
        for rt in right_trans:
            new_exprs.append(LogicalJoin(expr.left, rt, expr.join_condition))

    # each sub-expression might recursively produce new transformations
    return new_exprs
