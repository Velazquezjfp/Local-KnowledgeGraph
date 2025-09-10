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
- pip package manager
- UV package manager (optional but recommended)
- Claude Desktop application (optional)

## Linux Installation

### Option 1: Using UV (Recommended)

```bash
# Clone or download the repository
git clone <repository-url> ~/knowledge-graph-mcp
cd ~/knowledge-graph-mcp

# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment with UV
~/.local/bin/uv venv venv-kgmcp

# Install dependencies with UV
~/.local/bin/uv pip install --python venv-kgmcp/bin/python -r requirements.txt

# Make the startup script executable
chmod +x run_kg_server.sh

# Run the server
./run_kg_server.sh
```

### Option 2: Using pip

```bash
# Clone or download the repository
git clone <repository-url> ~/knowledge-graph-mcp
cd ~/knowledge-graph-mcp

# Create virtual environment
python3 -m venv venv-kgmcp

# Activate virtual environment
source venv-kgmcp/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server directly
python knowledge_graph_mcp.py
```

## Windows Installation

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
uv pip install -r requirements.txt
```

### Step 2: Run the MCP Server
```bash
# Run directly with Python
venv-kgmcp\Scripts\python.exe knowledge_graph_mcp.py
```

## Configure Claude Desktop (Optional)

### Linux Configuration

Add to your Claude Desktop `claude_desktop_config.json` file (usually in `~/.config/claude/`):

```json
{
  "mcps": {
    "Knowledge Graph": {
      "command": "/home/YOUR_USERNAME/.local/bin/uv",
      "args": [
        "run",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/home/YOUR_USERNAME/knowledge-graph-mcp/knowledge_graph_mcp.py"
      ],
      "env": {
        "UV_PYTHON": "/home/YOUR_USERNAME/knowledge-graph-mcp/venv-kgmcp/bin/python"
      }
    }
  }
}
```

### Windows Configuration

Add to your Claude Desktop `claude_desktop_config.json` file:

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

### After Configuration
Restart Claude Desktop to load the new MCP server.

## Claude Code Installation

### Installing MCP in Claude Code

If you're using Claude Code (not Claude Desktop), you can install the MCP directly from the command line:

#### Global Installation (Recommended)
Make the MCP available across ALL your projects:

```bash
# Navigate to the Knowledge Graph MCP directory
cd ~/knowledge-graph-mcp  # or wherever you cloned/downloaded it

# Remove any existing installation (if needed)
claude mcp remove knowledge-graph

# Add the MCP with user scope (globally available)
claude mcp add knowledge-graph --scope user venv-kgmcp/bin/python knowledge_graph_mcp.py

# Verify the installation
claude mcp list
```

You should see output like:
```
Checking MCP server health...
knowledge-graph: venv-kgmcp/bin/python knowledge_graph_mcp.py - ✓ Connected
```

#### Project-Specific Installation
If you only want the MCP for a specific project:

```bash
# In your project directory
claude mcp add knowledge-graph --scope project /path/to/knowledge_graph_mcp.py
```

#### Local Installation (Current User Only)
For personal use in the current project only:

```bash
# Default scope is local
claude mcp add knowledge-graph /path/to/knowledge_graph_mcp.py
```

### Scope Options Explained

- **`--scope user`**: Available in ALL your projects (stored in `~/.claude.json`)
- **`--scope project`**: Shared with team via `.mcp.json` file in project
- **`--scope local`**: Only for you in current project (default)

### Managing Your MCP

```bash
# List all installed MCPs and their status
claude mcp list

# Get details about a specific MCP
claude mcp get knowledge-graph

# Remove an MCP
claude mcp remove knowledge-graph

# In Claude Code, check connected MCPs
/mcp
```

## Testing the Installation

### Linux Testing

```bash
# Test the server with the included test script
venv-kgmcp/bin/python test_kg.py

# Or if you made the run script executable
./run_kg_server.sh

# You can also test individual functions
venv-kgmcp/bin/python -c "from knowledge_graph_mcp import get_graph_file_path; print(f'Data location: {get_graph_file_path()}')"
```

### Windows Testing

```bash
# Test the server with the included test script
venv-kgmcp\Scripts\python.exe test_kg.py

