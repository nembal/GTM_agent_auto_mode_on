# Contributing to Fullsend

Thanks for your interest in contributing to Fullsend! This document provides guidelines for contributing.

## Getting Started

1. **Fork the repo** and clone locally
2. **Install dependencies**: `uv sync`
3. **Copy environment**: `cp .env.example .env` and fill in your API keys
4. **Run tests**: `uv run pytest`

## Development Setup

```bash
# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies
uv sync

# Run the full system
./run_all.sh

# Run tests
uv run pytest

# Lint
uv run ruff check .
```

## Code Style

- Python 3.11+
- Use async/await for I/O operations
- Pydantic for settings and data models
- Line length: 100 characters
- Use ruff for linting

## Pull Request Process

1. **Create a branch** from `main` for your changes
2. **Write tests** for new functionality
3. **Run the test suite** to ensure nothing is broken
4. **Update documentation** if needed
5. **Submit a PR** with a clear description of changes

## Architecture Overview

See [CLAUDE.md](./CLAUDE.md) for detailed architecture documentation.

Key points:
- Services communicate via Redis pub/sub
- Each service has its own `config.py` with Settings class
- Tests use pytest-asyncio

## Adding a New Service

1. Create folder under `services/`
2. Add `__init__.py`, `main.py`, `config.py`
3. Define Redis channels it publishes/subscribes to
4. Add tests in `tests/` subfolder
5. Document in CLAUDE.md

## Adding a New Tool

Tools live in `tools/` and are dynamically loaded by the Executor.

1. Create `tools/your_tool.py`
2. Implement the required interface
3. Register with: `python -m tools.register your_tool`
4. Add tests

## Questions?

Open an issue for questions or discussion.
