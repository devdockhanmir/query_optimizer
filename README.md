# Query Optimizer

A relational query optimizer inspired by the **Volcano/Cascades framework**. This project represents SQL queries as relational algebra trees and applies transformation rules to optimize query execution. The optimizer is designed to showcase concepts such as predicate pushdown, join reordering, and cost-based optimization.

---

## Features

- **Relational Algebra Tree Representation**: Queries are represented as hierarchical trees with operations like `SELECT`, `JOIN`, and `PROJECT`.
- **Predicate Pushdown**: Moves filtering conditions (`WHERE` clauses) closer to the data source to reduce intermediate result sizes.
- **Cost Estimation**: A simple cost model to estimate the efficiency of query execution plans.
- **Modular Design**: Each component (query parsing, transformation, cost modeling, etc.) is implemented in a separate module for clarity and extensibility.
- **Tree Visualization**: Generates visual representations of query plans using Graphviz.

---

## Project Structure

```
query_optimizer/
├── main.py                # Entry point
├── optimizer/
│   ├── __init__.py
│   ├── query_parser.py    # Defines relational algebra tree
│   ├── transformation.py  # Implements transformation rules
│   ├── cost_model.py      # Estimates query execution costs
│   ├── optimizer.py       # Implements the optimization logic
│   ├── visualizer.py      # Visualizes query plans
├── data/
│   ├── test_queries.sql   # Example SQL queries
│   ├── mock_data.json     # Mock data for testing
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── .gitignore             # Files to exclude from Git
```

---

## Installation

### Prerequisites
- Python 3.8 or higher
- `pip` package manager

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/query_optimizer.git
   cd query_optimizer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # For macOS/Linux
   env\Scripts\activate    # For Windows
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Run the Optimizer
1. Navigate to the project directory:
   ```bash
   cd query_optimizer
   ```

2. Run the `main.py` script:
   ```bash
   python main.py
   ```

3. The script will display the original and optimized query plans in the terminal.

### Example Output
**Original Query Plan:**
```
PROJECT (FirstName, LastName)
  SELECT (TotalDue > 10000)
    JOIN (CustomerID = CustomerID)
      RELATION (SalesOrderHeader)
      RELATION (Customer)
```

**Optimized Query Plan:**
```
PROJECT (FirstName, LastName)
  JOIN (CustomerID = CustomerID)
    SELECT (TotalDue > 10000)
      RELATION (SalesOrderHeader)
    RELATION (Customer)
```

### Visualize Query Plans
To generate a graphical representation of the query plan:
```python
from optimizer.visualizer import visualize_query_tree

# Visualize the optimized query tree
visualize_query_tree(optimized_tree, filename="optimized_query_plan")
```
This will generate `optimized_query_plan.png` in the project directory.

---

## Key Components

### 1. Relational Algebra Tree
- Represents SQL queries as trees with operations as nodes.
- Defined in `query_parser.py`.

### 2. Transformation Rules
- Implements optimization techniques like predicate pushdown.
- Defined in `transformation.py`.

### 3. Cost Model
- Estimates the cost of different query execution plans.
- Defined in `cost_model.py`.

### 4. Optimizer
- Applies transformations and selects the most efficient query plan.
- Defined in `optimizer.py`.

### 5. Visualizer
- Generates graphical representations of query plans.
- Uses Graphviz, defined in `visualizer.py`.

---

## Examples

### Query 1: High-Spending Customers
**SQL:**
```sql
SELECT FirstName, LastName, SUM(TotalDue) AS TotalSpent
FROM SalesOrderHeader
JOIN Customer ON SalesOrderHeader.CustomerID = Customer.CustomerID
WHERE TotalDue > 10000;
```
**Optimized Plan:**
```
PROJECT (FirstName, LastName)
  JOIN (CustomerID = CustomerID)
    SELECT (TotalDue > 10000)
      RELATION (SalesOrderHeader)
    RELATION (Customer)
```

---

## Future Enhancements
- Implement additional transformation rules (e.g., join reordering, projection pushdown).
- Expand the cost model for more realistic query plan evaluation.
- Support more complex queries with subqueries and aggregates.

---

## Contributing
1. Fork the repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature name"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## License
This project is licensed under the MIT License. See `LICENSE` for details.

