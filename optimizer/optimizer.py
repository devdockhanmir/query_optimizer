# optimizer/optimizer.py

from .transformation import get_logical_transformations
from .cost_model import estimate_cost

class Optimizer:
    """
    Explores transformations, enumerates plan variants,
    picks the cheapest plan based on cost.
    """

    def optimize(self, logical_expr):
        candidates = self.explore(logical_expr)
        best_expr = None
        best_cost = float("inf")

        for expr in candidates:
            c = estimate_cost(expr)
            if c < best_cost:
                best_cost = c
                best_expr = expr
        
        return best_expr

    def explore(self, expr):
        """
        BFS/DFS approach: generate transformations repeatedly until no new ones.
        """
        result = set()
        queue = [expr]

        while queue:
            current = queue.pop()
            if current not in result:
                result.add(current)
                trans = get_logical_transformations(current)
                for t in trans:
                    if t not in result:
                        queue.append(t)

        return list(result)
