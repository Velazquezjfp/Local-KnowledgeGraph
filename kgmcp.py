from mcp.server.fastmcp import FastMCP, Context, Image
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import json
from pathlib import Path
import io
import click
import uvicorn

# Define our data models
class Entity(BaseModel):
    name: str
    entityType: str
    observations: List[str] = Field(default_factory=list)

class Relation(BaseModel):
    from_: str
    to: str
    relationType: str

class KnowledgeGraph(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    relations: List[Relation] = Field(default_factory=list)

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

# Create MCP server
mcp = FastMCP("Knowledge Graph")

# File operations for persistence
def get_graph_file_path():
    # Store graph in user's home directory in a hidden folder
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
            return KnowledgeGraph.parse_obj(data)
        except (json.JSONDecodeError, ValueError):
            return KnowledgeGraph()

def save_graph(graph: KnowledgeGraph):
    with open(get_graph_file_path(), "w") as f:
        f.write(graph.json(indent=2))

# MCP tools

@mcp.tool()
def create_entities(request: CreateEntitiesRequest) -> List[Entity]:
    """
    Create multiple entities in the graph.
    
    Provide a list of entities to add to the knowledge graph.
    Each entity needs a name, entityType, and optional observations.
    """
    graph = read_graph_file()
    existing_names = {e.name.lower() for e in graph.entities}
    
    # Convert all entity names to lowercase for case-insensitive matching
    for entity in request.entities:
        entity.name = entity.name.lower()
    
    new_entities = [e for e in request.entities if e.name not in existing_names]
    graph.entities.extend(new_entities)
    save_graph(graph)
    return new_entities

@mcp.tool()
def create_relations(request: CreateRelationsRequest) -> List[Relation]:
    """
    Create multiple relations between entities.
    
    Provide a list of relations to add to the knowledge graph.
    Each relation consists of from_ (source entity), to (target entity), 
    and relationType (how they are related).
    """
    graph = read_graph_file()
    
    # Convert entity names to lowercase
    for relation in request.relations:
        relation.from_ = relation.from_.lower()
        relation.to = relation.to.lower()
    
    # Check that all entities exist
    entity_names = {e.name for e in graph.entities}
    for relation in request.relations:
        if relation.from_ not in entity_names:
            return [{"error": f"Source entity {relation.from_} not found"}]
        if relation.to not in entity_names:
            return [{"error": f"Target entity {relation.to} not found"}]
    
    # Add new relations
    existing = {(r.from_, r.to, r.relationType) for r in graph.relations}
    new = [r for r in request.relations if (r.from_, r.to, r.relationType) not in existing]
    graph.relations.extend(new)
    save_graph(graph)
    return new

@mcp.tool()
def add_observations(request: AddObservationsRequest) -> Dict[str, Any]:
    """
    Add new observations to an existing entity.
    
    Specify the entityName and a list of observations to add to that entity.
    """
    graph = read_graph_file()
    name = request.entityName.lower()
    entity = next((e for e in graph.entities if e.name == name), None)
    if not entity:
        return {"error": f"Entity {name} not found"}
    
    added = [c for c in request.observations if c not in entity.observations]
    entity.observations.extend(added)
    save_graph(graph)
    return {"entityName": name, "addedObservations": added}

@mcp.tool()
def delete_entities(request: DeleteEntitiesRequest) -> Dict[str, str]:
    """
    Delete entities and their associated relations.
    
    Provide a list of entityNames to delete from the knowledge graph.
    """
    graph = read_graph_file()
    # Convert to lowercase for case-insensitive matching
    entity_names = [name.lower() for name in request.entityNames]
    
    graph.entities = [e for e in graph.entities if e.name not in entity_names]
    graph.relations = [
        r
        for r in graph.relations
        if r.from_ not in entity_names and r.to not in entity_names
    ]
    save_graph(graph)
    return {"message": f"Entities deleted successfully"}

@mcp.tool()
def delete_observations(request: DeleteObservationsRequest) -> Dict[str, str]:
    """
    Delete specific observations from an entity.
    
    Specify the entityName and a list of observations to remove from that entity.
    """
    graph = read_graph_file()
    name = request.entityName.lower()
    entity = next((e for e in graph.entities if e.name == name), None)
    if not entity:
        return {"error": f"Entity {name} not found"}
    
    entity.observations = [
        obs for obs in entity.observations if obs not in request.observations
    ]
    save_graph(graph)
    return {"message": f"Observations deleted from {name} successfully"}

@mcp.tool()
def delete_relations(request: DeleteRelationsRequest) -> Dict[str, str]:
    """
    Delete relations from the graph.
    
    Provide a list of relations to remove from the knowledge graph.
    """
    graph = read_graph_file()
    
    # Convert to lowercase for case-insensitive matching
    for relation in request.relations:
        relation.from_ = relation.from_.lower()
        relation.to = relation.to.lower()
    
    del_set = {(r.from_, r.to, r.relationType) for r in request.relations}
    graph.relations = [
        r for r in graph.relations if (r.from_, r.to, r.relationType) not in del_set
    ]
    save_graph(graph)
    return {"message": "Relations deleted successfully"}

@mcp.tool()
def read_graph() -> KnowledgeGraph:
    """
    Read the entire knowledge graph.
    
    Returns all entities and relations currently in the graph.
    """
    return read_graph_file()

@mcp.tool()
def search_nodes(request: SearchRequest) -> KnowledgeGraph:
    """
    Search for nodes by keyword.
    
    Provide a query string to search entity names, types, and observations.
    Returns matching entities and relations between them.
    """
    graph = read_graph_file()
    query = request.query.lower()
    
    entities = [
        e
        for e in graph.entities
        if query in e.name.lower()
        or query in e.entityType.lower()
        or any(query in o.lower() for o in e.observations)
    ]
    names = {e.name for e in entities}
    relations = [r for r in graph.relations if r.from_ in names and r.to in names]

    return KnowledgeGraph(entities=entities, relations=relations)

@mcp.tool()
def open_nodes(request: OpenNodesRequest) -> KnowledgeGraph:
    """
    Open specific nodes by name.
    
    Provide a list of entity names to retrieve from the graph.
    Returns the specified entities and relations between them.
    """
    graph = read_graph_file()
    # Convert to lowercase for case-insensitive matching
    names = [name.lower() for name in request.names]
    
    entities = [e for e in graph.entities if e.name in names]
    names_set = {e.name for e in entities}
    relations = [r for r in graph.relations if r.from_ in names_set and r.to in names_set]
    return KnowledgeGraph(entities=entities, relations=relations)

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
        return {"error": "Visualization libraries not available. Install matplotlib and networkx."}
    
    graph = read_graph_file()
    
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
    pos = nx.spring_layout(G)
    
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
    edge_labels = {(relation.from_, relation.to): relation.relationType for relation in graph.relations}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, ax=ax)
    
    # Add a legend for node types
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                              markerfacecolor=color, markersize=10, label=ntype)
                  for ntype, color in color_map.items()]
    ax.legend(handles=legend_elements, title="Entity Types", loc="upper right")
    
    # Remove axis
    ax.axis('off')
    
    # Title
    ax.set_title("Knowledge Graph Visualization")
    
    # Convert plot to image
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    # Return as Image
    return Image(data=buf.getvalue(), format='png')

@mcp.tool()
def get_statistics() -> Dict[str, Any]:
    """
    Get statistics about the knowledge graph.
    
    Returns counts of entities by type, total relations, etc.
    """
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
    
    # Count observations
    total_observations = sum(len(entity.observations) for entity in graph.entities)
    
    return {
        "total_entities": len(graph.entities),
        "entity_types": entity_types,
        "total_relations": len(graph.relations),
        "relation_types": relation_types,
        "total_observations": total_observations
    }

@click.command()
@click.option("--port", default=8000, help="Port to listen on for SSE")
def main(port: int):
    """Run the Knowledge Graph MCP server with SSE transport."""
    print(f"Starting Knowledge Graph MCP server on port {port}...")
    print(f"To connect, run: mcp connect http://localhost:{port}/sse")
    uvicorn.run(
        mcp.sse_app(route="/sse", message_path="/messages"),
        host="0.0.0.0",
        port=port
    )

if __name__ == "__main__":
    main()