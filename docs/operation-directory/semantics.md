# Operation Directory Semantics

## Component Responsibility

Operation Directory is the machine-readable boundary between system and component artifacts. It builds a catalog of component operations and schema references so other components can resolve `component + operation` without parsing raw interface files.

## Operations

### buildOperationDirectory

Builds an in-memory operation catalog from component interface artifacts. The operation means "make operation contracts addressable"; it does not merge conflicting definitions or judge semantics.

Input fields identify component interface paths. Output fields include operation entries, schema references, and diagnostics for duplicate IDs or unreadable files.

Invariant: operation IDs are unique within one component.

### lookupOperation

Looks up a component operation. The operation means "resolve the contract identity for this boundary call."

Input fields identify component and operation. Output fields either contain the operation contract or a lookup diagnostic.

Invariant: lookup failure is diagnostic data, not a reason to invent a fallback operation.

### resolveInputSchema

Resolves the input schema for an operation. The operation means "find the contract used to validate input values."

Input fields identify component and operation. Output fields include the schema reference and loaded schema material when available.

Invariant: schema paths remain repository-root relative at the interface boundary.

### resolveOutputSchema

Resolves the output schema for an operation. The operation has the same meaning as `resolveInputSchema`, applied to output values.

Invariant: output schema resolution does not validate a concrete output value by itself.

### checkHttpStatus

Checks whether an HTTP status is allowed by an HTTP operation contract. The operation means "compare a trace status against the catalog"; it is not an OpenAPI lint pass.

Input fields identify component, operation, and status. Output fields indicate allowed or mismatched status and carry allowed values for diagnostics.

Invariant: non-HTTP operations are not silently treated as HTTP.

### checkCliExitCode

Checks whether a CLI exit code is allowed by a CLI operation contract. The operation means "compare an observed or expected exit code against the catalog."

Input fields identify component, operation, and exit code. Output fields indicate allowed or mismatched exit code and carry allowed values.

Invariant: non-CLI operations are not silently treated as CLI.

## Common Misunderstandings

- Operation Directory is not the source of semantic truth; `semantics.md` is.
- Operation Directory does not read acceptance cases or test mappings.
- Schema resolution is not business validation.
