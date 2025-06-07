from typing import Dict, Any, Union
import json
import subprocess
import tempfile
from pathlib import Path

def graph_to_svg(graph: Dict[str, Any], invert_y: bool = False) -> str:
    """Convert the graph to an SVG representation using svg-transit-map."""
    # Create a temporary file to store the graph JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
        json.dump(graph, tmp_file)
        tmp_path = tmp_file.name
    
    try:
        # Build the command
        cmd = ['svg-transit-map']
        if invert_y:
            cmd.append('--invert-y')
        
        # Run svg-transit-map
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Feed the graph JSON to stdin
        with open(tmp_path) as f:
            svg_output, stderr = process.communicate(f.read())
            
        if process.returncode != 0:
            raise RuntimeError(f"svg-transit-map failed: {stderr}")
        
        return svg_output
        
    finally:
        # Clean up temporary file
        Path(tmp_path).unlink() 
