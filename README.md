# Knowledge Graph MCP

A Model Context Protocol (MCP) server that provides a powerful knowledge graph management system for Claude. This tool allows you to create, manage, and visualize complex networks of interconnected entities with observations and relationships.

## Two Versions Available

### 1. Standard Knowledge Graph MCP (`knowledge_graph_mcp.py`)
The original MCP that stores graphs in `~/.knowledge_graph/` - perfect for personal knowledge management and persistent data storage.

### 2. Custom Path Knowledge Graph MCP (`knowledge_graph_mcp_custom_path.py`) 
**Optimized for Codebase Analysis and Project-Specific Graphs**

This enhanced version allows you to save knowledge graphs to custom locations, making it ideal for:
- **Code-Graph Generation**: Analyze codebases and create knowledge graphs representing functions, classes, modules, and their relationships
- **Project-Specific Analysis**: Save graphs within project directories for version control and team collaboration
- **Sub-Agent Integration**: Perfect for AI agents that need to build and save knowledge graphs in specific locations
- **Multi-Project Management**: Each project can have its own knowledge graph without conflicts

The custom path version includes two additional tools:
- `set_graph_path(path)` - Set a custom save location (relative or absolute)
- `get_current_graph_path()` - Check where the graph is currently being saved

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

### Interactive Visualization & Analysis
- **Interactive HTML Visualization**: Auto-generated D3.js visualizations with zoom, pan, and drag capabilities
- **Automatic Visualization**: Every saved knowledge graph automatically gets an interactive HTML companion file
- **Manual Visualization**: Generate HTML visualizations on-demand using `generate_html_visualization()`
- **Rich Tooltips**: Click and hover on nodes to see detailed entity information and observations
- **Graph Controls**: Adjust node sizes, link distances, reset views, and center graphs
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
- `get_graph_visualization` - Generate static matplotlib graph representations
- `generate_html_visualization` - Create interactive HTML visualizations with D3.js

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
Make the MCPs available across ALL your projects:

```bash
# Navigate to the Knowledge Graph MCP directory
cd ~/knowledge-graph-mcp  # or wherever you cloned/downloaded it

# Get the absolute path of the current directory
pwd  # Note this path for the next step

# INSTALL STANDARD MCP (saves to ~/.knowledge_graph/)
# Remove any existing installation (if needed)
claude mcp remove knowledge-graph

# Add the standard MCP with user scope using ABSOLUTE PATHS
claude mcp add knowledge-graph --scope user -- /absolute/path/to/venv-kgmcp/bin/python /absolute/path/to/knowledge_graph_mcp.py

# INSTALL CUSTOM PATH MCP (for codebase analysis)
# Remove any existing installation (if needed)
claude mcp remove knowledge-graph-custom-path

# Add the custom path MCP with user scope using ABSOLUTE PATHS
claude mcp add knowledge-graph-custom-path --scope user -- /absolute/path/to/venv-kgmcp/bin/python /absolute/path/to/knowledge_graph_mcp_custom_path.py

# Example with actual paths:
# claude mcp add knowledge-graph --scope user -- /home/username/knowledge-graph-mcp/venv-kgmcp/bin/python /home/username/knowledge-graph-mcp/knowledge_graph_mcp.py
# claude mcp add knowledge-graph-custom-path --scope user -- /home/username/knowledge-graph-mcp/venv-kgmcp/bin/python /home/username/knowledge-graph-mcp/knowledge_graph_mcp_custom_path.py

# Verify both installations
claude mcp list
```

You should see output like:
```
Checking MCP server health...
knowledge-graph: /home/username/knowledge-graph-mcp/venv-kgmcp/bin/python /home/username/knowledge-graph-mcp/knowledge_graph_mcp.py - ✓ Connected
knowledge-graph-custom-path: /home/username/knowledge-graph-mcp/venv-kgmcp/bin/python /home/username/knowledge-graph-mcp/knowledge_graph_mcp_custom_path.py - ✓ Connected
```

**Note:** The MCP must show absolute paths in the output. If you see relative paths, it will only work from the installation directory.

