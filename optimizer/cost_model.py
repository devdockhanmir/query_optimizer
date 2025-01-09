def estimate_cost(node):
    """
    Estimate the cost of a query operation.
    :param node: RelationalAlgebraNode
    :return: Estimated cost (integer)
    """
    if node.operation == "RELATION":
        return 1000  # Example: Number of rows in the table
    elif node.operation == "SELECT":
        return estimate_cost(node.children[0]) // 10  # Example: Filter reduces rows by 90%
    elif node.operation == "JOIN":
        left_cost = estimate_cost(node.children[0])
        right_cost = estimate_cost(node.children[1])
        return left_cost * right_cost  # Cartesian product cost
    elif node.operation == "PROJECT":
        return estimate_cost(node.children[0])  # Projection doesn't change row count
    return 0
