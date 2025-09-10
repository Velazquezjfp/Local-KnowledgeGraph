#!/usr/bin/env python3
"""
Test script for Knowledge Graph MCP
This tests the core functionality without requiring Claude Desktop
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_graph_mcp import (
    CreateEntitiesRequest, 
    CreateRelationsRequest,
    SearchRequest,
    Entity, 
    Relation,
    create_entities,
    create_relations,
    read_graph,
    search_nodes,
    get_statistics,
    get_graph_file_path
)

def test_knowledge_graph():
    print("Testing Knowledge Graph MCP Server...")
    print(f"Data will be stored at: {get_graph_file_path()}")
    print("-" * 50)
    
    # Test 1: Create entities
    print("\n1. Creating test entities...")
    entities_request = CreateEntitiesRequest(entities=[
        Entity(name="Python", entityType="language", observations=["High-level", "Dynamic typing"]),
        Entity(name="FastMCP", entityType="library", observations=["MCP framework", "Python-based"]),
        Entity(name="Knowledge Graph", entityType="system", observations=["Graph database", "Entity relationships"])
    ])
    result = create_entities(entities_request)
    print(f"   Result: {result['status']} - {result['message']}")
    
    # Test 2: Create relations
    print("\n2. Creating relations...")
    relations_request = CreateRelationsRequest(relations=[
        Relation(from_="FastMCP", to="Python", relationType="written_in"),
        Relation(from_="Knowledge Graph", to="FastMCP", relationType="uses")
    ])
    result = create_relations(relations_request)
    print(f"   Result: {result['status']} - {result['message']}")
    
    # Test 3: Read the graph
    print("\n3. Reading the entire graph...")
    graph = read_graph()
    print(f"   Entities: {len(graph['entities'])}")
    print(f"   Relations: {len(graph['relations'])}")
    
    # Test 4: Search functionality
    print("\n4. Testing search...")
    search_request = SearchRequest(query="Python")
    result = search_nodes(search_request)
    print(f"   Found {result['matchCount']} matches for 'Python'")
    
    # Test 5: Get statistics
    print("\n5. Getting statistics...")
    stats = get_statistics()
    print(f"   Total entities: {stats['total_entities']}")
    print(f"   Total relations: {stats['total_relations']}")
    print(f"   Entity types: {stats['entity_types']}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")
    print(f"Graph data stored at: {get_graph_file_path()}")
    
if __name__ == "__main__":
    test_knowledge_graph()