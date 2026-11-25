# Acceptance criteria and Definition of Done — 05/08

Use this document to decide completion of [TASK-A, TASK-B and TASK-C](tasks/README.md). The [canonical feature specification](feature_spec.md) defines semantics, the [allocation matrix](team_preparation/task_allocation_matrix.md) assigns accountability, and the [test commands](testing.md) define how to collect evidence. This preparation establishes gates. It makes no new claim about implemented quality.

## Acceptance layers and statuses

| Layer | Required evidence | What a pass establishes |
| --- | --- | --- |
| Mathematical correctness | Fixed inputs, masks and reference operands, independent expected values, stated tolerance, validity/edge cases and exact feature positions. | The numeric operation is correct on the specified inputs. |
| Real-image algorithm quality | Frozen image splits, qualified references/annotation provenance, pixel and visibility metrics, overlays, failure analysis and timings. | The evaluated profile meets the agreed real-image targets for the stated scope. |
| Integrated system functionality | Production extraction, batch/database checks, exact search, real UI/trace and reproducible demo with compatible versions. | The integrated workflow is functional with the declared gallery, query and failure paths. |

Record a separate status and evidence for every applicable layer, criterion and phase. A pass in one layer gives no credit for another. Satisfy all mandatory clauses before declaring the criterion passed. Store the observed outcome of each failed case even when aggregating task status.

| Status | Use |
| --- | --- |
| `PASS` | All applicable mandatory criteria for the assessed scope are verified and met. |
| `PARTIAL` | Some mandatory criteria remain unsatisfied. List the individual failed, blocked or pending results with their scope. |
| `FAIL` | An executed check contradicts its expected result or misses its frozen target. |
| `BLOCKED` | A required verification cannot run or cannot be judged due to missing prerequisite, reference data, environment or approval. Record the blocker. |
| `LIMITED` | The project owner explicitly accepts an evidence-backed prototype limitation. Record approver, date, scope, failed/unverified clauses, impacted features or claims, and allowable uses. Coding agents cannot award this status. |

