from mcp.server.fastmcp import FastMCP, Context, Image
from typing import List, Optional, Dict, Any, Annotated
from pydantic import BaseModel, Field, field_validator
import json
from pathlib import Path
import io
import base64
import shutil
from datetime import datetime

# Define our data models
class Entity(BaseModel):
    name: str
    entityType: str
    observations: List[str] = Field(default_factory=list)
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Entity name cannot be empty')
        return v.strip()

class Relation(BaseModel):
    from_: str
    to: str
    relationType: str
    
    @field_validator('from_', 'to', 'relationType')
    @classmethod
    def fields_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

class KnowledgeGraph(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relations: List[Relation] = Field(default_factory=list)
    
    # Additional attributes for internal use (not serialized)
    _name_index: Optional[Dict[str, int]] = None
    
    model_config = {
        "arbitrary_types_allowed": True,
        "extra": "ignore"
    }

class CreateEntitiesRequest(BaseModel):
    entities: List[Entity]

class CreateRelationsRequest(BaseModel):
    relations: List[Relation]

class AddObservationsRequest(BaseModel):
    entityName: str
    observations: List[str]

class DeleteEntitiesRequest(BaseModel):
    entityNames: List[str]

class DeleteObservationsRequest(BaseModel):
    entityName: str
    observations: List[str]

class DeleteRelationsRequest(BaseModel):
    relations: List[Relation]

class SearchRequest(BaseModel):
    query: str

class OpenNodesRequest(BaseModel):
    names: List[str]

class MergeEntitiesRequest(BaseModel):
    sourceName: str
    targetName: str

class ExportGraphRequest(BaseModel):
    format: str = "json"

class AdvancedSearchRequest(BaseModel):
    entityType: Optional[str] = None
    relationType: Optional[str] = None
    minObservations: Optional[int] = None
    maxRelations: Optional[int] = None

# Create MCP server
mcp = FastMCP("Knowledge Graph Custom Path")

# Global variable to store custom path
_custom_graph_path = None

# File operations for persistence
def get_graph_file_path():
    # Use custom path if set, otherwise use default
    if _custom_graph_path:
        # Handle both absolute and relative paths
        graph_path = Path(_custom_graph_path)
        
        # If path starts with ~, expand it
        if str(graph_path).startswith('~'):
            graph_path = graph_path.expanduser()
        # If path is relative (doesn't start with /), make it relative to current working directory
        elif not graph_path.is_absolute():
            graph_path = Path.cwd() / graph_path
        
        graph_path = graph_path.resolve()
        graph_path.parent.mkdir(parents=True, exist_ok=True)
        return graph_path
    
    # Default: Store graph in user's home directory in a hidden folder
    home_dir = Path.home()
    graph_dir = home_dir / ".knowledge_graph"
    graph_dir.mkdir(exist_ok=True)
    return graph_dir / "graph.json"

def read_graph_file() -> KnowledgeGraph:
    file_path = get_graph_file_path()
    if not file_path.exists():
        return KnowledgeGraph()
    
    with open(file_path, "r") as f:
        try:
            data = json.load(f)
            graph = KnowledgeGraph.model_validate(data)
            # Create an index for faster lookups
            graph._name_index = {e.name.lower(): i for i, e in enumerate(graph.entities)}
            return graph
        except (json.JSONDecodeError, ValueError):
            return KnowledgeGraph()

def save_graph(graph: KnowledgeGraph, auto_generate_html: bool = True):
    file_path = get_graph_file_path()
    # Create a backup before saving
    if file_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = file_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)
        backup_path = backup_dir / f"graph_{timestamp}.json.bak"
        shutil.copy(file_path, backup_path)

        # Keep only the last 10 backups
        backup_files = sorted(list(backup_dir.glob("*.bak")))
        if len(backup_files) > 10:
            for old_file in backup_files[:-10]:
                old_file.unlink()

    # Save the graph without the index
    graph_dict = graph.model_dump(exclude={'_name_index'})
    with open(file_path, "w") as f:
        json.dump(graph_dict, indent=2, fp=f)

    # Auto-generate HTML visualization if graph has entities and relations
    if auto_generate_html and graph.entities and len(graph.entities) > 0:
        try:
            _generate_html_visualization_internal(graph, file_path)
        except Exception as e:
            # Don't fail the save operation if visualization fails
            print(f"Warning: Could not auto-generate visualization: {e}")

def find_entity_by_name(graph: KnowledgeGraph, name: str) -> Optional[Entity]:
    """Helper function to find an entity by name (case-insensitive)"""
    name = name.lower()
    if graph._name_index is not None and name in graph._name_index:
        return graph.entities[graph._name_index[name]]
    
    # Fallback if index is not available
    return next((e for e in graph.entities if e.name.lower() == name), None)

