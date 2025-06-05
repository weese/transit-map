from typing import Dict, Any, List, Union

def _stringify_properties(props: Dict[str, str]) -> str:
    """Convert properties dictionary to SVG attribute string."""
    return ' '.join(f'{k}="{v}"' for k, v in props.items())

def _stringify_children(children: List[Dict[str, Any]]) -> str:
    """Convert child elements to SVG string."""
    return ''.join(svg_to_string(child) for child in children)

def svg_to_string(vdom: Dict[str, Any]) -> str:
    """Convert virtual DOM representation to SVG string."""
    tag = vdom['tagName']
    props = _stringify_properties(vdom.get('properties', {}))
    children = _stringify_children(vdom.get('children', []))
    
    if children:
        return f'<{tag} {props}>{children}</{tag}>'
    else:
        return f'<{tag} {props}/>' 
