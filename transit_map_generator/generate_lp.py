from typing import Dict, Any, List, TextIO, Callable
from dataclasses import dataclass
import io

from .util import node_index, edge_index
from .occlusion import create_occlusion_constraints
from .octolinearity import create_octolinearity_constraints

def create_not_equal(settings: Dict[str, Any]) -> Callable[[str, str, str], List[str]]:
    """Create constraints to ensure left != right using a boolean variable."""
    def not_equal(left: str, negative_right: str, boolean: str) -> List[str]:
        upper_bound = settings['max_edge_length'] + 1
        return [
            f"{left} {negative_right} - {upper_bound} {boolean} <= -0.5",
            f"{left} {negative_right} - {upper_bound} {boolean} >= {0.5 - upper_bound}"
        ]
    return not_equal

@dataclass
class Variables:
    """Container for LP variables."""
    continuous: Dict[str, List[str]]
    integer: Dict[str, List[str]]
    binary: Dict[str, List[str]]
    coefficients: Dict[str, List[float]]

def create_generate_lp(graph: Dict[str, Any], settings: Dict[str, Any]) -> Callable[[TextIO], None]:
    """Create a function that generates the LP problem for the given graph."""
    
    def generate_lp(output_stream: TextIO) -> None:
        # Initialize constraints
        constraints: List[str] = []
        lazy_constraints: List[str] = []
        
        # Create constraint generators
        occlusion_constraints = create_occlusion_constraints(settings)
        octolinearity_constraints = create_octolinearity_constraints(settings)
        not_equal = create_not_equal(settings)
        
        # Initialize variables
        variables = Variables(
            continuous={
                'vx': [f"vx{node_index(graph, n['id'])}" for n in graph['nodes']],
                'vy': [f"vy{node_index(graph, n['id'])}" for n in graph['nodes']],
                'l': [f"l{i}" for i in range(len(graph['edges']))],
                'pa': [f"pa{i}" for i in range(len(graph['edges']))],
                'pb': [f"pb{i}" for i in range(len(graph['edges']))],
                'pc': [f"pc{i}" for i in range(len(graph['edges']))],
                'pd': [f"pd{i}" for i in range(len(graph['edges']))]
            },
            integer={'q': []},
            binary={
                'a': [f"a{i}" for i in range(len(graph['edges']))],
                'b': [f"b{i}" for i in range(len(graph['edges']))],
                'c': [f"c{i}" for i in range(len(graph['edges']))],
                'd': [f"d{i}" for i in range(len(graph['edges']))],
                'h': [], 'oa': [], 'ob': [], 'oc': [], 'od': [],
                'ua': [], 'ub': [], 'uc': [], 'ud': []
            },
            coefficients={'q': []}
        )
        
        # Generate octolinearity constraints
        for i, edge in enumerate(graph['edges']):
            constraints.extend(octolinearity_constraints(graph, edge))
        
        # Generate edge occlusion constraints
        num_adjacent_edge_constraints = 0
        edges = graph['edges']
        for o in range(len(edges)):
            for i in range(o + 1, len(edges)):
                outer = edges[o]
                inner = edges[i]
                
                # Check if edges are adjacent
                outer_nodes = {outer['source'], outer['target']}
                inner_nodes = {inner['source'], inner['target']}
                if len(outer_nodes & inner_nodes) > 0:  # intersection
                    # Handle adjacent edges
                    suffix = str(num_adjacent_edge_constraints)
                    
                    # Add variables
                    for var_type in ['h', 'oa', 'ob', 'oc', 'od', 'ua', 'ub', 'uc', 'ud']:
                        variables.binary[var_type].append(f"{var_type}{suffix}")
                    variables.integer['q'].append(f"q{suffix}")
                    
                    # Set coefficients for same/different lines
                    outer_lines = set(outer['metadata']['lines'])
                    inner_lines = set(inner['metadata']['lines'])
                    share_lines = bool(outer_lines & inner_lines)
                    variables.coefficients['q'].append(1.0 if share_lines else 0.25)
                    
                    # For edges sharing lines, limit angle to >= 90°
                    if share_lines:
                        constraints.append(f"q{suffix} <= 2")
                    
                    # Add constraints
                    constraints.append(
                        f"q{suffix} - oa{suffix} - ob{suffix} - oc{suffix} - od{suffix} = 0"
                    )
                    
                    # Handle edge direction constraints
                    if outer['target'] == inner['source'] or outer['source'] == inner['target']:
                        lazy_constraints.extend(
                            not_equal(
                                f"3 a{o} - 3 b{o} + c{o} - d{o}",
                                f"+ 3 a{i} - 3 b{i} + c{i} - d{i}",
                                f"h{suffix}"
                            )
                        )
                        # Add direction-specific constraints
                        for dir_var in ['a', 'b', 'c', 'd']:
                            constraints.append(
                                f"{dir_var}{o} + {dir_var}{i} - 2 u{dir_var}{suffix} - "
                                f"o{dir_var}{suffix} = 0"
                            )
                    else:
                        lazy_constraints.extend(
                            not_equal(
                                f"3 a{o} - 3 b{o} + c{o} - d{o}",
                                f"- 3 a{i} + 3 b{i} - c{i} + d{i}",
                                f"h{suffix}"
                            )
                        )
                        # Add opposite direction constraints
                        constraints.extend([
                            f"a{o} + b{i} - 2 ua{suffix} - oa{suffix} = 0",
                            f"b{o} + a{i} - 2 ub{suffix} - ob{suffix} = 0",
                            f"c{o} + d{i} - 2 uc{suffix} - oc{suffix} = 0",
                            f"d{o} + c{i} - 2 ud{suffix} - od{suffix} = 0"
                        ])
                    
                    num_adjacent_edge_constraints += 1
                else:
                    # Handle non-adjacent edges
                    constraints.extend(occlusion_constraints(graph, outer, inner))
        
        # Write LP file
        def write(text: str) -> None:
            output_stream.write(text + '\n')
            
        def write_tab(text: str) -> None:
            output_stream.write(' ' + text + '\n')
            
        # 1. Objective function
        write('Minimize')
        
        # Linearized sum of edge lengths
        lengths = ' + '.join(f"3 {l}" for l in variables.continuous['l'])
        
        # Sum of angle differences
        angles = ' + '.join(
            f"{4 * coef} {q}"
            for q, coef in zip(variables.integer['q'], variables.coefficients['q'])
        )
        
        # Write objective function
        write_tab(f"{angles} + {lengths}")
        
        # 2. Constraints
        write('Subject To')
        # Fix one coordinate pair
        write_tab(f"vx0 = {settings['offset']}")
        write_tab(f"vy0 = {settings['offset']}")
        
        # Write all constraints
        for c in constraints + lazy_constraints:
            write_tab(c)
            
        # 3. Bounds
        write('Bounds')
        # Edge length variables
        for l in variables.continuous['l']:
            write_tab(f"{settings['min_edge_length']} <= {l} <= {settings['max_edge_length']}")
            
        # Node coordinates
        for vx in variables.continuous['vx']:
            write_tab(
                f"{settings['offset'] - settings['max_width']/2} <= {vx} <= "
                f"{settings['offset'] + settings['max_width']/2}"
            )
        for vy in variables.continuous['vy']:
            write_tab(
                f"{settings['offset'] - settings['max_height']/2} <= {vy} <= "
                f"{settings['offset'] + settings['max_height']/2}"
            )
            
        # Helper variables
        for var_type in ['pa', 'pb', 'pc', 'pd']:
            for var in variables.continuous[var_type]:
                write_tab(f"0 <= {var}")
                
        # Edge angle variables
        for q in variables.integer['q']:
            write_tab(f"0 <= {q} <= 3")
            
        # 4. Integer variables
        write('General')
        for q in variables.integer['q']:
            write_tab(q)
            
        # 5. Binary variables
        write('Binary')
        for var_type, vars_list in variables.binary.items():
            for var in vars_list:
                write_tab(var)

        # 6. End
        write('End')

    return generate_lp 
