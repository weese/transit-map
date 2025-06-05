from typing import Dict, Any, List, TextIO, Union

def node_index(graph: Dict[str, Any], node_id: str) -> int:
    """Get the index of a node in the graph."""
    for i, node in enumerate(graph['nodes']):
        if node['id'] == node_id:
            return i
    raise ValueError(f"Node {node_id} not found in graph")

def edge_index(graph: Dict[str, Any], edge: Dict[str, Any]) -> int:
    """Get the index of an edge in the graph."""
    for i, e in enumerate(graph['edges']):
        if (e['source'] == edge['source'] and 
            e['target'] == edge['target'] and 
            e['metadata']['lines'] == edge['metadata']['lines']):
            return i
    raise ValueError("Edge not found in graph") 
