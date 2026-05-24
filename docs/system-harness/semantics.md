# System Harness Semantics

## Component Responsibility

System Harness performs machine-checkable validation and context-source selection for system scenarios. It checks references, schemas, status codes, exit codes, and observations, while leaving semantic acceptance to humans and agents.

## Operations

### validateSystemArtifacts

Validates a scenario artifact set against the Operation Directory. The operation means "confirm that the system-side trace can be mechanically followed through component operations."

Input fields include system artifacts and operation lookup capabilities. Output fields include diagnostics scoped to scenario, trace step, component, operation, and schema reference.

Invariants: missing operations and schema validation failures are errors; thin observations are warnings; component acceptance scope and test-map are not inputs.

Forbidden transformation: converting a semantic concern into a hard validation error without a machine-checkable rule.

### buildDeskDebugContextSource

Selects the source material needed to desk-debug a scenario. The operation means "prepare focused context for human or agent reasoning"; it does not produce the final Markdown and does not edit the trace.

Input fields identify the scenario artifacts and relevant operation contracts. Output fields contain structured context sections that Output & Presentation can render.

Invariant: context includes only relevant component semantics and operation contracts, not every component artifact by default.

## Common Misunderstandings

- System Harness can say a trace is mechanically invalid; it cannot say the business change is accepted.
- Component semantics may appear in context, but it is reference material for system work.
- Context source is not report rendering.
