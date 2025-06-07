from typing import Dict, Any, TextIO, Callable
import json

def create_revise_solution(graph: Dict[str, Any], settings: Dict[str, Any]) -> Callable[[TextIO], Dict[str, Any]]:
    """Create a function to revise the SCIP solution."""
    def revise_solution(solution_stream: TextIO) -> Dict[str, Any]:
        # Create a deep copy of the input graph to avoid modifying the original
        graph_copy = json.loads(json.dumps(graph))
        
        # Parse the SCIP solution file
        solution = {}
        for line in solution_stream:
            # Skip objective value line
            if line.startswith('objective value:') or line.startswith('solution status:'):
                continue
            
            # Parse variable and value
            parts = line.strip().split()
            if len(parts) >= 2:
                variable, value = parts[:2]
                solution[variable] = float(value)
        
        # Update node coordinates
        for i, node in enumerate(graph_copy['nodes']):
            # Get the new coordinates from the solution
            # Subtract the offset to get back to the original coordinate space
            node['metadata']['x'] = round(solution[f'vx{i}'] - settings['offset'], 5)
            node['metadata']['y'] = round(solution[f'vy{i}'] - settings['offset'], 5)
        
        return graph_copy
    
    return revise_solution 
