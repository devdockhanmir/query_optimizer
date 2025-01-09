import graphviz

def visualize_query_tree(tree, filename="query_tree"):
    """
    Visualize the query tree using Graphviz.
    :param tree: RelationalAlgebraTree
    :param filename: Output filename for the graph
    """
    dot = graphviz.Digraph()
    _add_nodes(dot, tree.root)
    dot.render(filename, format="png", cleanup=True)

def _add_nodes(dot, node, parent_id=None):
    node_id = id(node)
    dot.node(str(node_id), f"{node.operation}\n({node.condition})")
    if parent_id:
        dot.edge(str(parent_id), str(node_id))
    for child in node.children:
        _add_nodes(dot, child, node_id)
