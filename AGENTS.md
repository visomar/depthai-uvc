# AGENTS.md

Guidelines for any AI coding agent (or human) working in this repository.

## Principles

- Add tests whenever possible. New behavior should come with tests; bug fixes should come with a regression test.
- Keep the code simple. Prefer clear, small functions over clever ones.
- Document through naming: choose descriptive names for functions, methods, and variables so the code explains itself. Add comments or docstrings only for the *why*, not the *what*.
- Follow Python software engineering best practices at all times (PEP 8, type hints, small single-purpose functions, no mutable default arguments, no bare `except`, context managers for resources, etc.).

## Project notes

- Python package lives in `src/oak_app/`.
- Uses DepthAI v3 (`depthai>=3.11,<4`). The v3 API differs from v2, so v2 examples found online usually will not work.
- See `README.md` for setup and run instructions.
