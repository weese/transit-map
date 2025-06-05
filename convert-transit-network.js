const fs = require('fs');

// Read input file
const inputFile = process.argv[2] || 'hamburg-overlapfree.json';
const outputFile = process.argv[3] || 'output.json';

// Read and parse the input file
const inputData = JSON.parse(fs.readFileSync(inputFile, 'utf8'));

// Initialize output structure
const output = {
    nodes: [],
    edges: [],
    lines: []
};

// Track unique lines
const uniqueLines = new Set();

// Create a map of node IDs to help with edge creation
const nodeMap = new Map();

// Find coordinate bounds for normalization
let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
inputData.features.forEach(feature => {
    if (feature.geometry.type === 'Point') {
        const [x, y] = feature.geometry.coordinates;
        minX = Math.min(minX, x);
        maxX = Math.max(maxX, x);
        minY = Math.min(minY, y);
        maxY = Math.max(maxY, y);
    }
});

// Normalize coordinates function
function normalizeCoordinates(x, y) {
    return [x,y];
}

// Process nodes
inputData.features.forEach(feature => {
    if (feature.geometry.type === 'Point') {
        const nodeId = feature.properties.station_id || feature.properties.id;
        const [normalizedX, normalizedY] = normalizeCoordinates(...feature.geometry.coordinates);
        
        const node = {
            id: nodeId,
            label: feature.properties.station_label || feature.properties.id,
            metadata: {
                x: normalizedX,
                y: normalizedY
            }
        };
        output.nodes.push(node);
        nodeMap.set(nodeId, node);
    }
});

// Helper function to find node by coordinates
function findNodeByCoordinates(coordinates) {
    const [targetX, targetY] = coordinates;
    return output.nodes.find(node => {
        const [nodeX, nodeY] = [node.metadata.x, node.metadata.y];
        // Use normalized coordinates for comparison
        const [normalizedTargetX, normalizedTargetY] = normalizeCoordinates(targetX, targetY);
        return Math.abs(nodeX - normalizedTargetX) < 0.0001 && 
               Math.abs(nodeY - normalizedTargetY) < 0.0001;
    });
}

// Process edges
const processedEdges = new Set(); // To avoid duplicate edges

inputData.features.forEach(feature => {
    if (feature.geometry.type === 'LineString') {
        const coordinates = feature.geometry.coordinates;
        if (coordinates.length >= 2) {
            const sourceNode = findNodeByCoordinates(coordinates[0]);
            const targetNode = findNodeByCoordinates(coordinates[coordinates.length - 1]);

            if (sourceNode && targetNode) {
                // Create a unique edge identifier
                const edgeId = [sourceNode.id, targetNode.id].sort().join('-');
                
                if (!processedEdges.has(edgeId)) {
                    processedEdges.add(edgeId);
                    
                    // Extract line information
                    let lines = [];
                    if (feature.properties.line) {
                        lines = [feature.properties.line];
                        uniqueLines.add(feature.properties.line);
                    }
                    // Also check for lines array
                    if (feature.properties.lines && Array.isArray(feature.properties.lines)) {
                        lines = feature.properties.lines;
                        lines.forEach(line => uniqueLines.add(line));
                    }
                    
                    const edge = {
                        source: sourceNode.id,
                        target: targetNode.id,
                        relation: "subway",
                        metadata: {
                            time: feature.properties.time || 120,
                            lines: lines
                        }
                    };
                    output.edges.push(edge);
                } else {
                    // If edge exists, update its lines
                    const existingEdge = output.edges.find(e => 
                        (e.source === sourceNode.id && e.target === targetNode.id) ||
                        (e.source === targetNode.id && e.target === sourceNode.id)
                    );
                    if (existingEdge && feature.properties.line) {
                        if (!existingEdge.metadata.lines.includes(feature.properties.line)) {
                            existingEdge.metadata.lines.push(feature.properties.line);
                            uniqueLines.add(feature.properties.line);
                        }
                    }
                }
            }
        }
    }
});

// Process lines with predefined colors
const lineColors = {
    'U1': '#55a822',
    'U2': '#ff3300',
    'U3': '#019377',
    'U4': '#ffd900',
    'U5': '#672f17',
    'U6': '#6f4e9c',
    'U7': '#3690c0',
    'U8': '#0a3c85',
    'U9': '#ff7300'
};

// Convert unique lines to output format
uniqueLines.forEach(line => {
    output.lines.push({
        id: line,
        color: lineColors[line] || '#000000', // Default to black if color not found
        group: null
    });
});

// Write output file
fs.writeFileSync(outputFile, JSON.stringify(output, null, 2));

console.log(`Conversion complete. Output written to ${outputFile}`); 
