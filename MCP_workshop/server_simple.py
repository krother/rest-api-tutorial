#!/usr/bin/env python3
"""Minimal MCP server example - Favorite Colors.

This demonstrates MCP's power with the simplest possible example:
a dictionary of data the model cannot know without calling the tool.

Usage:
    uv run python server_simple.py
"""

import os
from fastmcp import FastMCP

mcp = FastMCP("Favorite Colors")

# Data the model can't know without MCP!
FAVORITE_COLORS = {
    "Kristian": "green",
    "Alex": "blue",
    "Majid": "blue (but doesn't matter)",
    "Jonah": "purple",
    "Ben": "black",
    "Paulthi": "yellow",
    "Denise": "blue",
    "Paschalia": "green",
    "Iheb": "dark blue",   
}


@mcp.tool
def get_favorite_color(name: str) -> str:
    """Look up someone's favorite color.
    
    Args:
        name: The person's name to look up
    """
    for key, color in FAVORITE_COLORS.items():
        if key.lower() == name.lower():
            return f"{key}'s favorite color is {color}."
    
    available = ", ".join(FAVORITE_COLORS.keys())
    return f"I don't have {name}'s favorite color. I know about: {available}"


@mcp.tool
def list_participants() -> str:
    """List all participants whose favorite colors we know."""
    if not FAVORITE_COLORS:
        return "No participants registered yet."
    
    lines = ["Registered participants:"]
    for name, color in FAVORITE_COLORS.items():
        lines.append(f"  - {name}: {color}")
    return "\n".join(lines)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    if transport == "sse":
        host = os.getenv("MCP_HOST", "0.0.0.0")
        port = int(os.getenv("MCP_PORT", "9001"))
        mcp.run(transport="sse", host=host, port=port)
    else:
        mcp.run(transport="stdio")