# Test individual functions
venv-kgmcp\Scripts\python.exe -c "from knowledge_graph_mcp import get_graph_file_path; print(f'Data location: {get_graph_file_path()}')"
```

### Expected Test Output

When you run `test_kg.py`, you should see:
```
Testing Knowledge Graph MCP Server...
Data will be stored at: /home/username/.knowledge_graph/graph.json
--------------------------------------------------

1. Creating test entities...
   Result: success - Added 3 entities

2. Creating relations...
   Result: success - Added 2 relations

3. Reading the entire graph...
   Entities: 3
   Relations: 2

4. Testing search...
   Found 2 matches for 'Python'

5. Getting statistics...
   Total entities: 3
   Total relations: 2
   Entity types: {'language': 1, 'library': 1, 'system': 1}

==================================================
All tests completed successfully!
Graph data stored at: /home/username/.knowledge_graph/graph.json
```

## Usage Examples

### Creating Your First Knowledge Graph

#### Adding Entities
```python
# Using the test script or in your own Python code
from knowledge_graph_mcp import *

# Create multiple entities
entities_request = CreateEntitiesRequest(entities=[
    Entity(name="Authentication Service", entityType="service", 
           observations=["Handles user login", "Uses JWT tokens"]),
    Entity(name="Database", entityType="infrastructure", 
           observations=["PostgreSQL instance", "Stores user data"]),
    Entity(name="API Gateway", entityType="service", 
           observations=["Routes requests", "Rate limiting enabled"])
])
result = create_entities(entities_request)
```

#### Adding Relationships
```python
# Create relationships between entities
relations_request = CreateRelationsRequest(relations=[
    Relation(from_="Authentication Service", to="Database", relationType="depends_on"),
    Relation(from_="API Gateway", to="Authentication Service", relationType="routes_to")
])
result = create_relations(relations_request)
```

### Modifying Existing Data

#### Adding Observations to Entities
```python
# Add new observations to an existing entity
obs_request = AddObservationsRequest(
    entityName="Database",
    observations=["Backup daily at 2 AM", "Replicated across regions"]
)
result = add_observations(obs_request)
```

#### Merging Duplicate Entities
```python
# Merge two entities (useful for cleaning duplicates)
merge_request = MergeEntitiesRequest(
    sourceName="Auth Service",  # This entity will be removed
    targetName="Authentication Service"  # All data moved here
)
result = merge_entities(merge_request)
```

### Deleting Data

#### Delete Entities
```python
# Delete entities and their associated relationships
delete_request = DeleteEntitiesRequest(
    entityNames=["Old Service", "Deprecated API"]
)
result = delete_entities(delete_request)
```

#### Delete Specific Observations
```python
# Remove specific observations from an entity
del_obs_request = DeleteObservationsRequest(
    entityName="Database",
    observations=["Outdated info", "Wrong observation"]
)
result = delete_observations(del_obs_request)
```

#### Delete Relationships
```python
# Remove specific relationships
del_rel_request = DeleteRelationsRequest(relations=[
    Relation(from_="API Gateway", to="Old Service", relationType="routes_to")
])
result = delete_relations(del_rel_request)
```

### Searching and Querying

#### Basic Search
```python
# Search for entities by keyword
search_request = SearchRequest(query="authentication")
result = search_nodes(search_request)
```

#### Advanced Search with Filters
```python
# Find entities with specific criteria
adv_search = AdvancedSearchRequest(
    entityType="service",
    minObservations=2,
    maxRelations=5
)
result = advanced_search(adv_search)
```

#### Finding Paths Between Entities
```python
# Find connection paths between two entities
paths = find_paths(
    source="User Interface",
    target="Database",
    max_length=3
)
```

### Visualization and Analysis
```python
# Generate a graph visualization
visualization = get_graph_visualization()

# Get comprehensive statistics
stats = get_statistics()

# Generate a detailed report with recommendations
report = generate_report()

# Detect clusters/communities in the graph
clusters = detect_clusters()

# Get AI-powered relationship suggestions
suggestions = suggest_relations()
```

### Data Management

#### Export Data
```python
# Export in different formats
export_request = ExportGraphRequest(format="json")  # or "csv", "graphml"
result = export_graph(export_request)
```

#### Backup and Restore
```python
# Create a backup
backup_result = backup_graph()

# Restore from backup (latest by default)
restore_result = restore_graph()

# Restore from specific backup file
restore_result = restore_graph(backup_file="graph_backup_20240101_120000.json")
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