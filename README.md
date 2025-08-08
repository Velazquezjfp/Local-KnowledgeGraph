# Knowledge Graph MCP

A Model Context Protocol (MCP) server that provides a powerful knowledge graph management system for Claude. This tool allows you to create, manage, and visualize complex networks of interconnected entities with observations and relationships.

## Features

### Core Knowledge Graph Operations
- **Entity Management**: Create, read, update, and delete entities with types and observations
- **Relationship Management**: Define and manage typed relationships between entities
- **Advanced Search**: Search entities by keywords, types, and properties
- **Path Finding**: Discover connections and paths between entities
- **Cluster Detection**: Identify communities and groups within your knowledge graph

### Data Operations
- **Export**: Export your graph in multiple formats (JSON, CSV, GraphML)
- **Backup & Restore**: Automatic backups with manual restore capabilities
- **Merge Entities**: Combine duplicate entities while preserving all relationships
- **Statistics**: Comprehensive analytics and reporting on your knowledge graph

### Visualization & Analysis
- **Graph Visualization**: Generate visual representations of your knowledge network
- **Relationship Suggestions**: AI-powered suggestions for potential new connections
- **Advanced Filtering**: Filter entities and relationships by multiple criteria
- **Comprehensive Reports**: Detailed analysis with recommendations for graph improvement

## Available Tools

### Entity Operations
- `create_entities` - Create multiple entities with names, types, and observations
- `add_observations` - Add new observations to existing entities
- `delete_entities` - Remove entities and their associated relationships
- `delete_observations` - Remove specific observations from entities
- `merge_entities` - Combine two entities into one

### Relationship Operations
- `create_relations` - Create typed relationships between entities
- `delete_relations` - Remove specific relationships
- `find_paths` - Find connection paths between two entities
- `suggest_relations` - Get AI suggestions for potential new relationships

### Search & Discovery
- `read_graph` - Retrieve the entire knowledge graph
- `search_nodes` - Search entities by keywords
- `open_nodes` - Retrieve specific entities by name
- `advanced_search` - Multi-criteria filtering and search

### Analysis & Reporting
- `get_statistics` - Comprehensive graph statistics
- `generate_report` - Detailed analysis with recommendations
- `detect_clusters` - Community detection within the graph
- `get_graph_visualization` - Generate visual graph representations

### Data Management
- `export_graph` - Export in JSON, CSV, or GraphML formats
- `backup_graph` - Create timestamped backups
- `restore_graph` - Restore from backup files

## Installation

### Prerequisites
- Python 3.8+
- UV package manager (recommended)
- Claude Desktop application

### Step 1: Set up the Environment
```bash
# Create project directory
mkdir C:\user\KnowledgeGraph
cd C:\user\KnowledgeGraph

# Create virtual environment with UV
uv venv venv-kgmcp

# Activate the virtual environment (Windows)
venv-kgmcp\Scripts\activate

# Install required dependencies
uv pip install mcp fastmcp pydantic matplotlib networkx python-louvain
```

### Step 2: Install the MCP
```bash
# Copy knowledge_graph_mcp.py to your project directory
# Then install the Knowledge Graph MCP using the specific Python interpreter
mcp install knowledge_graph_mcp.py -v UV_PYTHON=C:\user\KnowledgeGraph\venv-kgmcp\Scripts\python.exe
```

### Step 3: Configure Claude Desktop

Add the following configuration to your Claude Desktop `claude_desktop_config.json` file:

```json
{
  "mcps": {
    "Knowledge Graph": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "C:\\user\\KnowledgeGraph\\knowledge_graph_mcp.py"
      ],
      "env": {
        "UV_PYTHON": "C:\\user\\KnowledgeGraph\\venv-kgmcp\\Scripts\\python.exe"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop
After updating the configuration, restart Claude Desktop to load the new MCP server.

## Usage Examples

### Creating Your First Knowledge Graph
```
Create entities for a software project:
- Entity: "Authentication Service", type: "service", observations: ["Handles user login", "Uses JWT tokens"]
- Entity: "Database", type: "infrastructure", observations: ["PostgreSQL instance", "Stores user data"]
- Entity: "API Gateway", type: "service", observations: ["Routes requests", "Rate limiting enabled"]

Create relationships:
- "Authentication Service" -> "Database" (relation: "depends_on")
- "API Gateway" -> "Authentication Service" (relation: "routes_to")
```

### Advanced Search
```
Find all entities of type "service" that have at least 2 observations and are connected to fewer than 5 other entities.
```

### Visualization
```
Generate a graph visualization to see the network structure and identify central nodes.
```

### Path Analysis
```
Find all paths between "User Interface" and "Database" to understand data flow.
```

## Data Storage

The knowledge graph is automatically stored in:
- **Main Graph**: `~/.knowledge_graph/graph.json`
- **Backups**: `~/.knowledge_graph/backups/`

Data is automatically backed up before major operations and can be restored at any time.

## Development

### Architecture
- Built with FastMCP for efficient tool execution
- Uses Pydantic for data validation and modeling
- NetworkX for graph algorithms and analysis
- Matplotlib for visualization generation

### File Structure
```
C:\user\KnowledgeGraph\
├── knowledge_graph_mcp.py    # Main MCP server
├── README.md                 # This file
└── venv-kgmcp/              # Virtual environment
```

### Dependencies
- `mcp` - Model Context Protocol framework
- `fastmcp` - FastMCP server implementation
- `pydantic` - Data validation and modeling
- `matplotlib` - Graph visualization
- `networkx` - Graph algorithms
- `python-louvain` - Community detection

## Troubleshooting

### Common Issues
1. **MCP not appearing in Claude**: Ensure Claude Desktop is restarted after configuration
2. **Visualization errors**: Check that matplotlib and networkx are installed in the virtual environment
3. **Path issues**: Verify all paths in the configuration use double backslashes (`\\`) on Windows

### Validation
Test your installation by asking Claude:
```
Show me the knowledge graph statistics
```

If working correctly, you should see a response with entity and relationship counts.

## Contributing

To extend the Knowledge Graph MCP:
1. Add new tools to `knowledge_graph_mcp.py`
2. Follow the existing pattern for error handling and data validation
3. Update the README with new features

## License

This project is part of the development work and follows established development practices.