def _generate_html_visualization_internal(graph: KnowledgeGraph, graph_file_path: Path):
    """Internal function to generate HTML visualization"""
    html_file_path = graph_file_path.parent / "graph_visualization.html"

    # Prepare data for D3.js
    nodes = []
    for i, entity in enumerate(graph.entities):
        nodes.append({
            "id": entity.name,
            "type": entity.entityType,
            "observations": entity.observations,
            "index": i
        })

    links = []
    for relation in graph.relations:
        links.append({
            "source": relation.from_,
            "target": relation.to,
            "type": relation.relationType
        })

    # Count entity types for color mapping
    entity_types = list(set(entity.entityType for entity in graph.entities))

    # Create the HTML content (reusing the same template from the main function)
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Graph Visualization - {graph_file_path.stem}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}

        .container {{
            max-width: 100%;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 20px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .graph-path {{
            font-size: 12px;
            color: #666;
            margin-top: 8px;
            font-family: monospace;
            background: #f8f9fa;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }}

        .stats {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 10px;
        }}

        .stat {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}

        .stat-label {{
            font-size: 14px;
            color: #666;
        }}

        .graph-container {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }}

        .controls {{
            padding: 15px;
            border-bottom: 1px solid #eee;
            display: flex;
            gap: 15px;
            align-items: center;
            flex-wrap: wrap;
        }}

        .control-group {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .control-group label {{
            font-size: 14px;
            font-weight: 500;
        }}

        .control-group select, .control-group button {{
            padding: 5px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }}

        .control-group button {{
            background: #007bff;
            color: white;
            cursor: pointer;
            border: none;
        }}

        .control-group button:hover {{
            background: #0056b3;
        }}

        #graph {{
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
        }}

        .node {{
            cursor: pointer;
            stroke: #fff;
            stroke-width: 2px;
        }}

        .link {{
            fill: none;
            stroke: #999;
            stroke-width: 1.5px;
            marker-end: url(#arrowhead);
        }}

        .node-label {{
            font-size: 12px;
            font-weight: bold;
            text-anchor: middle;
            pointer-events: none;
            fill: #333;
        }}

        .link-label {{
            font-size: 10px;
            text-anchor: middle;
            pointer-events: none;
            fill: #666;
        }}

        .tooltip {{
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            color: white;
            padding: 12px;
            border-radius: 6px;
            font-size: 14px;
            pointer-events: none;
            max-width: 300px;
            z-index: 1000;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}

        .tooltip h3 {{
            margin: 0 0 8px 0;
            font-size: 16px;
            color: #4fc3f7;
        }}

        .tooltip .type {{
            color: #81c784;
            font-weight: bold;
            margin-bottom: 8px;
        }}

        .tooltip .observations {{
            margin-top: 8px;
        }}

        .tooltip .observations h4 {{
            margin: 0 0 4px 0;
            font-size: 12px;
            color: #ffb74d;
        }}

        .tooltip .observations ul {{
            margin: 0;
            padding-left: 16px;
        }}

        .tooltip .observations li {{
            font-size: 12px;
            margin-bottom: 2px;
        }}

        .legend {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.95);
            padding: 15px;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            max-width: 200px;
        }}

        .legend h4 {{
            margin: 0 0 10px 0;
            font-size: 14px;
            color: #333;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 6px;
            font-size: 12px;
        }}

        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            margin-right: 8px;
            border: 1px solid #ccc;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Knowledge Graph: {graph_file_path.stem}</h1>
            <div class="graph-path">{str(graph_file_path)}</div>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{len(graph.entities)}</div>
                    <div class="stat-label">Entities</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{len(graph.relations)}</div>
                    <div class="stat-label">Relations</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{len(entity_types)}</div>
                    <div class="stat-label">Types</div>
                </div>
            </div>
        </div>

        <div class="graph-container">
            <div class="controls">
                <div class="control-group">
                    <label for="nodeSize">Node Size:</label>
                    <select id="nodeSize">
                        <option value="small">Small</option>
                        <option value="medium" selected>Medium</option>
                        <option value="large">Large</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="linkDistance">Link Distance:</label>
                    <select id="linkDistance">
                        <option value="short">Short</option>
                        <option value="medium" selected>Medium</option>
                        <option value="long">Long</option>
                    </select>
                </div>
                <div class="control-group">
                    <button onclick="resetZoom()">Reset View</button>
                </div>
                <div class="control-group">
                    <button onclick="centerGraph()">Center Graph</button>
                </div>
            </div>
            <svg id="graph"></svg>
            <div class="legend" id="legend"></div>
        </div>
    </div>

    <div class="tooltip" id="tooltip" style="display: none;"></div>

    <script>
        // Data
        const nodes = {json.dumps(nodes, indent=8)};
        const links = {json.dumps(links, indent=8)};

        // Set up dimensions and margins
        const margin = {{top: 20, right: 20, bottom: 20, left: 20}};
        const width = 1200;
        const height = 600;

        // Create SVG
        const svg = d3.select("#graph")
            .attr("width", width)
            .attr("height", height);

        // Create groups for zoomable content
        const container = svg.append("g");

        // Define zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", function(event) {{
                container.attr("transform", event.transform);
            }});

        svg.call(zoom);

        // Color scale for node types
        const entityTypes = [...new Set(nodes.map(d => d.type))];
        const colorScale = d3.scaleOrdinal()
            .domain(entityTypes)
            .range(d3.schemeCategory10);

        // Create legend
        function createLegend() {{
            const legend = d3.select("#legend");
            legend.append("h4").text("Entity Types");

            const items = legend.selectAll(".legend-item")
                .data(entityTypes)
                .enter()
                .append("div")
                .attr("class", "legend-item");

            items.append("div")
                .attr("class", "legend-color")
                .style("background-color", d => colorScale(d));

            items.append("span")
                .text(d => d);
        }}

        // Define arrow marker
        svg.append("defs").append("marker")
            .attr("id", "arrowhead")
            .attr("viewBox", "-0 -5 10 10")
            .attr("refX", 20)
            .attr("refY", 0)
            .attr("orient", "auto")
            .attr("markerWidth", 8)
            .attr("markerHeight", 8)
            .attr("xoverflow", "visible")
            .append("svg:path")
            .attr("d", "M 0,-5 L 10 ,0 L 0,5")
            .attr("fill", "#999")
            .style("stroke", "none");

        // Create force simulation
        let simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-400))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(25));

        // Create links
        const link = container.append("g")
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("class", "link");

        // Create link labels
        const linkLabel = container.append("g")
            .selectAll("text")
            .data(links)
            .enter().append("text")
            .attr("class", "link-label")
            .text(d => d.type);

        // Create nodes
        const node = container.append("g")
            .selectAll("circle")
            .data(nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", 12)
            .attr("fill", d => colorScale(d.type))
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        // Create node labels
        const nodeLabel = container.append("g")
            .selectAll("text")
            .data(nodes)
            .enter().append("text")
            .attr("class", "node-label")
            .attr("dy", -15)
            .text(d => d.id);

        // Tooltip
        const tooltip = d3.select("#tooltip");

        // Node interactions
        node
            .on("mouseover", function(event, d) {{
                // Highlight node
                d3.select(this).attr("stroke", "#333").attr("stroke-width", 3);

                // Show tooltip
                let tooltipContent = `<h3>${{d.id}}</h3>`;
                tooltipContent += `<div class="type">Type: ${{d.type}}</div>`;

                if (d.observations && d.observations.length > 0) {{
                    tooltipContent += '<div class="observations"><h4>Observations:</h4><ul>';
                    d.observations.forEach(obs => {{
                        tooltipContent += `<li>${{obs}}</li>`;
                    }});
                    tooltipContent += '</ul></div>';
                }}

                tooltip.html(tooltipContent)
                    .style("display", "block")
                    .style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY + 10) + "px");
            }})
            .on("mousemove", function(event) {{
                tooltip.style("left", (event.pageX + 10) + "px")
                    .style("top", (event.pageY + 10) + "px");
            }})
            .on("mouseout", function() {{
                // Remove highlight
                d3.select(this).attr("stroke", "#fff").attr("stroke-width", 2);

                // Hide tooltip
                tooltip.style("display", "none");
            }})
            .on("click", function(event, d) {{
                // Center on clicked node
                const transform = d3.zoomTransform(svg.node());
                const x = -d.x * transform.k + width / 2;
                const y = -d.y * transform.k + height / 2;

                svg.transition().duration(500).call(
                    zoom.transform,
                    d3.zoomIdentity.translate(x, y).scale(transform.k)
                );
            }});

        // Simulation tick
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            linkLabel
                .attr("x", d => (d.source.x + d.target.x) / 2)
                .attr("y", d => (d.source.y + d.target.y) / 2);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);

            nodeLabel
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});

        // Drag functions
        function dragstarted(event) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            event.subject.fx = event.subject.x;
            event.subject.fy = event.subject.y;
        }}

        function dragged(event) {{
            event.subject.fx = event.x;
            event.subject.fy = event.y;
        }}

        function dragended(event) {{
            if (!event.active) simulation.alphaTarget(0);
            event.subject.fx = null;
            event.subject.fy = null;
        }}

        // Control functions
        function resetZoom() {{
            svg.transition().duration(500).call(
                zoom.transform,
                d3.zoomIdentity
            );
        }}

        function centerGraph() {{
            const bounds = container.node().getBBox();
            const fullWidth = width;
            const fullHeight = height;
            const widthScale = fullWidth / bounds.width;
            const heightScale = fullHeight / bounds.height;
            const scale = Math.min(widthScale, heightScale) * 0.8;
            const translate = [fullWidth / 2 - scale * bounds.x - scale * bounds.width / 2,
                             fullHeight / 2 - scale * bounds.y - scale * bounds.height / 2];

            svg.transition().duration(500).call(
                zoom.transform,
                d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale)
            );
        }}

        // Control event listeners
        d3.select("#nodeSize").on("change", function() {{
            const size = this.value;
            const radius = size === "small" ? 8 : size === "large" ? 16 : 12;
            node.attr("r", radius);
            simulation.force("collision").radius(radius + 5);
            simulation.restart();
        }});

        d3.select("#linkDistance").on("change", function() {{
            const distance = this.value;
            const dist = distance === "short" ? 50 : distance === "long" ? 150 : 100;
            simulation.force("link").distance(dist);
            simulation.restart();
        }});

        // Initialize
        createLegend();

        // Auto-center after initial layout
        setTimeout(() => {{
            centerGraph();
        }}, 1000);
    </script>
