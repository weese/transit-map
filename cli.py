#!/usr/bin/env python3

import sys
import json
import argparse
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any
import io

from transit_map_generator.transit_map import transit_map, Solver
from transit_map_generator.svg_transit_map import graph_to_svg
from transit_map_generator.virtual_dom_stringify import svg_to_string

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate a metro network layout via MILP')
    parser.add_argument('--tmp-dir', '-t', 
                       help='Directory to store intermediate files. Default: unique tmp dir.')
    parser.add_argument('--output-file', '-o',
                       help='File to store result (instead of stdout).')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable solver logging to stderr.')
    parser.add_argument('--graph', '-g', action='store_true',
                       help='Return JSON graph instead of SVG map.')
    parser.add_argument('--invert-y', '-y', action='store_true',
                       help='Invert the Y axis in SVG result.')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Output the generated LP and stop.')
    parser.add_argument('--version', '-V', action='version',
                       version='%(prog)s 1.0.0')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Read from stdin
    try:
        stdin_data = sys.stdin.read()
        if not stdin_data:
            raise ValueError('No input network found in stdin.')
        graph = json.loads(stdin_data)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        sys.exit(1)

    config = {
        'work_dir': args.tmp_dir,
        'verbose': args.verbose,
    }

    if args.debug:
        # Generate and output LP only
        solver = Solver(graph)
        output = io.StringIO()
        solver.generate_lp(output)
        lp = output.getvalue()
        if args.output_file:
            Path(args.output_file).write_text(lp)
        else:
            print(lp)
        sys.exit(0)

    # Generate solution
    solution = transit_map(graph, config)

    # Generate output
    if args.graph:
        result = json.dumps(graph)
    else:
        result = graph_to_svg(solution, args.invert_y)

    # Output result
    if args.output_file:
        Path(args.output_file).write_text(result)
    else:
        print(result)

if __name__ == '__main__':
    main() 
