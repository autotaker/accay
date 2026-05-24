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
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
python -m unittest
```

## License

MIT
