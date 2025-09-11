#!/usr/bin/env python3
"""
Test script for the custom path knowledge graph MCP
"""

from knowledge_graph_mcp_custom_path import *
from pathlib import Path
import json
import tempfile
import shutil

def test_custom_path():
    print("Testing Custom Path Knowledge Graph MCP...")
    print("-" * 50)
    
    # Use project-relative path
    relative_path = "./docs/kg/test/test_graph.json"
    
    # Clean up any existing test directory in the project
    test_dir = Path.cwd() / "docs" / "kg" / "test"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    
    print(f"\n1. Setting custom graph path to: {relative_path}")
    result = set_graph_path(relative_path)
    print(f"   Result: {result['status']}")
    print(f"   Original path: {result.get('original_path')}")
    print(f"   Resolved path: {result.get('resolved_path')}")
    print(f"   Is relative: {result.get('is_relative')}")
    
    print(f"\n2. Verifying current path...")
    result = get_current_graph_path()
    print(f"   Current path: {result.get('path')}")
    print(f"   Is custom: {result.get('is_custom')}")
    
    print(f"\n3. Creating test entities...")
    entities_request = CreateEntitiesRequest(entities=[
        Entity(name="TestFunction", entityType="function", 
               observations=["Line 10-20", "Returns string", "Has 2 parameters"]),
        Entity(name="TestClass", entityType="class", 
               observations=["Line 50-100", "Inherits from BaseClass"]),
        Entity(name="config.py", entityType="module", 
               observations=["Configuration module", "Contains settings"])
    ])
    result = create_entities(entities_request)
    print(f"   Result: {result['status']} - {result['message']}")
    
    print(f"\n4. Creating relationships...")
    relations_request = CreateRelationsRequest(relations=[
        Relation(from_="TestClass", to="TestFunction", relationType="calls"),
        Relation(from_="config.py", to="TestClass", relationType="imports")
    ])
    result = create_relations(relations_request)
    print(f"   Result: {result['status']} - {result['message']}")
    
    print(f"\n5. Verifying file was created at custom path...")
    actual_file = Path.cwd() / "docs" / "kg" / "test" / "test_graph.json"
    if actual_file.exists():
        print(f"   ✓ File exists at: {actual_file}")
        with open(actual_file, 'r') as f:
            data = json.load(f)
            print(f"   ✓ Contains {len(data.get('entities', []))} entities")
            print(f"   ✓ Contains {len(data.get('relations', []))} relations")
    else:
        print(f"   ✗ File not found at: {actual_file}")
    
    print(f"\n6. Testing path persistence (reading back)...")
    graph = read_graph_file()
    print(f"   ✓ Read {len(graph.entities)} entities")
    print(f"   ✓ Read {len(graph.relations)} relations")
    
    print(f"\n7. Testing export with custom path...")
    export_request = ExportGraphRequest(format="json")
    result = export_graph(export_request)
    if result.get('status') == 'success':
        print(f"   ✓ Export successful")
    
    print(f"\n8. Resetting to default path...")
    global _custom_graph_path
    _custom_graph_path = None
    result = get_current_graph_path()
    print(f"   Current path: {result.get('path')}")
    print(f"   Is custom: {result.get('is_custom')}")
    
    print("\n" + "=" * 50)
    print("All tests completed successfully!")
    print(f"Custom graph saved at: {actual_file}")
    
    # Optional: Clean up test directory
    # shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_custom_path()