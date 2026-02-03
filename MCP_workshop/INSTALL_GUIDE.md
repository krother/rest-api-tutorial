# MCP Workshop - Installation Guide

> **Important**: Open the `MCP_workshop` folder as your workspace root in Cursor/VSCode for best results. Don't open the parent folder.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager
- Cursor or VSCode with GitHub Copilot

---

## macOS Installation

### Step 1: Open the correct folder

Open **only** the `MCP_workshop` folder in Cursor/VSCode (not the parent folder):

```bash
cd MCP_workshop
cursor .
# or for VSCode:
code .
```

### Step 2: Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` and fill in your Anthropic API key:

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

### Step 5: Configure MCP in VSCode

The `.vscode/mcp.json` file is already included. It should contain:

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

### Step 6: Reload the IDE

- **Cursor**: Press `Cmd+Shift+P` → "Developer: Reload Window"
- **VSCode**: Press `Cmd+Shift+P` → "Developer: Reload Window"

### Step 7: Verify MCP is running

- **Cursor**: Go to Settings → MCP, check that "cats-rag" shows green status
- **VSCode**: Check the MCP status in the bottom status bar

---

## Windows Installation

### Step 1: Install uv (if not installed)

Open PowerShell and run:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Restart your terminal after installation.

### Step 2: Open the correct folder

Open **only** the `MCP_workshop` folder in Cursor/VSCode:

```powershell
cd MCP_workshop
cursor .
# or for VSCode:
code .
```

### Step 3: Create your `.env` file

```powershell
copy .env.example .env
```

Edit `.env` with Notepad or your editor and fill in your Anthropic API key:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### Step 4: Install dependencies

```powershell
uv sync
```

### Step 5: Configure MCP in Cursor

Create the `.cursor` folder:

```powershell
mkdir .cursor
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

### Step 5: Configure MCP in VSCode

The `.vscode/mcp.json` file is already included and should work on Windows.

### Step 6: Reload the IDE

- **Cursor**: Press `Ctrl+Shift+P` → "Developer: Reload Window"
- **VSCode**: Press `Ctrl+Shift+P` → "Developer: Reload Window"

### Step 7: Verify MCP is running

- **Cursor**: Go to Settings → MCP, check that "cats-rag" shows green status
- **VSCode**: Check the MCP status in the bottom status bar

---

## Troubleshooting

### MCP shows red status

1. Check the MCP logs (click on the server name in MCP settings)
2. Verify your `.env` file exists and has valid API keys
3. Make sure you opened `MCP_workshop` as the workspace root
4. Try running manually: `uv run python server.py`

### "No such file or directory" error

You likely opened the parent folder instead of `MCP_workshop`. Close and reopen with `MCP_workshop` as root.

### First startup is slow

The first run downloads the sentence-transformers model (~90MB). This is normal.

---

## Next Steps

After installation, you need to:

1. **Ingest documents** into the vector database:
   ```bash
   uv run python ingest.py your_document.pdf
   ```

2. **Test the MCP** by asking the AI assistant to search your documents
