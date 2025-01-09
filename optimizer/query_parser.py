class RelationalAlgebraNode:
    def __init__(self, operation, condition=None, children=None):
        self.operation = operation
        self.condition = condition
        self.children = children if children else []

    def __repr__(self):
        return f"RelationalAlgebraNode(operation={self.operation}, condition={self.condition}, children={len(self.children)})"


class RelationalAlgebraTree:
    def __init__(self, root):
        self.root = root

    def display(self, node=None, depth=0):
        if node is None:
            node = self.root
        print("  " * depth + f"{node.operation} ({node.condition})")
        for child in node.children:
            self.display(child, depth + 1)
