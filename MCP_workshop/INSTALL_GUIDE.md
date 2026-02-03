# MCP Workshop - Installation Guide

> **Important**: Open the `MCP_workshop` folder as your workspace root. Don't open the parent folder.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- **macOS**: Cursor IDE
- **Windows**: VSCode with GitHub Copilot

---

## macOS Installation (Cursor)

### Step 1: Open the correct folder

Open **only** the `MCP_workshop` folder in Cursor (not the parent folder):

```bash
cd MCP_workshop
cursor .
```

### Step 2: Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` and fill in your Anthropic API key (optional - only needed for `search_cats_summarized` and `chat.py`):

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### Step 3: Install dependencies

```bash
uv sync
```

This installs all Python dependencies including FastMCP, ChromaDB, and sentence-transformers.

### Step 4: Configure MCP in Cursor

Create `.cursor/mcp.json` in your workspace root:

```bash
mkdir -p .cursor
```

Create the file `.cursor/mcp.json` with this content:

```json
{
  "mcpServers": {
    "cats-rag": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### Step 5: Reload Cursor

Press `Cmd+Shift+P` → type "Developer: Reload Window" → Enter

### Step 6: Verify MCP is running

Go to **Cursor Settings → MCP**, check that "cats-rag" shows **green status**.

### Step 7: Ingest data and test

```bash
uv run python ingest.py cats_demo.txt
```

Then ask the AI: *"Use cats-rag to search for cat hunting behavior"*

---

## Windows Installation (VSCode)

### Step 1: Install uv

Open PowerShell and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Restart your terminal** after installation to pick up the PATH.

### Step 2: Open the correct folder

Open **only** the `MCP_workshop` folder in VSCode:

```powershell
cd MCP_workshop
code .
```

### Step 3: Create your `.env` file

```powershell
copy .env.example .env
```

Edit `.env` and fill in your Anthropic API key (optional - only needed for `search_cats_summarized` and `chat.py`):

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### Step 4: Install dependencies

```powershell
uv sync
```

### Step 5: Verify MCP configuration

The `.vscode/mcp.json` file is already included:

```json
{
  "mcpServers": {
    "cats-rag": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### Step 6: Enable MCP in VSCode Settings

1. Open Settings: `Ctrl+,`
2. Search for `chat.mcp`
3. Make sure **"Chat > Mcp: Autostart"** is set to `newAndOutdated` or `always`

### Step 7: Reload VSCode

Press `Ctrl+Shift+P` → type "Developer: Reload Window" → Enter

### Step 8: Verify MCP is running

1. Press `Ctrl+Shift+P`
2. Type "MCP: List Servers"
3. You should see "cats-rag" listed

If it doesn't appear, try running the server manually first:

```powershell
uv run python server.py
```

### Step 9: Ingest data and test

```powershell
uv run python ingest.py cats_demo.txt
```

Then open GitHub Copilot Chat (`Ctrl+Shift+I`) and ask:

*"@cats-rag search for cat hunting behavior"*

---

## Troubleshooting

### MCP shows red status / doesn't appear

1. Check the MCP logs: `Ctrl+Shift+P` → "MCP: Show Output"
2. Verify your `.env` file exists
3. Make sure you opened `MCP_workshop` as the workspace root
4. Try running manually: `uv run python server.py`

### "uv not found" error

Restart your terminal after installing uv, or check that uv is in your PATH.

### "No such file or directory" error

You likely opened the parent folder instead of `MCP_workshop`. Close and reopen with `MCP_workshop` as root.

### First startup is slow

The first run downloads the sentence-transformers model (~90MB). This is normal and only happens once.

---

## Available Tools

| Tool | API Key Needed | Description |
|------|----------------|-------------|
| `search_cats` | No | Semantic search, returns raw chunks |
| `search_cats_summarized` | Yes | Search + Claude summarization |
| `fetch_file` | No | Retrieve full file by ID |

---

## Next Steps

After installation:

1. **Ingest documents** into the vector database:
   ```bash
   uv run python ingest.py cats_demo.txt
   # or for larger files:
   uv run python ingest.py your_document.pdf
   ```

2. **Test the MCP** by asking the AI assistant to search your documents

3. **Try the terminal chat** (requires API key):
   ```bash
   uv run python chat.py
   ```