**Which MCP to Use:**
- **`knowledge-graph`**: For personal knowledge management, persistent storage in `~/.knowledge_graph/`
- **`knowledge-graph-custom-path`**: For codebase analysis, project-specific graphs, sub-agent integration

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

### Codebase Analysis with Custom Path MCP

The Custom Path MCP is specifically designed for analyzing codebases and creating code-graphs. Here's how to use it:

#### Setting Up for Codebase Analysis
```python
from knowledge_graph_mcp_custom_path import *

# Set the graph to save in your project directory
set_graph_path("./docs/kg/codebase_graph.json")

# Create entities for code components
entities_request = CreateEntitiesRequest(entities=[
    Entity(name="UserController", entityType="class", 
           observations=["Line 10-150", "REST controller", "Handles /api/users/*"]),
    Entity(name="getUserById", entityType="function", 
           observations=["Line 45-60", "Returns User object", "Validates ID parameter"]),
    Entity(name="UserService", entityType="class", 
           observations=["Line 200-400", "Business logic layer", "Manages user operations"]),
    Entity(name="UserRepository", entityType="class", 
           observations=["Line 500-600", "Data access layer", "PostgreSQL queries"])
])
create_entities(entities_request)

# Define code relationships
relations_request = CreateRelationsRequest(relations=[
    Relation(from_="UserController", to="getUserById", relationType="contains"),
    Relation(from_="getUserById", to="UserService", relationType="calls"),
    Relation(from_="UserService", to="UserRepository", relationType="uses"),
    Relation(from_="UserController", to="UserService", relationType="imports")
])
create_relations(relations_request)
```

#### Sub-Agent Integration for Automated Code Analysis
The Custom Path MCP is perfect for sub-agents that analyze codebases:

1. **Main agent** invokes a sub-agent with specific instructions
2. **Sub-agent** uses the Custom Path MCP to:
   - Set a project-specific save location
   - Parse the codebase (using AST tools)
   - Create entities for functions, classes, modules
   - Map relationships (calls, imports, inherits, implements)
   - Save the graph in the project directory
3. **Result**: A complete code-graph saved at `./docs/kg/codebase_graph.json`
4. **🆕 Bonus**: Interactive HTML visualization automatically created at `./docs/kg/graph_visualization.html`

This enables:
- **Dependency tracking**: Visualize how components depend on each other
- **Impact analysis**: Find what code is affected by changes
- **Architecture documentation**: Auto-generate architecture diagrams
- **Code navigation**: Understand complex codebases quickly
- **Refactoring support**: Identify tightly coupled components

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
# 🆕 Generate interactive HTML visualization (RECOMMENDED)
result = generate_html_visualization()
print(f"Interactive HTML created at: {result['htmlPath']}")
# Opens in browser: zoom, pan, drag nodes, hover for details!

# Generate static matplotlib visualization
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
4. **MCP only works in installation directory**: This happens when using relative paths. Always use absolute paths when configuring the MCP globally:
   - ❌ Wrong: `claude mcp add knowledge-graph --scope user venv-kgmcp/bin/python knowledge_graph_mcp.py`
   - ✅ Correct: `claude mcp add knowledge-graph --scope user -- /home/username/path/to/venv-kgmcp/bin/python /home/username/path/to/knowledge_graph_mcp.py`
   - Run `pwd` in your MCP directory to get the correct absolute path

### Validation
Test your installation by asking Claude:
```
Show me the knowledge graph statistics
```

If working correctly, you should see a response with entity and relationship counts.

## Interactive HTML Visualization

### 🎯 **Auto-Generated Visualizations**

**Every knowledge graph automatically gets an interactive HTML visualization!**

When you save any knowledge graph (using any entity or relation creation/modification tool), the system automatically creates:
- **`your-graph.json`** - The knowledge graph data
- **`graph_visualization.html`** - Interactive D3.js visualization

### 📱 **Visualization Features**

