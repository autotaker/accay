# Accay

Accay is an acceptance-driven development support tool for AI-assisted coding workflows.

It helps teams decide whether a generated change is acceptable by organizing:

- Gherkin scenarios
- component semantics
- operation contracts
- desk-debug traces
- acceptance scopes
- test evidence maps
- regression reports based on JUnit XML

The product name combines **Acceptance** and **Assay**.

## Status

This repository is being bootstrapped from the v8 requirements document.

Current focus:

- CLI project skeleton
- `accay init`
- `accay install`
- validation and regression harness design
- agent skill templates

## Requirements

The requirements definition is stored at:

- [docs/requirements.md](docs/requirements.md)

## Planned CLI

```bash
accay init
accay install
accay validate
accay regression --junit <path>
accay serve

accay system validate
accay system pack desk-debug --scenario <scenario>

accay component validate <component>
accay component pack review <component> --case <case-id>
accay component regression <component> --junit <path>
```

## Development

```bash
uv sync --extra dev
```

Run the test suite:

```bash
uv run pytest
```

Check lint rules:

```bash
uv run ruff check
```

Format Python files:

```bash
uv run ruff format
```

Run static type checking:

```bash
uv run pyright src/accay
```

Before sending a change for review, run:

```bash
uv run pytest
uv run ruff check
uv run pyright src/accay
```

## License

MIT
