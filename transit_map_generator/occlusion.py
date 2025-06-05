from typing import Dict, Any, List, Callable
from .util import node_index, edge_index

def create_occlusion_constraints(settings: Dict[str, Any]) -> Callable[[Dict[str, Any], Dict[str, Any], Dict[str, Any]], List[str]]:
    """Create constraints to prevent edge occlusion."""
    def occlusion_constraints(graph: Dict[str, Any], edge1: Dict[str, Any], edge2: Dict[str, Any]) -> List[str]:
        # Get source and target indices for both edges
        e1s_index = node_index(graph, edge1['source'])
        e1t_index = node_index(graph, edge1['target'])
        e2s_index = node_index(graph, edge2['source'])
        e2t_index = node_index(graph, edge2['target'])

        # Get source and target metadata for both edges
        e1s = graph['nodes'][e1s_index]['metadata']
        e1t = graph['nodes'][e1t_index]['metadata']
        e2s = graph['nodes'][e2s_index]['metadata']
        e2t = graph['nodes'][e2t_index]['metadata']

        # Check if edges are only separated by one other edge
        combinations = [
            sorted([edge1['source'], edge2['source']]),
            sorted([edge1['source'], edge2['target']]),
            sorted([edge1['target'], edge2['source']]),
            sorted([edge1['target'], edge2['target']])
        ]
        combinations = ['-'.join(c) for c in combinations]
        edges_are_close = any(
            '-'.join(sorted([e['source'], e['target']])) in combinations
            for e in graph['edges']
        )

        # Calculate distances in all 4 directions for both edges in the input graph
        direction_distances = {
            'west-east': [
                e1s['x'] - e2s['x'],
                e1s['x'] - e2t['x'],
                e1t['x'] - e2s['x'],
                e1t['x'] - e2t['x']
            ],
            'south-north': [
                e1s['y'] - e2s['y'],
                e1s['y'] - e2t['y'],
                e1t['y'] - e2s['y'],
                e1t['y'] - e2t['y']
            ],
            'southwest-northeast': [
                (e1s['x'] - e1s['y']) - (e2s['x'] - e2s['y']),
                (e1s['x'] - e1s['y']) - (e2t['x'] - e2t['y']),
                (e1t['x'] - e1t['y']) - (e2s['x'] - e2s['y']),
                (e1t['x'] - e1t['y']) - (e2t['x'] - e2t['y'])
            ],
            'northwest-southeast': [
                (e1s['x'] + e1s['y']) - (e2s['x'] + e2s['y']),
                (e1s['x'] + e1s['y']) - (e2t['x'] + e2t['y']),
                (e1t['x'] + e1t['y']) - (e2s['x'] + e2s['y']),
                (e1t['x'] + e1t['y']) - (e2t['x'] + e2t['y'])
            ]
        }

        # Compare distances, check ordering of points in given direction
        direction_facts = {}
        for direction, distances in direction_distances.items():
            direction_facts[direction] = {
                'positive': sum(1 for x in distances if x > 0),
                'closest_if_separate': min(abs(n) for n in distances)
            }

        # Find preferred direction with longest distance
        best_directions = [
            d for d in direction_distances.keys()
            if direction_facts[d]['positive'] in (0, 4)
        ]
        if best_directions:
            preferred_direction = max(
                best_directions,
                key=lambda d: direction_facts[d]['closest_if_separate']
            )
        else:
            # No suitable direction found
            return []

        constraints = []

        # Set minimum distance for both edges in the given direction
        min_dist = 1
        end_string = (">= " if direction_facts[preferred_direction]['positive'] >= 3 else "<= -") + str(min_dist)

        # Add constraints based on preferred direction
        if preferred_direction == 'west-east':
            constraints.extend([
                f"vx{e1s_index} - vx{e2s_index} {end_string}",
                f"vx{e1s_index} - vx{e2t_index} {end_string}",
                f"vx{e1t_index} - vx{e2s_index} {end_string}",
                f"vx{e1t_index} - vx{e2t_index} {end_string}"
            ])
        elif preferred_direction == 'south-north':
            constraints.extend([
                f"vy{e1s_index} - vy{e2s_index} {end_string}",
                f"vy{e1s_index} - vy{e2t_index} {end_string}",
                f"vy{e1t_index} - vy{e2s_index} {end_string}",
                f"vy{e1t_index} - vy{e2t_index} {end_string}"
            ])
        elif preferred_direction == 'southwest-northeast':
            constraints.extend([
                f"vx{e1s_index} - vy{e1s_index} - vx{e2s_index} + vy{e2s_index} {end_string}",
                f"vx{e1s_index} - vy{e1s_index} - vx{e2t_index} + vy{e2t_index} {end_string}",
                f"vx{e1t_index} - vy{e1t_index} - vx{e2s_index} + vy{e2s_index} {end_string}",
                f"vx{e1t_index} - vy{e1t_index} - vx{e2t_index} + vy{e2t_index} {end_string}"
            ])
        elif preferred_direction == 'northwest-southeast':
            constraints.extend([
                f"vx{e1s_index} + vy{e1s_index} - vx{e2s_index} - vy{e2s_index} {end_string}",
                f"vx{e1s_index} + vy{e1s_index} - vx{e2t_index} - vy{e2t_index} {end_string}",
                f"vx{e1t_index} + vy{e1t_index} - vx{e2s_index} - vy{e2s_index} {end_string}",
                f"vx{e1t_index} + vy{e1t_index} - vx{e2t_index} - vy{e2t_index} {end_string}"
            ])

        return constraints
    return occlusion_constraints 
