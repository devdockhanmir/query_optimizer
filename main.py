from optimizer.query_parser import RelationalAlgebraNode, RelationalAlgebraTree
from optimizer.transformation import apply_transformation_rules

# Define the tree for a test query
sales_order_header = RelationalAlgebraNode("RELATION", "SalesOrderHeader")
customer = RelationalAlgebraNode("RELATION", "Customer")

join_node = RelationalAlgebraNode("JOIN", "CustomerID = CustomerID", [sales_order_header, customer])
select_node = RelationalAlgebraNode("SELECT", "TotalDue > 10000", [join_node])
project_node = RelationalAlgebraNode("PROJECT", "FirstName, LastName", [select_node])

# Create the relational algebra tree
tree = RelationalAlgebraTree(project_node)
print("Original Query Plan:")
tree.display()

# Apply transformations
optimized_tree = apply_transformation_rules(tree)
print("\nOptimized Query Plan:")
optimized_tree.display()
