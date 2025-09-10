#!/bin/bash
# Knowledge Graph MCP Server Startup Script for Linux

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment and run the server
echo "Starting Knowledge Graph MCP Server..."
echo "Data will be stored in: ~/.knowledge_graph/"
echo "----------------------------------------"

# Use the virtual environment's Python to run the server
"$SCRIPT_DIR/venv-kgmcp/bin/python" "$SCRIPT_DIR/knowledge_graph_mcp.py"