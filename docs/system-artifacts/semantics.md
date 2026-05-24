# System Artifacts Semantics

## Component Responsibility

System Artifacts represents the system-side source files as readable artifact models. It preserves identity, ordering, raw values, and source locations so System Harness can validate them. It does not decide whether operations exist or whether values match schemas.

## Operations

### discoverSystemArtifacts

Discovers scenario, sequence, and trace candidates under the workspace docs root. The meaning of the output is an inventory of system-side source material keyed by scenario ID.

Input fields identify the workspace and docs root. Output fields preserve discovered paths and missing counterparts.

Invariant: discovery is deterministic and does not validate semantic completeness.

### loadScenarioArtifacts

Loads the artifact set for one scenario. The operation means "read the source files that describe a scenario"; it does not judge whether the scenario is acceptable or complete.

Input fields identify the scenario. Output fields include scenario text, optional sequence text, optional trace data, and read diagnostics.

Invariant: missing or unreadable files are represented so Harness can produce diagnostics.

### loadTraceArtifact

Loads one trace YAML file while preserving step order and raw values. The operation means "turn trace source into a structure that can be inspected"; it does not validate operation references or schemas.

Input fields identify a trace path. Output fields preserve raw step IDs, components, operations, schema refs, values, observations, and parser errors.

Invariant: trace values are not normalized in a way that loses diagnostic context.

## Common Misunderstandings

- Reading a trace is not validating it.
- System Artifacts never reads component scope or test-map files.
- The sequence markdown helps humans understand a scenario but is not a machine contract.
