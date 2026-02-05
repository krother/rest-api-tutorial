#!/usr/bin/env python3
"""Simple terminal chat for the Favorite Colors MCP server.

Demonstrates direct API calls with tool use - minimal example.

Usage:
    uv run python simple_chat.py
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

if not ANTHROPIC_API_KEY:
    print("Error: ANTHROPIC_API_KEY not set in .env file")
    exit(1)

# Initialize Anthropic client
client_kwargs = {"api_key": ANTHROPIC_API_KEY}
if ANTHROPIC_BASE_URL:
    client_kwargs["base_url"] = ANTHROPIC_BASE_URL
anthropic = Anthropic(**client_kwargs)

print(f"Using model: {ANTHROPIC_MODEL}")
print("-" * 50)

# The same data as in server_simple.py
FAVORITE_COLORS = {
    "Alice": "blue",
    "Bob": "green",
    "Charlie": "purple",
    "Diana": "orange",
    "Eve": "red",
}

# Define tools for Claude
TOOLS = [
    {
        "name": "get_favorite_color",
        "description": "Look up someone's favorite color from our database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The person's name to look up"
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "list_participants",
        "description": "List all participants whose favorite colors we know.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]


def execute_tool(name: str, arguments: dict) -> str:
    """Execute a tool and return the result."""
    
    if name == "get_favorite_color":
        person_name = arguments.get("name", "")
        for key, color in FAVORITE_COLORS.items():
            if key.lower() == person_name.lower():
                return f"{key}'s favorite color is {color}."
        available = ", ".join(FAVORITE_COLORS.keys())
        return f"I don't have {person_name}'s favorite color. I know about: {available}"
    
    elif name == "list_participants":
        lines = ["Registered participants:"]
        for name, color in FAVORITE_COLORS.items():
            lines.append(f"  - {name}: {color}")
        return "\n".join(lines)
    
    return f"Unknown tool: {name}"


def chat(user_message: str, conversation_history: list) -> str:
    """Send a message to Claude and handle tool calls."""
    
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    response = anthropic.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        system="You are a helpful assistant. Use the tools to look up participant information when asked.",
        tools=TOOLS,
        messages=conversation_history
    )
    
    # Handle tool use loop
    while response.stop_reason == "tool_use":
        tool_calls = [block for block in response.content if block.type == "tool_use"]
        
        conversation_history.append({
            "role": "assistant",
            "content": response.content
        })
        
        tool_results = []
        for tool_call in tool_calls:
            print(f"  [Calling: {tool_call.name}({tool_call.input})]")
            result = execute_tool(tool_call.name, tool_call.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": result
            })
        
        conversation_history.append({
            "role": "user",
            "content": tool_results
        })
        
        response = anthropic.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            system="You are a helpful assistant. Use the tools to look up participant information when asked.",
            tools=TOOLS,
            messages=conversation_history
        )
    
    final_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            final_text += block.text
    
    conversation_history.append({
        "role": "assistant",
        "content": response.content
    })
    
    return final_text


def main():
    print("\n🎨 Favorite Colors Chat")
    print("Type 'quit' to exit\n")
    
    conversation_history = []
    
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        
        try:
            response = chat(user_input, conversation_history)
            print(f"\nAssistant: {response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
