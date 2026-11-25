# Three selectable task packages — 04/08

Read [AGENTS.md](../../AGENTS.md), then select one package through the [claim workflow](../team_workflow.md#claim-and-branch-workflow). Open its agent entry point and progress record before reading code. Package ownership below identifies technical accountability. Every package remains **UNASSIGNED** to a person. P01 and P02 are accepted foundations. Preserve their interfaces, source data and evidence.

| Package | Claim status | Primary scope | P12 contribution | Progress |
| --- | --- | --- | --- | --- |
| [TASK-A](TASK-A.md#agent-entry-point) | UNASSIGNED | P03 trunk X0–X8, P08 extraction, shared contracts and final integration | Extraction quality, compatibility, integration regression, release candidate and combined report evidence | [TASK-A](progress/TASK-A.md) |
| [TASK-B](TASK-B.md#agent-entry-point) | UNASSIGNED | P04 canopy X9–X16, P05 branches X17–X19, P09 normalization, storage and ingestion | Database integrity, Min–Max and batch evaluation, reproducible database setup and populated demo gallery | [TASK-B](progress/TASK-B.md) |
| [TASK-C](TASK-C.md#agent-entry-point) | UNASSIGNED | P06 roots X20–X25, P07 context X26–X37, P10 exact retrieval and P11 UI | Retrieval quality and evaluation, ranking explanation, working UI and observed demo walkthrough | [TASK-C](progress/TASK-C.md) |

[Agent quickstart](../agent_quickstart.md) · [Authority by concern](../../AGENTS.md#authoritative-references) · [Testing](../testing.md) · [Repository audit](../team_preparation/repository_audit.md) · [Phase and requirements allocation](../team_preparation/task_allocation_matrix.md)

## Workload and balance

| Package | Actual remaining burden | Scope control |
| --- | --- | --- |
| TASK-A | High uncertainty around real trunk masks, expected height and feature/prototype discrepancies. Hybrid and V3 data preparation reduce startup cost. P08 has an executable assembler but still needs runtime wiring and version coordination across all groups. | Start with reproducible hybrid and canonical measurement math. Continue V3 only if a bounded baseline comparison justifies it. Carry shared compatibility and release integration in this package. |
| TASK-B | Two unimplemented but related segmentation tasks share the canopy ROI and image utilities. Database and normalization are deterministic but have substantial implementation, migration, re-ingestion and data integrity work. | Reuse one canopy ROI, test persistence on synthetic vectors and keep ranking outside the persistence module. Own the reproducible populated gallery and database startup for the demo. |
| TASK-C | Roots and context have real uncertainty when upstream masks or trunk geometry are unreliable. Ranking requires explicit missingness handling, while UI and evaluation add feature visibility and demonstration work. | Start with fixtures, use conservative fallbacks and keep P11 to a single required query workflow with diagnostics. Use B's reproducible gallery/bootstrap and A's release regression rather than duplicate setup or coordination. |

The proposed phase allocation is retained. C has more phase boundaries, and B and A take hands-on responsibility for the demo database and release integration respectively. This reduces duplication and keeps C responsible for query behavior, evaluation and presentation. The balance reflects algorithm uncertainty and integration work as well as implementation size.

## Stages and synchronization milestones

**Stage I** runs in parallel. Each package implements and tests with versioned synthetic inputs and test doubles for its unavailable dependencies. **Stage II** replaces those inputs with compatible, accepted implementations and collects real-data evidence. Shared-interface or owner-approval gates apply to production choices. They leave synthetic work and already-defined numerical semantics available in Stage I.

| Gate | Accountable | Producers and artifact exchange | Exit condition |
| --- | --- | --- | --- |
| M1 · Component interface readiness | TASK-A | A publishes the pinned component contract and trunk observation schema. B hands over canopy/branch observations and shared-ROI provenance. C hands over root/context observations and exclusion diagnostics. Each supplies test commands, fixtures and profile IDs. | Shape, dtype, IDs, validity, failure behavior and contracts pass on fixtures. Any shared change is merged before beginning dependent stage-II wiring. |
| M2 · Feature extraction readiness | TASK-A | A combines production trunk and accepted B/C component registrations, propagates optional metadata, and publishes the extractor entry point with its profile ID, allowed dependency fallbacks and real-image evidence. B/C review their slices. | Assembled output satisfies the entire 38-position contract for real inputs. Report feature coverage and known limits. A `LIMITED` candidate proceeds only with recorded owner approval and valid flags reflecting actual evidence. |
| M3 · Database ingestion readiness | TASK-B | A supplies M2 extractor and profile. B runs full ingestion of the approved corpus, publishes gallery and fit IDs, compatible read API, manifest counts and replay procedure. C validates it can consume the gallery. | A locally reproducible PostgreSQL gallery with integrity results, ≥500 report-eligible corpus records as required by R01, and compatible finite vectors, validity and fit provenance. Document failures and prevent partial gallery publication. |
| M4 · Retrieval and demonstration readiness | TASK-C | C uses the M2 query extractor and M3 gallery/fit and publishes exact ranking proof, held-out evaluation, UI trace and demo recipe. B validates replay. A reviews compatibility and collects all work into the release candidate. | Verified real unseen query with five distinct eligible results, separately demonstrated degraded query, reproducible evaluation and evidence for R04–R05. Owner reviews any unmet gate explicitly. |

Final release is coordinated by A after M4 and the complete three-part P12 evidence is available. M3/M4 require the corresponding production path, even if the synthetic equivalents were completed earlier. The [allocation matrix](../team_preparation/task_allocation_matrix.md) records detailed handoffs and owners.

## Rules for all packages

- Start with the [feature specification](../feature_spec.md), [module contract](../module_contract.md), [requirements](../requirements.md), and [shared-file ownership](../team_preparation/shared_file_ownership.md). Keep 38 positions, canonical units, validity, and algorithm/configuration provenance. Separate measurements on known synthetic masks from segmentation quality on actual images.
- Prefer existing classical CV and handcrafted utilities. Supervised models may be trained on group-owned data only. Prohibit pretrained models, external AI inference, filename-specific production rules, production dependence on ground truth, and replacing the feature vector with embeddings.
- Use at most **three meaningful additional algorithm-improvement rounds per package by default**. Record hypothesis, configuration, development split, change, result and keep/drop decision in each round. A round tests a changed method or tuned configuration against the selected development baseline. Stop early when the evidence shows no viable improvement. Request owner direction before expanding the research budget. Synthetic math fixes and integration corrections do not authorize further tuning. Freeze selection before a held-out evaluation, and keep independent sets out of subsequent tuning.
- Use `PASS`, `PARTIAL`, `FAIL`, `BLOCKED` or `LIMITED` for acceptance. Keep runner `SKIPPED` counts in logs and classify required skipped verification as `BLOCKED`. A failed quality gate remains failed. The owner may accept a `LIMITED` prototype after reviewing evidence, documented limitations and actual resulting coverage. Keep required positions with explicit validity and reasons even in that case. [Acceptance criteria and Definition of Done](../acceptance_criteria.md)
- Run relevant targeted tests during development and the coordinated full suite after production integration. Preserve existing work and protect `.env`, datasets, sealed labels, heavy artifacts and machine-specific exports. Put reproducible runs and checksums in the relevant task evidence. Evidence can live in an approved internal artifact location with a tracked summary that teammates can use.

For Stage I a minimal cross-cutting smoke command is `./.venv/Scripts/python.exe -m pytest -v tests/unit/test_component_contracts.py`. It uses the existing `synthetic_tree_factory` without dataset or database access. [Exact contract run procedure](../module_contract.md#isolated-development-and-verification)