`SKIPPED` in a test runner or a historical evidence log is an execution observation. A skipped mandatory verification is `BLOCKED` for the affected gate. Optional non-applicability is recorded with its reason and earns no acceptance credit. Any approval changing academic meaning or accepting an unmet project target must reference the [owner decision register](team_preparation/specification_decisions.md#approval-and-calibration-boundaries).

## Primary feature acceptance

The [machine-readable acceptance matrix](team_preparation/acceptance_matrix.csv) defines exactly one primary criterion per feature. Each row binds the feature ID to the specific canonical section, responsible task, input/mask fixture, exact expected value or tolerance, validity negative cases, real-image evidence and a separate quality gate.

| Group | Primary criteria | Accountable | Quality gate |
| --- | --- | --- | --- |
| Trunk | `AC-X00`–`AC-X08` | TASK-A | `AC-Q-TRUNK` |
| Canopy | `AC-X09`–`AC-X16` | TASK-B | `AC-Q-FOLIAGE` |
| Branches | `AC-X17`–`AC-X19` | TASK-B | `AC-Q-BRANCH` |
| Roots | `AC-X20`–`AC-X25` | TASK-C | `AC-Q-ROOT` |
| Ground and background | `AC-X26`–`AC-X37` | TASK-C | `AC-Q-CONTEXT` |

For the mathematical claim, execute every subcase in the row. Use independent arithmetic or a manually constructed mask, contour, graph or converted swatch as appropriate. Expected outputs must be derived independently of the implementation. Small-grid fixtures test math with explicit support and parameters; the executable shared contract tests remain canonical-grid tests. For floating values use the row's absolute tolerance and zero relative tolerance. Counts and validity flags match exactly. Test the missing metadata/region case and ensure numeric zero can coexist with a distinct false validity flag as applicable. `AC-X01`–`AC-X03` use the Lab candidate in fixtures. If the owner chooses a different bark profile, version and update those approved fixtures before production acceptance. Any executed mismatch is `FAIL`. If a required profile or test input is unavailable, mark that verification `BLOCKED`.

For the real-image portion, submit the row's requested examples and raw measurement/invalidity trace with the run under its quality gate. This evidence may be shared across neighboring features when the operands are individually traceable. Quality gates use the [evaluation protocol and historical P03 targets](team_preparation/evaluation_protocol.md). A mathematically passing feature still needs real evidence and correct behavior in the integrated component. The row alone never declares algorithm or task acceptance.

## Mandatory phase gates

For P03–P07, each row requires its complete set of primary feature tests, real-image quality gate, explicit validity for unavailable/uncertain observations, original/mask and ROI/overlay evidence, intermediate operands and values, actual-image timing, limitations and reproducible commands. Component handoff also verifies output shape, profile and integration contract with the receiving task.

| Criterion | Phase and accountable task | Additional mandatory checks and evidence |
| --- | --- | --- |
| `AC-P03` | P03 trunk · TASK-A | `AC-X00`–`AC-X08` and `AC-Q-TRUNK`. Verify vertical, inclined and curved trunks, basal runs and actual junction counts. Test absence, width and endpoint provenance. Preserve the AUTO 5/6 and 9/12 targets and results and distinguish independent V2 findings. Supply candidate comparison/method decision and gate status. |
| `AC-P04` | P04 foliage/canopy · TASK-B | `AC-X09`–`AC-X16` and `AC-Q-FOLIAGE`. Test leafy, sparse, leafless and unknown cases, consistent HSV and geometry, fallback without trunk and shared ROI delivery to branches. |
| `AC-P05` | P05 branches · TASK-B | `AC-X17`–`AC-X19` and `AC-Q-BRANCH`. Verify shared canopy ROI, unreliable ROI fallback, observed unbranched count zero, exposed-vs-hidden distinctions and reproducible skeleton/measurement evidence. |
| `AC-P06` | P06 roots · TASK-C | `AC-X20`–`AC-X25` and `AC-Q-ROOT`. Require visible and verified negative cases, abstentions/false positives, base/ROI provenance and root skeleton evidence. Unreliable trunk width invalidates X22 at integration too. |
| `AC-P07` | P07 context · TASK-C | `AC-X26`–`AC-X37` and `AC-Q-CONTEXT`. Independently verify ground and background, disjointness, no included known tree/root pixels and explicit missing exclusion risk. Validate color, intensity, edge and in-mask line evidence and show errors in natural and built surroundings. |
| `AC-P08` | P08 extraction · TASK-A | Prove exactly 38 ordered finite raw positions and 38 bool validity flags for the production entry point. Check equivalent preprocessing on ingest/query, supported optional metadata, independent failure isolation and propagation of uncertain/absent status. Demonstrate shared canopy ROI, X22 width guard and root exclusion/context invalidity, approved common profile IDs and no mock substitution in production. Include real and synthetic integration evidence separately. |
| `AC-P09` | P09 database/ingestion · TASK-B | Attempt all 507 standardized manifest entries and reconcile each ID/hash to one final disposition. Use terminal counts for accepted/extracted, rejected and failed (including reason); report coverage and invalid counts per feature for stored vectors as separate dimensions. Do not equate attempts with success or all-valid vectors. Verify R01's ≥500 accepted corpus images separately from rank eligibility. Persist raw/normalized values, bool validity, metadata, image reference, group slices and fit/config versions. Independently recompute Min–Max from valid indexed fits and verify valid constant, all-unavailable, out-of-range and query reuse behavior. Demonstrate replay with no duplicate/change for the same inputs, retry/rollback and atomic gallery publication, stale/mixed-version rejection and PostgreSQL round-trip/read reproducibility. |
| `AC-P10` | P10 retrieval · TASK-C | Validate five weighted group distances, shared intersection, valid dimensions and fixed profile coverage logic, monotonic handling of removed support, and enough morphology support under the approved profile. Compare the same stored/effective values to an independent exhaustive reference over all eligible candidates. Require matching eligible IDs, score tolerance agreed before the run, and exact ordered result IDs with stable ID ties. Supply five distinct results when at least five are eligible; for zero to four, expose insufficient coverage, count and genuine results only. Check incompatible profile and avoid fabricated candidates or scores. |
| `AC-P11` | P11 UI · TASK-C | Record a new image uploaded through UI, actual preprocessing/extraction and Top-5 from the real gallery, plus invalid/failure or degraded query. Show image/ROI/masks, raw and normalized values, flags and explanations, group distances, weights, shared counts and contributions reconstructing the scores. Display meaningful error states. Keep explicit synthetic demo mode labeled and isolated from production. |
| `AC-P12` | P12 evaluation and release evidence · TASK-A | A supplies integrated regression and extraction quality, B actual 507-entry batch accounting and DB/normalization evidence, C independent retrieval relevance and demo. Record runtime boundaries and outcomes, exact ranking and held-out quality separately, relevance rubric and quality metrics only where judgments exist. Document missing references as a limitation with the resulting gate state. Attempt ablation/group-only and weight sensitivity when feasible and record a concrete reason otherwise. Include real failures, deterministic setup and reproducible real successful and degraded demos. |

## Definition of Done

### Individual feature

- [ ] One canonical X slot and its `AC-X` tests pass with expected units and tolerances. Missing-data and genuine-zero assertions pass.
- [ ] Required real-image operands, validity reasons and examples are linked. Report the relevant quality status separately. Owner-sensitive decisions affecting the feature are resolved or recorded as blocked.

### Component

- [ ] The assigned feature block and component contract pass, including mask/ROI layout, reliability and correct missing-uplink handling. Known failures never produce unsupported valid values.
- [ ] The applicable `AC-Q-*` gate has traceable data, metrics, timings and an actual status. The component carries a versioned profile and diagnostics and has a tested integration handoff.

### Task package

- [ ] All assigned primary and phase criteria have individual statuses and evidence. Required stages, artifacts and the corresponding milestone handoff have been completed. Pending or failed mandatory gates prevent a `PASS`.
- [ ] The package log and [handoff template](templates/task_handoff.md) record commit, changed files, exact test commands and results, artifact references, dependencies and owner decisions. Shared changes have been coordinated with their accountable package.
- [ ] If the owner accepts a bounded prototype, mark the approved scope `LIMITED` and retain underlying `FAIL`/`BLOCKED` results and what remains required for full completion.

### Integration milestones

| Milestone | Accountable | Completion checklist |
| --- | --- | --- |
| M1 · Component interfaces | TASK-A | Shared and component contract checks pass with synthetic inputs, compatible input/output types are published, and each provider supplies readiness, versions and fallback evidence. |
| M2 · Extraction | TASK-A | P03–P08 production path verified per gates above; actual compatible component registrations and extractor profile are available to B/C. Record any expressly approved `LIMITED` scope with no claim of full phase PASS. |
| M3 · Database | TASK-B | AC-P09 verified on the approved 507-entry manifest. The reproducible gallery, frozen fit, fail counts, validity and read interface are supplied to C. |
| M4 · Retrieval and demo | TASK-C | AC-P10/11 and C's AC-P12 contribution verified with real gallery and unseen query. Record exact ranking, successful and degraded trace, and reviewed reproduction instructions. |

### Final project

- [ ] TASK-A consolidates phase, feature and `AC-Q` evidence, test tiers, R01–R05 traceability and M1–M4 records, including B/C contributions. All required acceptance gates must be met for a full project `PASS`.
- [ ] Final `AC-P12` run links dataset/split/profile IDs, quality and runtime evidence, complete demo instructions, reproducible commands and actual limitations. A separately approved `LIMITED` demonstration preserves the unmet gates and acceptance scope in the report.
- [ ] Implementation existence and green unit tests alone do not close component, task, milestone or project acceptance.

## Evidence layout

Use `outputs/evaluation/<task-id>/<run-id>/` for local runs or mirror that layout in an approved internal artifact store. Use a stable run ID and task name (`task-a`, `task-b`, `task-c`), then link the checkpoint/commit from `docs/logs/TASK-A.md`, `docs/logs/TASK-B.md` or `docs/logs/TASK-C.md`. Example layout:

```text
run metadata and commands        run.md, versions.json
input and annotation provenance  manifests/, checksums.sha256
test outputs and decisions       tests/, criteria.csv
feature operands and validity    features/, validity.csv
masks, overlays and comparisons  segmentation/
metrics and runtime               metrics/, timings.csv
failure cases and limitations    limitations.md
real query or demo trace          demo/
```

`criteria.csv` in a run records criterion ID, assessment layer, status, executed vs blocked evidence, and reference paths. Include environment/library versions, fixed seeds, manifest/split and algorithm/fit/ranking IDs where relevant. Track digest, authorized internal location, access instructions and retention for large or private files. Keep `.env`, images, sealed references, model files, database dumps, caches and huge output batches out of routine Git commits. Small summaries and checksums can be tracked after checking publication policy. Evidence missing at handover is not presumed to exist.
