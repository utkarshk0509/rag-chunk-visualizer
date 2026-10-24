# Contributing

Thank you for considering contributing to **rag-chunk-visualizer**! Here's how to get started.

## Development Setup

```bash
# Clone the repo
git clone https://github.com/utkarshk0509/rag-chunk-visualizer.git
cd rag-chunk-visualizer

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Linting

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
ruff check .
ruff format .
```

## Adding a New Chunking Strategy

1. Implement your strategy function in [`src/chunkers.py`](src/chunkers.py).
   - Return `list[Chunk]` using the `_chunk()` helper.
2. Register the strategy name in `STRATEGIES` in [`src/cli.py`](src/cli.py).
3. Wire up the lambda in the `runners` dict in `main()`.
4. Add at least one test in [`tests/test.py`](tests/test.py).

## Pull Request Guidelines

- Keep PRs focused on a single concern.
- Ensure all tests pass before submitting.
- Add an entry to `CHANGELOG.md` under `[Unreleased]`.
