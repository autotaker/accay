# accay-desk-debugging

Use this skill to desk-debug an end-to-end scenario before implementation.

Inputs:

- `docs/acceptance/scenarios/{scenario}.feature`
- `docs/acceptance/sequences/{scenario}.md`
- component `semantics.md`
- component operation contracts and schemas

Output a draft trace at:

- `docs/acceptance/traces/{scenario}.trace.yaml`

The trace should use operation-level `input` and `output`, not endpoint-specific request and response language.
