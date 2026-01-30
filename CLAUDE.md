# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Sphinx documentation project for a REST API tutorial teaching FastAPI and Pydantic. The documentation builds into HTML using the Furo theme.

## Common Commands

```bash
# Install dependencies
uv sync

# Build documentation
uv run make html
```

## Project Structure

- **Root level**: Sphinx configuration (`conf.py`, `index.rst`, `Makefile`)
- **Numbered directories** (`01-hello-world/`, `02-pydantic/`, `03-async/`): Tutorial chapters
  - `README.rst` or `README.md`: Chapter content written in reStructuredText/Markdown
  - `app.py`: Working FastAPI example code for that chapter
- **`build/`**: Generated HTML output (gitignored)
- **`_static/`**: Static assets (CSS, images)

## Writing Guidelines

- each chapter consists of one README.rst file
- each chapter has a topic:: directive goal section at the top
- use === headings for chapter titles
- use --- headings for exercises
- each exercise starts with the word "Exercise <number>:"
- use +++ headings for lv.3 headings
- max. 3 levels of headings
- Documentation uses both reStructuredText (`.rst`) and Markdown (`.md`) via myst-parser
- prefer .rst over .md
- use Mermaid diagrams where useful
- images should be .png files
- Code examples in chapters can be self-contained or include code puzzles that participants need to complete by themselves (mixed up lines, gaps)
- complete examples should be runnable with `uv run fastapi dev`
- general writing style is that of a step-by-step guide
- no long theory, this can be linked to external sources