</body>
</html>'''

    # Write the HTML file
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

# MCP tools

@mcp.tool()
def set_graph_path(path: str) -> Dict[str, Any]:
    """
    Set a custom path for the knowledge graph file.
    
    Provide either:
    - Relative path: ./docs/kg/graph.json (relative to current working directory)
    - Absolute path: /full/path/to/graph.json
    - Home path: ~/docs/kg/graph.json
    """
    global _custom_graph_path
    try:
        # Store the original path string
        _custom_graph_path = path
        
        # Get the resolved path for display
        resolved_path = get_graph_file_path()
        
        return {
            "status": "success",
            "message": f"Graph path set to: {resolved_path}",
            "original_path": path,
            "resolved_path": str(resolved_path),
            "is_relative": not Path(path).is_absolute() and not path.startswith('~')
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to set graph path: {str(e)}"
        }

@mcp.tool()
def get_current_graph_path() -> Dict[str, Any]:
    """
    Get the current path where the knowledge graph is stored.
    """
    try:
        current_path = get_graph_file_path()
        return {
            "status": "success",
            "path": str(current_path),
            "is_custom": _custom_graph_path is not None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get graph path: {str(e)}"
        }

@mcp.tool()
def create_entities(request: CreateEntitiesRequest) -> Dict[str, Any]:
    """
    Create multiple entities in the graph.
    
    Provide a list of entities to add to the knowledge graph.
    Each entity needs a name, entityType, and optional observations.
    """
    try:
        graph = read_graph_file()
        existing_names = {e.name.lower() for e in graph.entities}
        
        # Convert all entity names to lowercase for case-insensitive matching
        new_entities = []
        for entity in request.entities:
            entity_lower = entity.name.lower()
            if entity_lower not in existing_names:
                # Keep original case for display but ensure uniqueness
                entity.name = entity.name.strip()
                new_entities.append(entity)
        
        if not new_entities:
            return {"status": "success", "message": "No new entities to add", "added": 0}
            
        graph.entities.extend(new_entities)
        save_graph(graph)
        
        return {
            "status": "success", 
            "message": f"Added {len(new_entities)} entities", 
            "added": len(new_entities),
            "entities": [e.dict() for e in new_entities]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def create_relations(request: CreateRelationsRequest) -> Dict[str, Any]:
    """
    Create multiple relations between entities.
    
    Provide a list of relations to add to the knowledge graph.
    Each relation consists of from_ (source entity), to (target entity), 
    and relationType (how they are related).
    """
    try:
        graph = read_graph_file()
        
        # Normalize entity names to lowercase for lookups
        entity_names = {e.name.lower() for e in graph.entities}
        missing_entities = []
        valid_relations = []
        
        for relation in request.relations:
            from_lower = relation.from_.lower()
            to_lower = relation.to.lower()
            
            if from_lower not in entity_names:
                missing_entities.append(relation.from_)
                continue
                
            if to_lower not in entity_names:
                missing_entities.append(relation.to)
                continue
                
            # Use actual stored case for entity names
            relation.from_ = next(e.name for e in graph.entities if e.name.lower() == from_lower)
            relation.to = next(e.name for e in graph.entities if e.name.lower() == to_lower)
            valid_relations.append(relation)
        
        if missing_entities:
            return {
                "status": "error", 
                "message": f"Entities not found: {', '.join(missing_entities)}"
            }
        
        # Add new relations, avoiding duplicates
        existing = {(r.from_.lower(), r.to.lower(), r.relationType.lower()) for r in graph.relations}
        new_relations = [r for r in valid_relations 
                         if (r.from_.lower(), r.to.lower(), r.relationType.lower()) not in existing]
        
        if not new_relations:
            return {"status": "success", "message": "No new relations to add", "added": 0}
            
        graph.relations.extend(new_relations)
        save_graph(graph)
        
        return {
            "status": "success", 
            "message": f"Added {len(new_relations)} relations", 
            "added": len(new_relations),
            "relations": [r.dict() for r in new_relations]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def add_observations(request: AddObservationsRequest) -> Dict[str, Any]:
    """
    Add new observations to an existing entity.
    
    Specify the entityName and a list of observations to add to that entity.
    """
    try:
        graph = read_graph_file()
        entity = find_entity_by_name(graph, request.entityName)
        
        if not entity:
            return {"status": "error", "message": f"Entity '{request.entityName}' not found"}
        
        # Filter out empty observations and duplicates
        new_observations = [obs for obs in request.observations 
                           if obs.strip() and obs not in entity.observations]
        
        if not new_observations:
            return {"status": "success", "message": "No new observations to add", "added": 0}
            
        entity.observations.extend(new_observations)
        save_graph(graph)
        
        return {
            "status": "success", 
            "message": f"Added {len(new_observations)} observations to '{entity.name}'", 
            "entityName": entity.name,
            "added": len(new_observations),
            "observations": new_observations
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def delete_entities(request: DeleteEntitiesRequest) -> Dict[str, Any]:
    """
    Delete entities and their associated relations.
    
    Provide a list of entityNames to delete from the knowledge graph.
    """
    try:
        graph = read_graph_file()
        # Convert to lowercase for case-insensitive matching
        entity_names_lower = {name.lower() for name in request.entityNames}
        
        # Get the original casing of entities that exist
        found_entities = [e.name for e in graph.entities if e.name.lower() in entity_names_lower]
        
        # Remove entities
        initial_count = len(graph.entities)
        graph.entities = [e for e in graph.entities if e.name.lower() not in entity_names_lower]
        deleted_count = initial_count - len(graph.entities)
        
        # Remove relations
        initial_rel_count = len(graph.relations)
        graph.relations = [
            r for r in graph.relations
            if r.from_.lower() not in entity_names_lower and r.to.lower() not in entity_names_lower
        ]
        deleted_rel_count = initial_rel_count - len(graph.relations)
        
        save_graph(graph)
        
        if deleted_count == 0:
            return {"status": "info", "message": "No entities found to delete"}
            
        return {
            "status": "success", 
            "message": f"Deleted {deleted_count} entities and {deleted_rel_count} relations", 
            "deletedEntities": found_entities,
            "deletedRelationsCount": deleted_rel_count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def delete_observations(request: DeleteObservationsRequest) -> Dict[str, Any]:
    """
    Delete specific observations from an entity.
    
    Specify the entityName and a list of observations to remove from that entity.
    """
    try:
        graph = read_graph_file()
        entity = find_entity_by_name(graph, request.entityName)
        
        if not entity:
            return {"status": "error", "message": f"Entity '{request.entityName}' not found"}
        
        initial_count = len(entity.observations)
        entity.observations = [
            obs for obs in entity.observations if obs not in request.observations
        ]
        deleted_count = initial_count - len(entity.observations)
        
        save_graph(graph)
        
        return {
            "status": "success", 
            "message": f"Deleted {deleted_count} observations from '{entity.name}'", 
            "entityName": entity.name,
            "deletedCount": deleted_count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def delete_relations(request: DeleteRelationsRequest) -> Dict[str, Any]:
    """
    Delete relations from the graph.
    
    Provide a list of relations to remove from the knowledge graph.
    """
    try:
        graph = read_graph_file()
        
        # Create a set of tuples for efficient lookup
        del_set = {(r.from_.lower(), r.to.lower(), r.relationType.lower()) 
                  for r in request.relations}
        
        initial_count = len(graph.relations)
        graph.relations = [
            r for r in graph.relations 
            if (r.from_.lower(), r.to.lower(), r.relationType.lower()) not in del_set
        ]
        deleted_count = initial_count - len(graph.relations)
        
        save_graph(graph)
        
        return {
            "status": "success", 
            "message": f"Deleted {deleted_count} relations", 
            "deletedCount": deleted_count
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def read_graph() -> Dict[str, Any]:
    """
    Read the entire knowledge graph.
    
    Returns all entities and relations currently in the graph.
    """
    try:
        graph = read_graph_file()
        return {
            "entities": [e.dict() for e in graph.entities],
            "relations": [r.dict() for r in graph.relations]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def search_nodes(request: SearchRequest) -> Dict[str, Any]:
    """
    Search for nodes by keyword.
    
    Provide a query string to search entity names, types, and observations.
    Returns matching entities and relations between them.
    """
    try:
        graph = read_graph_file()
        query = request.query.lower()
        
        if not query.strip():
            return {"status": "error", "message": "Search query cannot be empty"}
        
        entities = [
            e for e in graph.entities
            if query in e.name.lower()
            or query in e.entityType.lower()
            or any(query in o.lower() for o in e.observations)
        ]
        
        # Find relations between the matched entities
        entity_names_lower = {e.name.lower() for e in entities}
        relations = [
            r for r in graph.relations 
            if r.from_.lower() in entity_names_lower and r.to.lower() in entity_names_lower
        ]
        
        return {
            "status": "success",
            "matchCount": len(entities),
            "entities": [e.dict() for e in entities],
            "relations": [r.dict() for r in relations]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def open_nodes(request: OpenNodesRequest) -> Dict[str, Any]:
    """
    Open specific nodes by name.
    
    Provide a list of entity names to retrieve from the graph.
    Returns the specified entities and relations between them.
    """
    try:
        graph = read_graph_file()
        # Convert to lowercase for case-insensitive matching
        names_lower = {name.lower() for name in request.names}
        
        # Find entities with matching names (case-insensitive)
        entities = [e for e in graph.entities if e.name.lower() in names_lower]
        found_names_lower = {e.name.lower() for e in entities}
        
        # Find relations between these entities
        relations = [
            r for r in graph.relations 
            if r.from_.lower() in found_names_lower and r.to.lower() in found_names_lower
        ]
        
        # Check for entities that weren't found
        missing = [name for name in request.names if name.lower() not in found_names_lower]
        
        result = {
            "status": "success",
            "entities": [e.dict() for e in entities],
            "relations": [r.dict() for r in relations]
        }
        
        if missing:
            result["missing"] = missing
            result["message"] = f"Some entities were not found: {', '.join(missing)}"
        
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def get_graph_visualization(ctx: Context = None) -> Image:
    """
    Generate a visualization of the knowledge graph.
    
    Creates an image showing entities as nodes and relations as edges.
    """
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
        from matplotlib.figure import Figure
    except ImportError:
        return {"status": "error", "message": "Visualization libraries not available. Install matplotlib and networkx."}
    
    try:
        graph = read_graph_file()
        
        if not graph.entities:
            # Create a simple "empty graph" image
            fig = Figure(figsize=(8, 6), dpi=100)
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, "Empty Knowledge Graph", 
                   horizontalalignment='center', verticalalignment='center', 
                   transform=ax.transAxes, fontsize=14)
            ax.axis('off')
            buf = io.BytesIO()
            fig.savefig(buf, format='png')
            buf.seek(0)
            return Image(data=buf.getvalue(), format='png')
        
        # Create a networkx graph
        G = nx.DiGraph()
        
        # Add nodes with labels and attributes
        for entity in graph.entities:
            G.add_node(entity.name, type=entity.entityType, observations=entity.observations)
        
        # Add edges with labels
        for relation in graph.relations:
            G.add_edge(relation.from_, relation.to, relation_type=relation.relationType)
        
        # Create a figure and render the graph
        fig = Figure(figsize=(12, 8), dpi=100, tight_layout=True)
        ax = fig.add_subplot(111)
        
        # Draw nodes and edges
        pos = nx.spring_layout(G, seed=42)  # Fixed seed for consistent layouts
        
        # Find node types to color them differently
        node_types = set(nx.get_node_attributes(G, 'type').values())
        color_map = {}
        colors = plt.cm.tab10.colors
        for i, ntype in enumerate(node_types):
            color_map[ntype] = colors[i % len(colors)]
        
        # Assign colors based on node types
        node_colors = [color_map.get(G.nodes[node]['type'], 'lightgray') for node in G.nodes]
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_size=700, node_color=node_colors, alpha=0.8, ax=ax)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.7, arrowsize=15, ax=ax)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(G, 'relation_type')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
        
        # Add a legend for node types
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                  markerfacecolor=color, markersize=10, label=ntype)
                      for ntype, color in color_map.items()]
        ax.legend(handles=legend_elements, title="Entity Types", loc="upper right")
        
        # Remove axis
        ax.axis('off')
        
        # Title
        node_count = len(G.nodes)
        edge_count = len(G.edges)
        ax.set_title(f"Knowledge Graph: {node_count} nodes, {edge_count} edges")
        
        # Convert plot to image
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        
        # Return as Image
        return Image(data=buf.getvalue(), format='png')
    except Exception as e:
        return {"status": "error", "message": f"Failed to generate visualization: {str(e)}"}

@mcp.tool()
def get_statistics() -> Dict[str, Any]:
    """
    Get statistics about the knowledge graph.
    
    Returns counts of entities by type, total relations, etc.
    """
    try:
        graph = read_graph_file()
        
        # Count entities by type
        entity_types = {}
        for entity in graph.entities:
            entity_type = entity.entityType
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        
        # Count relation types
        relation_types = {}
        for relation in graph.relations:
            rel_type = relation.relationType
            relation_types[rel_type] = relation_types.get(rel_type, 0) + 1
        
        # Find most connected entities
        entity_connections = {}
        for relation in graph.relations:
            entity_connections[relation.from_] = entity_connections.get(relation.from_, 0) + 1
            entity_connections[relation.to] = entity_connections.get(relation.to, 0) + 1
        
        # Sort by number of connections
        most_connected = []
        if entity_connections:
            most_connected = sorted(entity_connections.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Count observations
        total_observations = sum(len(entity.observations) for entity in graph.entities)
        avg_observations = total_observations / len(graph.entities) if graph.entities else 0
        
        # Entities with most observations
        entities_with_observations = [(e.name, len(e.observations)) for e in graph.entities if e.observations]
        most_observed = sorted(entities_with_observations, key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "status": "success",
            "total_entities": len(graph.entities),
            "entity_types": entity_types,
            "total_relations": len(graph.relations),
            "relation_types": relation_types,
            "total_observations": total_observations,
            "avg_observations_per_entity": round(avg_observations, 2),
            "most_connected_entities": most_connected,
            "entities_with_most_observations": most_observed
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# NEW TOOLS

@mcp.tool()
def merge_entities(request: MergeEntitiesRequest) -> Dict[str, Any]:
    """
    Merge two entities, combining their observations and updating all relations.
    
    The source entity will be removed, and all its observations and relations
    will be transferred to the target entity.
    """
    try:
        graph = read_graph_file()
        source = find_entity_by_name(graph, request.sourceName)
        target = find_entity_by_name(graph, request.targetName)
        
        if not source:
            return {"status": "error", "message": f"Source entity '{request.sourceName}' not found"}
        
        if not target:
            return {"status": "error", "message": f"Target entity '{request.targetName}' not found"}
        
        if source.name.lower() == target.name.lower():
            return {"status": "error", "message": "Cannot merge an entity with itself"}
        
        source_name_lower = source.name.lower()
        target_name_lower = target.name.lower()
        
        # Merge observations
        new_observations = [o for o in source.observations if o not in target.observations]
        target.observations.extend(new_observations)
        
        # Update relations
        for relation in graph.relations:
            if relation.from_.lower() == source_name_lower:
                relation.from_ = target.name
            if relation.to.lower() == source_name_lower:
                relation.to = target.name
        
        # Remove duplicate relations that may have been created
        unique_relations = {}
        for r in graph.relations:
            key = (r.from_.lower(), r.to.lower(), r.relationType.lower())
            unique_relations[key] = r
        
        # Get counts for the report
        relations_before = len(graph.relations)
        relations_after = len(unique_relations)
        
        # Update graph relations
        graph.relations = list(unique_relations.values())
        
        # Remove source entity
        graph.entities = [e for e in graph.entities if e.name.lower() != source_name_lower]
        
        save_graph(graph)
        
        return {
            "status": "success",
            "message": f"Merged '{source.name}' into '{target.name}'",
            "sourceName": source.name,
            "targetName": target.name,
            "observationsMerged": len(new_observations),
            "relationsOptimized": relations_before - relations_after
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def export_graph(request: ExportGraphRequest) -> Dict[str, Any]:
    """
    Export the knowledge graph in various formats.
    
    Supported formats: json, csv, graphml
    """
    try:
        graph = read_graph_file()
        format_lower = request.format.lower()
        
        if format_lower == "json":
            return {
                "status": "success",
                "format": "json",
                "data": graph.json(indent=2)
            }
        
        elif format_lower == "csv":
            # Create CSV exports
            entities_csv = "id,name,type,observations\n"
            for i, e in enumerate(graph.entities):
                observations_str = "|".join(e.observations).replace(",", ";")
                entities_csv += f"{i},{e.name},{e.entityType},{observations_str}\n"
                
            relations_csv = "source,target,relation\n"
            for r in graph.relations:
                relations_csv += f"{r.from_},{r.to},{r.relationType}\n"
                
            return {
                "status": "success",
                "format": "csv",
                "entities_csv": entities_csv,
                "relations_csv": relations_csv
            }
        
        elif format_lower == "graphml":
            try:
                import networkx as nx
            except ImportError:
                return {"status": "error", "message": "NetworkX library not available for GraphML export"}
                
            # Create a NetworkX graph
            G = nx.DiGraph()
            
            # Add nodes with attributes
            for i, entity in enumerate(graph.entities):
                G.add_node(entity.name, 
                          id=i, 
                          type=entity.entityType, 
                          observations=";".join(entity.observations))
            
            # Add edges with attributes
            for relation in graph.relations:
                G.add_edge(relation.from_, relation.to, type=relation.relationType)
            
            # Create GraphML string
            graphml_io = io.StringIO()
            nx.write_graphml(G, graphml_io)
            
            return {
                "status": "success",
                "format": "graphml",
                "graphml": graphml_io.getvalue()
            }
        
        else:
            return {"status": "error", "message": f"Unsupported format: {request.format}"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def advanced_search(request: AdvancedSearchRequest) -> Dict[str, Any]:
    """
    Advanced search with multiple filters.
    
    Filter by entity type, relation type, minimum number of observations,
    and maximum number of relations.
    """
    try:
        graph = read_graph_file()
        
        # Filter entities by type
        filtered_entities = graph.entities
        if request.entityType:
            entity_type_lower = request.entityType.lower()
            filtered_entities = [e for e in filtered_entities 
                                if e.entityType.lower() == entity_type_lower]
        
        # Filter by observation count
        if request.minObservations is not None:
            filtered_entities = [e for e in filtered_entities 
                                if len(e.observations) >= request.minObservations]
        
        # Get entity names for relation filtering
        entity_names = {e.name.lower() for e in filtered_entities}
        
        # Filter relations
        filtered_relations = [r for r in graph.relations 
                             if r.from_.lower() in entity_names and r.to_.lower() in entity_names]
        
        # Filter by relation type
        if request.relationType:
            relation_type_lower = request.relationType.lower()
            filtered_relations = [r for r in filtered_relations 
                                 if r.relationType.lower() == relation_type_lower]
        
        # Calculate connection counts
        connection_counts = {}
        for relation in filtered_relations:
            connection_counts[relation.from_.lower()] = connection_counts.get(relation.from_.lower(), 0) + 1
            connection_counts[relation.to.lower()] = connection_counts.get(relation.to.lower(), 0) + 1
        
        # Filter by maximum number of relations if specified
        if request.maxRelations is not None:
            filtered_entity_names = {name for name, count in connection_counts.items() 
                                    if count <= request.maxRelations}
            filtered_entities = [e for e in filtered_entities 
                                if e.name.lower() in filtered_entity_names]
            
            # Update relations to match new filtered entities
            entity_names = {e.name.lower() for e in filtered_entities}
            filtered_relations = [r for r in filtered_relations 
                                 if r.from_.lower() in entity_names and r.to.lower() in entity_names]
        
        return {
            "status": "success",
            "entityCount": len(filtered_entities),
            "relationCount": len(filtered_relations),
            "entities": [e.dict() for e in filtered_entities],
            "relations": [r.dict() for r in filtered_relations]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def generate_report() -> Dict[str, Any]:
    """
    Generate a comprehensive report about the knowledge graph.
    
    Includes statistics, most important entities and relationships,
    and recommendations for improving the graph.
    """
    try:
        graph = read_graph_file()
        
        if not graph.entities:
            return {
                "status": "info",
                "message": "The knowledge graph is empty. Add some entities and relations to generate a report."
            }
        
        # Basic statistics
        entity_count = len(graph.entities)
        relation_count = len(graph.relations)
        
        # Entity types
        entity_types = {}
        for entity in graph.entities:
            entity_types[entity.entityType] = entity_types.get(entity.entityType, 0) + 1
        
        # Relation types
        relation_types = {}
        for relation in graph.relations:
            relation_types[relation.relationType] = relation_types.get(relation.relationType, 0) + 1
        
        # Connection statistics
        from_counts = {}
        to_counts = {}
        total_connections = {}
        
        for relation in graph.relations:
            from_name = relation.from_.lower()
            to_name = relation.to_.lower()
            
            from_counts[from_name] = from_counts.get(from_name, 0) + 1
            to_counts[to_name] = to_counts.get(to_name, 0) + 1
            total_connections[from_name] = total_connections.get(from_name, 0) + 1
            total_connections[to_name] = total_connections.get(to_name, 0) + 1
        
        # Identify key entities (highest connections)
        key_entities = []
        if total_connections:
            key_entities = sorted(total_connections.items(), key=lambda x: x[1], reverse=True)[:10]
            key_entities = [(find_entity_by_name(graph, name).name, count) for name, count in key_entities]
        
        # Identify isolated entities (no connections)
        isolated_entities = [e.name for e in graph.entities if e.name.lower() not in total_connections]
        
        # Entities with no observations
        no_observations = [e.name for e in graph.entities if not e.observations]
        
        # Calculate graph density
        max_relations = entity_count * (entity_count - 1)  # Maximum possible in a directed graph
        density = relation_count / max_relations if max_relations > 0 else 0
        
        # Generate recommendations
        recommendations = []
        
        if isolated_entities:
            recommendations.append(f"Connect isolated entities: {', '.join(isolated_entities[:5])}" + 
                                  (f" and {len(isolated_entities) - 5} more" if len(isolated_entities) > 5 else ""))
        
        if no_observations:
            recommendations.append(f"Add observations to entities: {', '.join(no_observations[:5])}" + 
                                  (f" and {len(no_observations) - 5} more" if len(no_observations) > 5 else ""))
        
        if density < 0.1 and entity_count > 5:
            recommendations.append("The graph is sparse. Consider adding more relationships between entities.")
        
        if len(relation_types) < 3 and relation_count > 10:
            recommendations.append("Consider using more diverse relationship types to better describe connections.")
        
        return {
            "status": "success",
            "summary": {
                "entities": entity_count,
                "relations": relation_count,
                "entityTypes": entity_types,
                "relationTypes": relation_types,
                "graphDensity": round(density, 4)
            },
            "keyEntities": key_entities,
            "isolatedEntities": isolated_entities,
            "entitiesWithoutObservations": no_observations,
            "recommendations": recommendations
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def find_paths(source: str, target: str, max_length: int = 3) -> Dict[str, Any]:
    """
    Find paths between two entities in the graph.
    
    Identifies all paths up to the specified maximum length (default: 3)
    between the source and target entities.
    """
    try:
        import networkx as nx
    except ImportError:
        return {"status": "error", "message": "NetworkX library not available for path finding"}
    
    try:
        graph = read_graph_file()
        
        source_entity = find_entity_by_name(graph, source)
        target_entity = find_entity_by_name(graph, target)
        
        if not source_entity:
            return {"status": "error", "message": f"Source entity '{source}' not found"}
        
        if not target_entity:
            return {"status": "error", "message": f"Target entity '{target}' not found"}
        
        # Build a NetworkX graph
        G = nx.DiGraph()
        
        # Add nodes
        for entity in graph.entities:
            G.add_node(entity.name)
        
        # Add edges with attributes
        for relation in graph.relations:
            G.add_edge(relation.from_, relation.to, relation_type=relation.relationType)
        
        # Find all simple paths up to max_length
        paths = []
        try:
            for path in nx.all_simple_paths(G, source=source_entity.name, target=target_entity.name, cutoff=max_length):
                # Get the relations for each step in the path
                path_relations = []
                for i in range(len(path) - 1):
                    from_node = path[i]
                    to_node = path[i + 1]
                    # Find the relation between these nodes
                    rel_type = G.get_edge_data(from_node, to_node)['relation_type']
                    path_relations.append(rel_type)
                
                paths.append({
                    "nodes": path,
                    "relations": path_relations,
                    "length": len(path) - 1
                })
        except nx.NetworkXNoPath:
            pass  # No path exists
        
        if not paths:
            return {
                "status": "info",
                "message": f"No paths found between '{source_entity.name}' and '{target_entity.name}' within {max_length} steps"
            }
        
        return {
            "status": "success",
            "source": source_entity.name,
            "target": target_entity.name,
            "pathsFound": len(paths),
            "paths": paths
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def detect_clusters() -> Dict[str, Any]:
    """
    Detect clusters or communities in the knowledge graph.
    
    Uses community detection algorithms to identify groups of closely related entities.
    """
    try:
        import networkx as nx
        import community as community_louvain
    except ImportError:
        return {
            "status": "error", 
            "message": "Required libraries not available. Install networkx and python-louvain."
        }
    
    try:
        graph = read_graph_file()
        
        if len(graph.entities) < 3:
            return {
                "status": "info",
                "message": "Not enough entities to detect meaningful clusters (minimum 3 required)."
            }
        
        # Create an undirected graph for community detection
        G = nx.Graph()
        
        # Add nodes
        for entity in graph.entities:
            G.add_node(entity.name, type=entity.entityType)
        
        # Add edges (undirected)
        for relation in graph.relations:
            G.add_edge(relation.from_, relation.to, relation_type=relation.relationType)
        
        if not G.edges:
            return {
                "status": "info",
                "message": "No relationships between entities. Cannot detect clusters."
            }
        
        # Detect communities using Louvain method
        partition = community_louvain.best_partition(G)
        
        # Organize entities by community
        communities = {}
        for node, community_id in partition.items():
            if community_id not in communities:
                communities[community_id] = []
            communities[community_id].append(node)
        
        # Format results
        clusters = []
        for community_id, members in communities.items():
            # Find the most common entity type in this cluster
            entity_types = {}
            for member in members:
                entity = find_entity_by_name(graph, member)
                if entity:
                    entity_types[entity.entityType] = entity_types.get(entity.entityType, 0) + 1
            
            dominant_type = max(entity_types.items(), key=lambda x: x[1])[0] if entity_types else "Unknown"
            
            clusters.append({
                "id": community_id,
                "size": len(members),
                "dominantType": dominant_type,
                "members": members
            })
        
        # Sort clusters by size
        clusters.sort(key=lambda x: x["size"], reverse=True)
        
        return {
            "status": "success",
            "clusterCount": len(clusters),
            "clusters": clusters
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def suggest_relations() -> Dict[str, Any]:
    """
    Suggest potential new relations between entities.
    
    Analyzes the graph structure to find entities that might be related
    but don't have direct connections yet.
    """
    try:
        import networkx as nx
    except ImportError:
        return {"status": "error", "message": "NetworkX library not available for relation suggestions"}
    
    try:
        graph = read_graph_file()
        
        if len(graph.entities) < 3:
            return {
                "status": "info",
                "message": "Not enough entities to suggest meaningful relations (minimum 3 required)."
            }
        
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes
        entity_types = {}
        for entity in graph.entities:
            G.add_node(entity.name)
            entity_types[entity.name] = entity.entityType
        
        # Add existing edges
        existing_relations = set()
        for relation in graph.relations:
            G.add_edge(relation.from_, relation.to)
            existing_relations.add((relation.from_, relation.to))
        
        # Suggestions based on common neighbors (triangles)
        suggestions = []
        
        # For each pair of nodes not directly connected
        for source in G.nodes():
            for target in G.nodes():
                if source != target and (source, target) not in existing_relations:
                    # Get common neighbors
                    source_neighbors = set(G.successors(source)).union(set(G.predecessors(source)))
                    target_neighbors = set(G.successors(target)).union(set(G.predecessors(target)))
                    common = source_neighbors.intersection(target_neighbors)
                    
                    if common:
                        suggestions.append({
                            "source": source,
                            "sourceType": entity_types.get(source),
                            "target": target,
                            "targetType": entity_types.get(target),
                            "commonConnections": list(common),
                            "strength": len(common)
                        })
        
        # Sort by suggestion strength
        suggestions.sort(key=lambda x: x["strength"], reverse=True)
        
        # Take the top 10 suggestions
        top_suggestions = suggestions[:10]
        
        if not top_suggestions:
            return {
                "status": "info",
                "message": "No relation suggestions found. Try adding more entities and connections first."
            }
        
        return {
            "status": "success",
            "suggestionCount": len(top_suggestions),
            "suggestions": top_suggestions
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def backup_graph() -> Dict[str, Any]:
    """
    Create a backup of the current knowledge graph.
    
    Creates a timestamped backup file in the backup directory.
    """
    try:
        graph = read_graph_file()
        
        # Generate backup path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        home_dir = Path.home()
        backup_dir = home_dir / ".knowledge_graph" / "backups"
        backup_dir.mkdir(exist_ok=True, parents=True)
        backup_path = backup_dir / f"graph_backup_{timestamp}.json"
        
        # Save backup
        with open(backup_path, "w") as f:
            f.write(graph.json(indent=2, exclude={'_name_index'}))
        
        # List existing backups
        backups = sorted(list(backup_dir.glob("*.json")))
        
        return {
            "status": "success",
            "message": f"Backup created successfully at {backup_path}",
            "backupPath": str(backup_path),
            "timestamp": timestamp,
            "entityCount": len(graph.entities),
            "relationCount": len(graph.relations),
            "existingBackups": len(backups)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def restore_graph(backup_file: str = None) -> Dict[str, Any]:
    """
    Restore the knowledge graph from a backup.

    If no backup file is specified, restores from the most recent backup.
    """
    try:
        home_dir = Path.home()
        backup_dir = home_dir / ".knowledge_graph" / "backups"

        if not backup_dir.exists() or not list(backup_dir.glob("*.json")):
            return {"status": "error", "message": "No backups found"}

        # Find the backup to restore
        if backup_file:
            backup_path = backup_dir / backup_file
            if not backup_path.exists():
                return {"status": "error", "message": f"Backup file '{backup_file}' not found"}
        else:
            # Get the most recent backup
            backups = sorted(list(backup_dir.glob("*.json")))
            if not backups:
                return {"status": "error", "message": "No backups found"}
            backup_path = backups[-1]

        # Read the backup
        with open(backup_path, "r") as f:
            backup_data = json.load(f)

        # Parse and validate
        backup_graph = KnowledgeGraph.parse_obj(backup_data)

        # Back up the current graph before replacing
        current_graph = read_graph_file()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        current_backup_path = backup_dir / f"pre_restore_{timestamp}.json"
        with open(current_backup_path, "w") as f:
            f.write(current_graph.json(indent=2, exclude={'_name_index'}))

        # Save the restored graph
        save_graph(backup_graph)

        return {
            "status": "success",
            "message": f"Graph restored from backup: {backup_path.name}",
            "entityCount": len(backup_graph.entities),
            "relationCount": len(backup_graph.relations),
            "originalBackup": str(backup_path),
            "previousStateSaved": str(current_backup_path)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def generate_html_visualization() -> Dict[str, Any]:
    """
    Generate an interactive HTML visualization of the knowledge graph.

    Creates a self-contained HTML file with D3.js for interactive graph exploration.
    Features include zoom, pan, drag nodes, click to view details, and smooth navigation.
    """
    try:
        graph = read_graph_file()

        if not graph.entities:
            return {
                "status": "info",
                "message": "The knowledge graph is empty. Add some entities and relations first."
            }

        # Get the graph file path to determine where to save the HTML
        graph_file_path = get_graph_file_path()

        # Use the internal function to generate the HTML
        _generate_html_visualization_internal(graph, graph_file_path)

        html_file_path = graph_file_path.parent / "graph_visualization.html"
        entity_types = list(set(entity.entityType for entity in graph.entities))

        return {
            "status": "success",
            "message": f"Interactive HTML visualization created successfully",
            "htmlPath": str(html_file_path),
            "entityCount": len(graph.entities),
            "relationCount": len(graph.relations),
            "entityTypes": len(entity_types),
            "openCommand": f"Open {html_file_path} in your web browser to view the interactive visualization"
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to generate HTML visualization: {str(e)}"}

if __name__ == "__main__":
    mcp.run()