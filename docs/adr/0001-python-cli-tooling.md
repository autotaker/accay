# ADR 0001: Python CLI tooling and dependency management

Date: 2026-05-25

Status: Accepted

## Context

Accay is a Python CLI tool that supports acceptance-driven development workflows. The design keeps the CLI as a thin orchestration layer, places validation and regression logic in dedicated components, and favors readable diagnostics and reports over a large runtime framework.

The project also needs a conservative supply-chain posture. Dependency installation should avoid newly published artifacts where practical, because recently uploaded packages have a higher risk of accidental breakage or malicious compromise before the ecosystem has had time to observe them.

## Decision

Use the following baseline stack for the MVP:

| Area | Choice | Purpose |
|---|---|---|
| CLI parsing | `argparse` | Keep CLI orchestration explicit and avoid an unnecessary runtime dependency. |
| YAML | `PyYAML` | Read config, trace, scope, test-map, and operation files with safe loading. |
| JSON Schema | `jsonschema` | Validate trace `input.value` and `output.value` against component schemas. |
| Terminal output | `rich` | Render diagnostics summaries, tables, and readable console output. |
| Report templates | `Jinja2` | Generate Markdown and HTML context/report files from stable templates. |
| Tests | `pytest` | Support contract tests, unit tests, fixtures, and focused CLI behavior checks. |
| Lint/format | `ruff` | Use one fast tool for linting and formatting. |
| Type checking | `pyright` | Prefer fast type checking and strong editor feedback for package boundaries. |
| Dependency manager | `uv` | Maintain a lockfile and reproducible local environment. |

Configure `uv` with:

- `exclude-newer = "7 days"` as the release-age gate, excluding distributions uploaded less than seven days before resolution.
- `index-strategy = "first-index"` to keep dependency resolution on the first index that contains a package and reduce dependency-confusion risk.
- `prerelease = "disallow"` to avoid pre-release dependencies unless the policy is intentionally changed later.

## Consequences

Accay keeps a small runtime dependency set while still gaining better CLI output and deterministic report rendering.

`argparse` remains acceptable because the CLI is not intended to contain business logic. If command ergonomics become a major maintenance issue later, Click can be reconsidered in a separate ADR.

`PyYAML` is sufficient for MVP read/generate flows. If Accay later needs comment-preserving edits to human-maintained YAML files, `ruamel.yaml` can be reconsidered.

`pyright` is the first type checker because it is fast and fits the package-boundary feedback loop. `mypy` remains a reasonable fallback if a future dependency requires mypy plugins or if Python-only tooling becomes more important than editor responsiveness.

The seven-day release-age gate may delay adoption of fresh dependency releases. That is an intentional tradeoff for supply-chain safety. Emergency upgrades can be handled explicitly by changing the lock operation or temporarily relaxing the setting in a reviewed change.
