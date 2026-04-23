# Argus

Argus is a Python-based agentic framework focused on autonomous task execution, evaluation workflows, and extensible runtime components.

## What This Repository Includes

- Core Argus package under `argus/`
- Evaluation suites under `evaluation/` (including BFCL and SWEBench helpers)
- Container definitions for agent runtimes
- Test coverage under `tests/`

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Run tests:

```bash
pytest
```

## Repository Layout

- `argus/`: core package and runtime modules
- `evaluation/`: benchmark and adapter scripts
- `docs/`: project documentation
- `tests/`: automated tests

## License

See `LICENSE`.
