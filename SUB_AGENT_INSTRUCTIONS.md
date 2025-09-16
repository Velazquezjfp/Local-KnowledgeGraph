# Sub-Agent Instructions for Auto-Visualization

## What's Changed

✅ **Auto-HTML Generation**: Every knowledge graph now automatically gets an interactive HTML visualization when saved!

## How It Works

1. **Sub-agent builds code graph** using the custom path MCP
2. **HTML visualization is automatically created** alongside the JSON graph
3. **Both files are saved** in the same directory:
   - `code-graph.json` (or `clean_analysis.json`)
   - `graph_visualization.html` ← **NEW: Interactive visualization**

## For Your Two Graph Types

**1. code-graph.json** (High-level architectural)
- Gets `graph_visualization.html` showing module relationships
- Perfect for understanding overall architecture

**2. clean_analysis.json** (Detailed granular analysis)
- Gets `graph_visualization.html` showing every config key, function, class
- Perfect for diving deep into implementation details

## Sub-Agent Instructions

Simply continue using the MCP as before:

```
1. Set custom path: set_graph_path("./code-graph.json")
2. Create entities and relations as normal
3. 🎉 HTML visualization automatically created!
```

## Features Available in HTML

- **Zoom & Pan**: Mouse wheel + drag
- **Interactive nodes**: Hover for details, click to center
- **Drag nodes**: Reposition elements
- **Controls**: Adjust node size, link distance
- **Color coding**: Different entity types
- **Tooltips**: Show observations and details
- **Auto-layout**: Force-directed positioning

## No Extra Steps Needed!

The visualization happens automatically whenever the graph is saved. Just open the HTML file in any browser to explore your knowledge graph interactively.