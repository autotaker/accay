# CLI & Workspace Semantics

## Component Responsibility

CLI & Workspace is the user-facing entrypoint. It turns command-line intent into a workspace, configuration, orchestration plan, exit code, and concise user-facing summary. It does not interpret artifact meaning or perform validation, regression, or rendering logic itself.

## Operations

### initWorkspace

Creates the minimum Accay workspace shape without overwriting existing files. The meaning of the output is a filesystem preparation summary: created paths were introduced by this run, existing paths were already present and were preserved.

Input fields identify the repository root and optional configuration defaults. Output fields preserve the distinction between created and existing paths so humans can tell whether initialization changed anything.

Invariant: existing user files are not replaced. Forbidden transformation: treating an existing file as created, or silently rewriting config.

### installSkills

Installs bundled Accay agent skills into the configured skill directory. The operation means "make the skills available to agents", not "run an agent" or "refresh every existing skill".

Input fields identify the workspace and install target. Output fields report each skill as created or existing. Existing `SKILL.md` files remain authoritative unless a future force mode is explicitly designed.

Invariant: install is non-destructive by default.

### validateWorkspace

Runs aggregate validation across system and component artifacts. The operation means "collect diagnostics from the validation components and return an exit decision"; it does not decide semantic acceptance.

Input fields define the workspace and optional validation scope. Output fields carry diagnostics, report references, and exit status. Error diagnostics make the command fail; warning and info diagnostics remain visible but do not imply failure.

Invariant: validation logic is delegated to System Harness, Component Harness, and Operation Directory.

### validateSystem

Runs system-only validation. The operation means "validate scenario, sequence, trace, and operation references"; it does not inspect component acceptance cases or test maps.

Input fields identify the workspace and optional scenario. Output fields summarize system diagnostics and exit status.

Invariant: system validation remains independent of component acceptance state.

### validateComponent

Runs validation for one component. The operation means "validate component-owned artifacts and operation references"; it does not read system traces as required input.

Input fields identify the component and workspace. Output fields summarize component diagnostics and exit status.

Invariant: component validation can run without any scenario or trace.

### packDeskDebugContext

Builds an agent-readable context for desk debugging a system scenario. The operation means "collect relevant source material"; it does not author or approve the trace.

Input fields identify the scenario and workspace. Output fields identify the run directory and generated `context.md`.

Invariant: context is an input artifact for judgment, not the system source of truth.

### packReviewContext

Builds an agent-readable context for reviewing one component case. The operation means "collect review material around scope, semantics, interfaces, tests, and optional related traces"; it does not accept or reject the case.

Input fields identify component, case ID, and optional JUnit sources. Output fields identify the run directory and generated `context.md`.

Invariant: related system artifacts are reference material, not component validation inputs.

### runRegression

Runs component regression across all components using JUnit XML and `test-map.yaml`. The operation means "evaluate known test evidence against recorded acceptance mappings"; it does not explain the business cause of failures.

Input fields identify JUnit paths and policy. Output fields aggregate component results, report paths, and exit status.

Invariant: regression is component-side and does not read system traces.

### runComponentRegression

Runs regression for one component. The operation has the same evidence meaning as `runRegression`, restricted to a single component.

Input fields identify component, JUnit paths, and policy. Output fields report case-level status for that component.

Invariant: missing or skipped evidence for an accepted case is represented as a failure according to policy.

### serveReports

Serves generated reports for human inspection. The operation means "view existing output"; it does not regenerate validation or edit source artifacts.

Input fields identify report directory and bind options. Output fields identify the server endpoint or a user-facing error.

Invariant: serve is a thin viewer over generated output.

## Common Misunderstandings

- CLI success does not mean a change is semantically accepted.
- CLI handlers should not parse YAML, JSON Schema, or JUnit details.
- Context generation does not update source-of-truth artifacts.
