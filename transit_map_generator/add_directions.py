from typing import Dict, Any, List
import math
import json
import copy

def mod8(n: int) -> int:
    """Fix mod 8 for negative numbers close to 0."""
    return (n + 16) % 8

def ang(vector: Dict[str, float]) -> float:
    """Calculate angle. 9 o'clock = 0/8, 6 o'clock = 2, 3 o'clock = 4, 12 o'clock = 6."""
    return 4 * ((math.atan2(vector['y'], vector['x']) / math.pi) + 1)

def closest_number(target: float, numbers: List[int]) -> int:
    """Find the closest number to target from a list of numbers."""
    return min(numbers, key=lambda x: abs(x - target))

def closest_direction_ids(angle: float) -> List[int]:
    """Find closest direction ids (0-7, see `ang`) for a given angle."""
    closest_directions = []
    all_directions = list(range(-1, 10))  # -1, 0, 1, ..., 9

    for _ in range(3):  # find the 3 closest directions
        closest_direction = closest_number(angle, all_directions)
        closest_directions.append(mod8(closest_direction))
        all_directions.remove(closest_direction)

    return closest_directions

def add_directions(graph: Dict[str, Any]) -> Dict[str, Any]:
    """Add directions to the graph edges."""
    # Create a deep copy of the graph to avoid modifying the input
    graph = copy.deepcopy(graph)

    for edge in graph['edges']:
        # Find source and target nodes
        source = next(n['metadata'] for n in graph['nodes'] if n['id'] == edge['source'])
        target = next(n['metadata'] for n in graph['nodes'] if n['id'] == edge['target'])

        # Calculate vector and angle
        vector = {'x': target['x'] - source['x'], 'y': target['y'] - source['y']}
        angle = ang(vector)

        # Set source and target directions
        edge['sourceDirections'] = closest_direction_ids(angle)
        edge['targetDirections'] = [mod8(d + 4) for d in edge['sourceDirections']]
        print(edge)

    return graph 
