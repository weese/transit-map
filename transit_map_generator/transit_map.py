import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess

from .prepare_graph import prepare_graph
from .generate_lp import create_generate_lp
from .revise_solution import create_revise_solution

# solver settings
SETTINGS = {
    'offset': 10000,
    'max_width': 300,
    'max_height': 300,
    'min_edge_length': 1,
    'max_edge_length': 8
}

# script default options
DEFAULTS = {
    'work_dir': None,
    'verbose': False
}

class Solver:
    def __init__(self, network_graph: Dict[str, Any]):
        self.graph = prepare_graph(network_graph)
        self.generate_lp = create_generate_lp(self.graph, SETTINGS)
        self.revise_solution = create_revise_solution(self.graph, SETTINGS)

def run_scip(cwd: str, verbose: bool = False) -> None:
    """Run SCIP solver on the problem file and generate solution."""
    problem_path = os.path.join(cwd, 'problem.lp')
    solution_path = os.path.join(cwd, 'solution.sol')
    
    cmd = [
        'scip',
        '-c', f'read {problem_path}',
        '-c', 'optimize',
        '-c', f'write solution {solution_path}',
        '-c', 'quit'
    ]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE if not verbose else None,
            stderr=subprocess.PIPE,
            text=True
        )
        _, stderr = process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"SCIP solver failed: {stderr}")
            
    except FileNotFoundError:
        raise RuntimeError("Make sure 'scip' is in your PATH")

def transit_map(network_graph: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate a transit map layout from a network graph."""
    # Merge options with defaults
    options = {**DEFAULTS, **(options or {})}
    
    # Create temporary directory if not provided
    if not options['work_dir']:
        options['work_dir'] = tempfile.mkdtemp(prefix='transit-map-')
    
    solver = Solver(network_graph)
    
    # Write problem file
    problem_path = Path(options['work_dir']) / 'problem.lp'
    with open(problem_path, 'w') as lp_stream:
        solver.generate_lp(lp_stream)
    
    # Run solver
    run_scip(options['work_dir'], options['verbose'])
    
    # Read solution file
    solution_path = Path(options['work_dir']) / 'solution.sol'
    with open(solution_path, 'r') as sol_stream:
        solution = solver.revise_solution(sol_stream)
    
    return solution 
