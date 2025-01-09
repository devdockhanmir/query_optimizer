from optimizer.query_parser import RelationalAlgebraTree, RelationalAlgebraNode

def predicate_pushdown(node):
    """
    Apply predicate pushdown transformation.
    Moves SELECT conditions closer to the relevant relation.
    """
    if node.operation == "SELECT" and len(node.children) == 1:
        child = node.children[0]
        
        if child.operation == "JOIN":
            # Extract the condition and check if it applies to one of the JOIN children
            condition = node.condition
            left_child, right_child = child.children
            
            # Check if the condition applies to the left child
            if "TotalDue" in condition:  # Adjust this to parse column references dynamically
                # Push the SELECT condition onto the left child
                new_select = RelationalAlgebraNode("SELECT", condition, [left_child])
                new_join = RelationalAlgebraNode("JOIN", child.condition, [new_select, right_child])
                return new_join

    # Recursively apply predicate pushdown on child nodes
    if node.children:
        node.children = [predicate_pushdown(child) for child in node.children]
    
    return node



def apply_transformation_rules(tree):
    """
    Apply all transformation rules to the relational algebra tree.
    """
    root = predicate_pushdown(tree.root)
    return RelationalAlgebraTree(root)
