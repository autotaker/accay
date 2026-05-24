# Component Artifacts Semantics

## Component Responsibility

Component Artifacts represents component-owned source files as readable artifact models. It preserves scope, test evidence mappings, semantics paths, review guideline paths, and interface paths without judging acceptance or regression status.

## Operations

### discoverComponents

Discovers component directories under the docs root. The operation means "find component-owned source-of-truth areas."

Input fields identify the workspace and components root. Output fields list component names and paths in deterministic order.

Invariant: only directories are component candidates.

### loadComponentArtifacts

Loads the artifact set for one component. The operation means "read all component-owned source material needed by Harness or Regression."

Input fields identify component and workspace. Output fields include scope data, test-map data, semantics path, review guidelines path, interface paths, and read diagnostics.

Invariant: related system traces are not required inputs.

### loadAcceptanceScope

Loads a component's acceptance-scope YAML. The operation means "read the case ledger"; it does not decide whether a case status is appropriate.

Input fields identify the component path. Output fields preserve case IDs, titles, priorities, statuses, scenarios, operations, and parser errors.

Invariant: status policy is checked by Component Harness, not by the loader.

### loadTestMap

Loads a component's test-map YAML. The operation means "read the recorded evidence mapping"; it does not compare against JUnit results.

Input fields identify the component path. Output fields preserve case IDs, mapped JUnit `classname + name` keys, verifies text, and parser errors.

Invariant: verifies text is preserved as review evidence, not normalized into a generated test ID.

## Common Misunderstandings

- Loading a component artifact is not accepting the component.
- Component Artifacts does not build the operation catalog.
- Component Artifacts does not read system traces for validation.