**Interactive Navigation:**
- **Zoom**: Mouse wheel to zoom in/out (0.1x to 4x)
- **Pan**: Click and drag on empty space to move around
- **Drag Nodes**: Click and drag any node to reposition it
- **Click to Center**: Click any node to smoothly center it on screen

**Visual Elements:**
- **Color-coded nodes** by entity type with automatic legend
- **Directional arrows** showing relationship flow
- **Node labels** displaying entity names
- **Link labels** showing relationship types
- **Dynamic tooltips** on hover with full entity details

**Interactive Controls:**
- **Node Size**: Switch between Small/Medium/Large nodes
- **Link Distance**: Adjust Short/Medium/Long connection distances
- **Reset View**: Return to original zoom/position
- **Center Graph**: Auto-fit entire graph in view

### 🚀 **Usage Examples**

#### Automatic Visualization (Recommended)
```python
# Just use the MCP normally - HTML is auto-generated!
from knowledge_graph_mcp_custom_path import *

# Set your project path
set_graph_path("./docs/knowledge-graph.json")

# Create entities and relations as usual
entities = CreateEntitiesRequest(entities=[
    Entity(name="UserService", entityType="service",
           observations=["Handles authentication", "REST API endpoints"]),
    Entity(name="Database", entityType="infrastructure",
           observations=["PostgreSQL", "User data storage"])
])
create_entities(entities)

# Relations are created
relations = CreateRelationsRequest(relations=[
    Relation(from_="UserService", to="Database", relationType="depends_on")
])
create_relations(relations)

# 🎉 HTML visualization automatically created at ./docs/graph_visualization.html
```

#### Manual Visualization Generation
```python
# Generate HTML visualization on-demand
result = generate_html_visualization()
print(f"HTML created at: {result['htmlPath']}")
# Open the HTML file in your browser to explore!
```

### 📂 **File Structure After Creating Graphs**

```
your-project/
├── docs/
│   ├── knowledge-graph.json          # Your graph data
│   ├── graph_visualization.html      # 🆕 Interactive visualization
│   └── backups/                      # Automatic backups
├── src/
└── README.md
```

### 🌐 **Opening Your Visualization**

**Option 1: Direct Browser Opening**
```bash
# Linux/WSL
xdg-open ./docs/graph_visualization.html

# macOS
open ./docs/graph_visualization.html

# Windows
start ./docs/graph_visualization.html
```

**Option 2: File Explorer**
- Navigate to your graph directory
- Double-click `graph_visualization.html`
- Opens in your default browser

### 🎨 **Visualization Customization**

The HTML file includes:
- **Responsive design** that works on desktop and mobile
- **Professional styling** with clean, modern interface
- **Statistics dashboard** showing entity/relation counts
- **Graph path display** showing the source JSON file
- **Auto-layout algorithm** that positions nodes optimally
- **Performance optimized** for large graphs (hundreds of nodes)

### 💡 **Perfect for Code Analysis**

When used with code analysis sub-agents, you get:

1. **High-level Architecture** (`code-graph.json` → `graph_visualization.html`)
   - Visualize modules, services, and their relationships
   - Understand system architecture at a glance
   - Perfect for documentation and onboarding

2. **Detailed Implementation** (`clean_analysis.json` → `graph_visualization.html`)
   - Explore every function, class, and configuration
   - Navigate through detailed code relationships
   - Ideal for debugging and refactoring

### 🔧 **Technical Details**

- **Technology**: D3.js v7 with force-directed layout
- **Dependencies**: None (completely self-contained HTML file)
- **File Size**: Typically 50-200KB depending on graph size
- **Browser Support**: All modern browsers (Chrome, Firefox, Safari, Edge)
- **Performance**: Handles graphs with 100+ entities smoothly

### 🚫 **Disabling Auto-Visualization**

If you need to disable automatic HTML generation:
```python
# Save without auto-generating HTML
save_graph(your_graph, auto_generate_html=False)
```

## Contributing

To extend the Knowledge Graph MCP:
1. Add new tools to `knowledge_graph_mcp.py`
2. Follow the existing pattern for error handling and data validation
3. Update the README with new features

## License

This project is part of the development work and follows established development practices.