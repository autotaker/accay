# Component Regression Semantics

## Component Responsibility

Component Regression compares recorded test evidence with JUnit results and aggregates case-level regression status. It detects broken or missing evidence but does not explain the business cause or update source artifacts.

## Operations

### readJUnitResultSet

Reads one or more JUnit XML files into a single result set. The operation means "create a stable executed-test evidence set keyed by `classname + name`."

Input fields identify JUnit XML paths. Output fields include testcase results, duplicate-key diagnostics, and read diagnostics.

Invariant: duplicate testcase keys are errors, not merge candidates.

### matchTestMap

Matches a component test-map against a JUnit result set. The operation means "connect accepted evidence records to executed tests."

Input fields include test mappings and result set. Output fields identify matched, missing, and unmapped tests.

Invariant: missing mapped tests are preserved as missing evidence, not ignored.

### aggregateComponentRegression

Aggregates matched tests into case-level regression status for one component. The operation means "evaluate whether each component case still has its recorded evidence."

Input fields include component artifacts, JUnit result set, and regression policy. Output fields include case results, unmapped tests, diagnostics, and overall component status.

Invariant: accepted cases with failed, errored, skipped, or missing mapped tests fail according to default policy.

### aggregateAllComponentRegression

Aggregates component regression across all components. The operation means "produce repository-level regression evidence from component-level results."

Input fields include multiple component artifact sets, one result set, and policy. Output fields include component results and overall status.

Invariant: top-level aggregation does not read system traces.

## Common Misunderstandings

- A regression failure is evidence failure, not an automatic root-cause diagnosis.
- Unmapped tests are informational unless policy changes later.
- Regression never updates `test-map.yaml`.
