# Output & Presentation Semantics

## Component Responsibility

Output & Presentation turns diagnostics, context sources, and regression results into readable CLI summaries, Markdown files, HTML reports, and a thin local viewer. It does not decide validation or regression status.

## Operations

### renderDiagnosticsSummary

Renders diagnostics for CLI display. The operation means "make existing diagnostic facts readable."

Input fields include diagnostics and display preferences. Output fields include summary text, severity counts, and recommended exit status supplied or derived from diagnostic severity.

Invariant: Output does not invent diagnostic severity.

### writeDeskDebugContext

Writes a desk-debug context Markdown file. The operation means "render selected system context for human or agent reasoning."

Input fields include structured context source and run metadata. Output fields identify the written path and diagnostics about rendering.

Invariant: writing context does not edit scenario, sequence, or trace source files.

### writeReviewContext

Writes an acceptance-review context Markdown file. The operation means "render selected component review material."

Input fields include structured review context and run metadata. Output fields identify the written path and diagnostics.

Invariant: writing review context does not update `test-map.yaml` or `acceptance-scope.yaml`.

### writeRegressionReports

Writes Markdown and HTML regression reports. The operation means "render regression results for humans, CI, and agents."

Input fields include regression result data and report directories. Output fields identify generated report paths and rendering diagnostics.

Invariant: report rendering does not recalculate regression.

### serveGeneratedReports

Serves generated reports through a local viewer. The operation means "make existing reports browsable."

Input fields identify report directory and bind options. Output fields identify server endpoint or user-facing failure.

Invariant: serve does not edit source artifacts or regenerate reports.

## Common Misunderstandings

- A pretty report is not the source of truth.
- Context and report are different artifacts: context is input for judgment, report is output from a run.
- Output must not call artifact loaders to fill gaps.
