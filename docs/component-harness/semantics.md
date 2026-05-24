# Component Harness Semantics

## Component Responsibility

Component Harness performs machine-checkable validation and review-context source selection for component-owned artifacts. It verifies scope/test-map/interface consistency while leaving final accept or reject decisions to humans.

## Operations

### validateComponentArtifacts

Validates one component's artifact set against the Operation Directory. The operation means "confirm that the component ledger and evidence map are mechanically coherent."

Input fields include component artifacts and operation lookup capabilities. Output fields include diagnostics scoped to component, case ID, operation, schema, and source file.

Invariants: invalid scope, missing test-map case references, empty verifies, and missing operations are errors; missing semantics or review guidelines are warnings.

Forbidden transformation: using system trace presence as a precondition for component validation.

### buildReviewContextSource

Selects source material for an acceptance review. The operation means "prepare focused review inputs"; it does not produce final Markdown, update test-map, or decide acceptance.

Input fields identify component artifacts, target case, operation contracts, optional JUnit summary, and optional related system references. Output fields contain structured context sections for Output & Presentation.

Invariant: review context can include related traces as reference material without making them component source of truth.

## Common Misunderstandings

- Component Harness validates evidence structure; Component Regression evaluates executed evidence.
- Review context is not a decision file.
- Proposed updates remain separate from source-of-truth files until humans accept them.
