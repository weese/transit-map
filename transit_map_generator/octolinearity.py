from typing import Dict, Any, List, Callable
from .util import node_index, edge_index

def create_octolinearity_constraints(settings: Dict[str, Any]) -> Callable[[Dict[str, Any], Dict[str, Any]], List[str]]:
    """Create constraints to maintain octolinear edge directions."""
    def octolinearity_constraints(graph: Dict[str, Any], edge: Dict[str, Any]) -> List[str]:
        constraints = []
        e = edge_index(graph, edge)

        # Get main and secondary directions
        main_direction = edge.get('mainDirection', 0)
        secondary_direction = edge.get('secondaryDirection')

        # Add constraints based on direction
        if main_direction == 0:  # 9 o'clock
            constraints.extend([
                f"a{e} = 0",
                f"b{e} = 1"
            ])
            if secondary_direction == 7:
                constraints.append(f"d{e} = 0")
            if secondary_direction == 1:
                constraints.append(f"c{e} = 0")

        elif main_direction == 1:  # 7.5 o'clock
            constraints.extend([
                f"a{e} = 0",
                f"c{e} = 0"
            ])
            if secondary_direction == 2:
                constraints.append(f"d{e} = 1")
            if secondary_direction == 0:
                constraints.append(f"b{e} = 1")

        elif main_direction == 2:  # 6 o'clock
            constraints.extend([
                f"c{e} = 0",
                f"d{e} = 1"
            ])
            if secondary_direction == 3:
                constraints.append(f"b{e} = 0")
            if secondary_direction == 1:
                constraints.append(f"a{e} = 0")

        elif main_direction == 3:  # 4.5 o'clock
            constraints.extend([
                f"b{e} = 0",
                f"c{e} = 0"
            ])
            if secondary_direction == 4:
                constraints.append(f"a{e} = 1")
            if secondary_direction == 2:
                constraints.append(f"d{e} = 1")

        elif main_direction == 4:  # 3 o'clock
            constraints.extend([
                f"a{e} = 1",
                f"b{e} = 0"
            ])
            if secondary_direction == 5:
                constraints.append(f"d{e} = 0")
            if secondary_direction == 3:
                constraints.append(f"c{e} = 0")

        elif main_direction == 5:  # 1.5 o'clock
            constraints.extend([
                f"b{e} = 0",
                f"d{e} = 0"
            ])
            if secondary_direction == 6:
                constraints.append(f"c{e} = 1")
            if secondary_direction == 4:
                constraints.append(f"a{e} = 1")

        elif main_direction == 6:  # 12 o'clock
            constraints.extend([
                f"c{e} = 1",
                f"d{e} = 0"
            ])
            if secondary_direction == 7:
                constraints.append(f"a{e} = 0")
            if secondary_direction == 5:
                constraints.append(f"b{e} = 0")

        elif main_direction == 7:  # 10.5 o'clock
            constraints.extend([
                f"a{e} = 0",
                f"d{e} = 0"
            ])
            if secondary_direction == 0:
                constraints.append(f"b{e} = 1")
            if secondary_direction == 6:
                constraints.append(f"c{e} = 1")

        else:
            raise ValueError('Unknown direction')

        # Force angle to 180° for some pairs of adjacent edges
        adjacent_line_edges = [e for e in graph['edges'] if 
            bool(set(e['metadata']['lines']) & set(edge['metadata']['lines'])) and 
            len(set([e['source'], e['target']]) & set([edge['source'], edge['target']])) == 1]

        for a_edge in adjacent_line_edges:
            degrees = [
                len([e for e in graph['edges'] if node in [e['source'], e['target']]])
                for node in [edge['source'], edge['target'], a_edge['source'], a_edge['target']]
            ]
            middle_node_id = list(set([edge['source'], edge['target']]) & 
                                set([a_edge['source'], a_edge['target']]))[0]
            middle = next(n for n in graph['nodes'] if n['id'] == middle_node_id)
            
            if all(d == 2 for d in degrees) or middle.get('dummy', False):
                if edge['target'] == a_edge['source'] or edge['source'] == a_edge['target']:
                    if edge.get('sourceDirections', []) == a_edge.get('sourceDirections', []):
                        a_e = edge_index(graph, a_edge)
                        constraints.extend([
                            f"a{e} - a{a_e} = 0",
                            f"b{e} - b{a_e} = 0",
                            f"c{e} - c{a_e} = 0",
                            f"d{e} - d{a_e} = 0"
                        ])
                else:
                    if edge.get('targetDirections', []) == a_edge.get('sourceDirections', []):
                        a_e = edge_index(graph, a_edge)
                        constraints.extend([
                            f"a{e} - b{a_e} = 0",
                            f"b{e} - a{a_e} = 0",
                            f"c{e} - d{a_e} = 0",
                            f"d{e} - c{a_e} = 0"
                        ])

        return constraints
    return octolinearity_constraints 
