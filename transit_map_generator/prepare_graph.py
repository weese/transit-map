from typing import Dict, Any, List

from .planarize import planarize
from .add_directions import add_directions

def prepare_graph(network_graph: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare the network graph by adding directions."""
    # Ensure each node has metadata
    for node in network_graph['nodes']:
        if 'metadata' not in node:
            node['metadata'] = {}
    
    # Ensure each edge has metadata and lines
    for edge in network_graph['edges']:
        if 'metadata' not in edge:
            edge['metadata'] = {}
        if 'lines' not in edge['metadata']:
            edge['metadata']['lines'] = []
        
        # Convert line objects to line IDs
        if isinstance(edge['metadata']['lines'], list):
            edge['metadata']['lines'] = [
                line['id'] if isinstance(line, dict) else line
                for line in edge['metadata']['lines']
            ]
    
    # Add directions to the graph edges
    network_graph = add_directions(network_graph)
    
    return network_graph 
