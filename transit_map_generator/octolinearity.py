from typing import Dict, Any, List, Callable
from .util import node_index, edge_index

def create_set_product(settings: Dict[str, Any]) -> Callable[[str, str, str], List[str]]:
    """Create constraints to linearize the product of a continuous and a binary variable."""
    def set_product(product: str, continuous: str, binary: str) -> List[str]:
        upper_bound = settings['max_edge_length'] + 1
        return [
            f"{product} - {upper_bound} {binary} <= 0",
            f"{product} - {continuous} <= 0",
            f"{product} - {continuous} - {upper_bound} {binary} >= -{upper_bound}"
        ]
    return set_product

def create_octolinearity_constraints(settings: Dict[str, Any]) -> Callable[[Dict[str, Any], Dict[str, Any]], List[str]]:
    """Create constraints to maintain octolinear edge directions."""
    set_product = create_set_product(settings)
    
    def octolinearity_constraints(graph: Dict[str, Any], edge: Dict[str, Any]) -> List[str]:
        constraints = []
        e = edge_index(graph, edge)

        # Set helper variables for products
        constraints.extend(set_product(f"pa{e}", f"l{e}", f"a{e}"))
        constraints.extend(set_product(f"pb{e}", f"l{e}", f"b{e}"))
        constraints.extend(set_product(f"pc{e}", f"l{e}", f"c{e}"))
        constraints.extend(set_product(f"pd{e}", f"l{e}", f"d{e}"))

        # Add coordinate constraints
        constraints.extend([
            f"vx{node_index(graph, edge['target'])} - vx{node_index(graph, edge['source'])} - pa{e} + pb{e} = 0",
            f"vy{node_index(graph, edge['target'])} - vy{node_index(graph, edge['source'])} - pc{e} + pd{e} = 0"
        ])

        # Basic constraints that limit sum of direction variables
        constraints.extend([
            f"a{e} + b{e} <= 1",
            f"c{e} + d{e} <= 1"
        ])

        # Get main and secondary directions
        sourceDirections = edge.get('sourceDirections', [0, 0])
        main_direction = sourceDirections[0]
        secondary_direction = len(sourceDirections) > 1 and sourceDirections[1] or 0

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

        # TODO: remove this
        # adjacent_line_edges = []

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
                    # Check if both edges have sourceDirections and they are equal
                    edge_source_dirs = edge.get('sourceDirections', None)
                    a_edge_source_dirs = a_edge.get('sourceDirections', None)
                    if edge_source_dirs is not None and a_edge_source_dirs is not None and edge_source_dirs == a_edge_source_dirs:
                        a_e = edge_index(graph, a_edge)
                        constraints.extend([
                            f"a{e} - a{a_e} = 0",
                            f"b{e} - b{a_e} = 0",
                            f"c{e} - c{a_e} = 0",
                            f"d{e} - d{a_e} = 0"
                        ])
                else:
                    # Check if both edges have their respective directions and they are equal
                    edge_target_dirs = edge.get('targetDirections', None)
                    a_edge_source_dirs = a_edge.get('sourceDirections', None)
                    if edge_target_dirs is not None and a_edge_source_dirs is not None and edge_target_dirs == a_edge_source_dirs:
                        a_e = edge_index(graph, a_edge)
                        constraints.extend([
                            f"a{e} - b{a_e} = 0",
                            f"b{e} - a{a_e} = 0",
                            f"c{e} - d{a_e} = 0",
                            f"d{e} - c{a_e} = 0"
                        ])

        return constraints
    return octolinearity_constraints 
