# Transit Map Generator

A Python tool to generate metro-style transit maps using Mixed Integer Linear Programming (MILP).

## Requirements

- Python 3.7+
- SCIP solver (must be available in your PATH)
- Required Python packages (install via `pip install -r requirements.txt`):
  - typing-extensions
  - pathlib
  - svgwrite
  - json5

## Installation

1. Make sure you have Python 3.7 or higher installed
2. Install SCIP solver:
   - macOS: `brew install scip`
   - Linux: `apt-get install scip` or equivalent for your distribution
   - Windows: Download from [SCIP website](https://www.scipopt.org/index.php#download)
3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Install svg-transit-map:

   ```bash
   npm install -g svg-transit-map
   ```

## Usage

The tool reads a network graph in JSON format from stdin and outputs either a JSON graph or SVG map:

```bash
cat converted-network.json | python cli.py > output.svg
```

### Command Line Options

- `--tmp-dir`, `-t`: Directory to store intermediate files (default: unique tmp dir)
- `--output-file`, `-o`: File to store result (instead of stdout)
- `--silent`, `-s`: Disable solver logging to stderr
- `--graph`, `-g`: Return JSON graph instead of SVG map
- `--invert-y`, `-y`: Invert the Y axis in SVG result
- `--help`, `-h`: Show help message
- `--version`, `-v`: Show version number

### Input Format

The input JSON should describe a network graph with nodes and edges:

```json
{
  "nodes": [
    {
      "id": "station1",
      "metadata": {
        "name": "Station 1"
      }
    }
  ],
  "edges": [
    {
      "source": "station1",
      "target": "station2",
      "metadata": {
        "lines": ["line1", "line2"]
      }
    }
  ]
}
```

### Output

By default, the tool outputs an SVG representation of the transit map. Use the `--graph` flag to get the computed graph layout in JSON format instead.

## How It Works

1. The tool takes a network graph as input
2. Generates a Mixed Integer Linear Programming (MILP) problem
3. Uses SCIP to solve the optimization problem
4. Converts the solution into either a JSON graph or SVG map

The optimization aims to:
- Maintain octolinear edge directions (multiples of 45°)
- Minimize edge lengths
- Avoid edge crossings
- Preserve relative positions of stations

## License

See the LICENSE file for details.
