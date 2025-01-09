from optimizer.cost_model import estimate_cost

def optimize_query(tree):
    """
    Optimize the relational algebra tree using cost-based optimization.
    """
    root = tree.root
    cost = estimate_cost(root)
    print(f"Estimated cost: {cost}")
    return tree
