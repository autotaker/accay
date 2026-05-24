# AGENTS.md

## Project Context

Accay is a Python CLI tool for acceptance-driven development workflows. The project is currently design-first, so read the relevant documents under `docs/` before changing component boundaries or public CLI behavior.

Important design rules:

- Keep the CLI as an orchestration layer.
- Do not add direct dependencies between `system` and `component`.
- Use Operation Directory as the machine-readable boundary between system and component artifacts.
- Keep Output responsible for rendering and file output only.
- Avoid overwriting existing user files unless a command explicitly owns that behavior.

## Development Setup

Use `uv` for dependency management:

```bash
uv sync --extra dev
```

The project uses a seven-day dependency cooldown via `tool.uv.exclude-newer`.

## Required Checks

Run tests with:

```bash
uv run pytest
```

Run lint checks with:

```bash
uv run ruff check
```

Format Python code with:

```bash
uv run ruff format
```

Run static type checking with:

```bash
uv run pyright src/accay
```

Before finishing code changes, run:

```bash
uv run pytest
uv run ruff check
uv run pyright src/accay
```

## Testing Guidance

Use contract tests for public CLI behavior and fixture-project workflows. Use unit tests for parsers, resolvers, matchers, and formatters. Probe tests are for temporary investigation and should not become required checks unless promoted intentionally.
