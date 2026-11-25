# TASK-C — Roots, Context and Retrieval Application

- **Claim status** · UNASSIGNED
- **Phases** · P06, P07, P10, P11 and P12 retrieval quality, ranking, UI and demonstration evidence
- **Features** · X20–X25 (roots), X26–X37 (ground/background). Ranking consumes the complete vector.
- **Academic objectives** · Accountable for R04, R04B and R05. Supports R01, R02, R03, R04A and R04C with component validation, information-value experiments and the query trace. [Requirement allocation](../team_preparation/task_allocation_matrix.md)

## Agent entry point

1. Confirm the claim and branch and open [TASK-C progress](progress/TASK-C.md). Read the [root/context feature blocks](../feature_spec.md#roots-x20x25), [ranking contract](../requirements.md#normalization-and-ranking-contract), [module contract](../module_contract.md), [acceptance gates](../acceptance_criteria.md) and the ranking decisions in the [register](../team_preparation/specification_decisions.md). Manually read the common [skills and database-development](../agent_quickstart.md#manual-skill-loading) for storage/read integration.
2. Start at **TC-01** on a new task. Inspect `src/tree_cbir/segmentation/root.py` and `src/tree_cbir/features/root.py` first. Use the synthetic tree cases for missing trunk and incomplete masks in roots/context. For ranking/UI, inspect `src/tree_cbir/similarity.py`, `src/tree_cbir/services/retrieval.py` and `app.py`. Use an in-memory fixture gallery with explicit fixture labeling until compatible M2/M3 artifacts arrive.
3. Apply `AC-P06`, `AC-P07`, `AC-P10` and `AC-P11`, and supply retrieval/demo evidence for `AC-P12`. Deliver component outputs for M1/M2 and require a real gallery and query for M4. [Independent and integration test commands](../testing.md#test-tiers-and-commands)

## Mission and starting point

Deliver root and context observations with reliable exclusion and per-feature validity. Implement exact eligible Top-5, a query service, and a focused Streamlit demonstration that exposes the actual calculations and limitations. Use synthetic observations and a fixture-only gallery in Stage I, then run real integration, evaluation and demo using the accepted extractor and populated DB.

Root/context segmentation and feature files, `similarity.py`, `services/retrieval.py` and `scripts/evaluate.py` are placeholders. `app.py` is a scaffold. The existing component assembler already invalidates X22 without a positive measured trunk width and flags or rejects certain context contamination. The pgvector P01 smoke test proves DDL/operators on temporary synthetic data. Production pair eligibility, weighted distances and exact search are still open. The audit records no accepted root/context or retrieval implementation. [Audit](../team_preparation/repository_audit.md)

Reuse `synthetic_tree_factory`, component contracts, canonical preprocessing, geometry/color/morphology/edge utilities and existing overlay functions. Known risks include uncertain trunk bases, root–ground confusion, leaf or branch pixels leaking into context, and context similarity overwhelming morphology. Previous AUTO/V2 trunk limits justify conservative fallback. Context-only pairs and unsupported missing-group scores must not become favorable matches. A healthy database provides no evidence of rank correctness or relevance.

## Permitted paths and interfaces

| Scope | Permitted source and test paths |
| --- | --- |
| Roots and context | `src/tree_cbir/segmentation/root.py`, `src/tree_cbir/segmentation/context.py`, new task-local `src/tree_cbir/segmentation/root_*.py` and `src/tree_cbir/segmentation/context_*.py`, `src/tree_cbir/features/root.py`, `src/tree_cbir/features/context.py` |
| Ranking, service and interface | `src/tree_cbir/similarity.py`, `src/tree_cbir/services/retrieval.py`, `src/tree_cbir/utils/visualization.py`, `app.py`, `scripts/evaluate.py` |
| Task validation and notes | `tests/unit/test_root_*.py`, `tests/unit/test_context_*.py`, `tests/unit/test_similarity.py`, `tests/unit/test_retrieval.py`, `tests/unit/test_demo_ui.py`, `tests/integration/test_retrieval.py`, this task checklist, `docs/tasks/progress/TASK-C.md` and `docs/logs/TASK-C.md` |

C owns ranking, application retrieval, presentation and the retrieval evaluation script. Request A's shared contract or extractor changes through A. Request SQL/schema, exact-candidate reads or normalization changes through B. Keep SQL in B's persistence adapter and restrict app logic to presentation and service calls. [Shared-file map](../team_preparation/shared_file_ownership.md)

Use root base/width reliability from `TrunkGeometry` with classical connected structures, edges, morphology or a justified supervised model fitted on group data. Prefer conservative root candidates with explicit ROI provenance. Compute context only on disjoint masks that exclude all known tree/root positives. Use versioned color predicates, grayscale/edge and line conventions from the spec and evaluate parameters on development data. Retrieval consumes compatible normalized 38-position records, validity, gallery fit and an explicit profile. It returns deterministic Top-5 plus overlap, eligibility, per-group distances/weights/contributions and reasons for degradation. Test the bounded shared-valid distance and missing-evidence adjustment in A22/A23 as a candidate. Final metric, weights, coverage and morphology gate need approval. [Root and context definitions](../feature_spec.md#roots-x20x25) · [Module contracts](../module_contract.md) · [Ranking requirements](../requirements.md#normalization-and-ranking-contract)

## Stage I — Independent development

- [ ] **TC-01** Implement root observation and X20–X25 using known masks and optional mock trunk geometry. Exercise `synthetic_tree_factory` complete, missing, uncertain base and unreliable width, exposed roots, and an explicit confirmed-absence fixture. Test root skeleton, thickness, base-connected branches and X22 invalidity. Estimated search ROI must retain its quality and may not imply a successful root detection.
- [ ] **TC-02** Implement context observation and X26–X37 with complete and incomplete exclusions. Verify `incomplete_tree=True`, known roots excluded from ground and background, valid empty versus unavailable component, detector clipping and disjointness. Publish optional inputs, diagnostics, unit and fixture results for **M1**.
- [ ] **TC-03** Implement exact eligible ranking over deterministic fixture records and an in-memory gallery/read double. Cover missing/no-overlap groups, constants, metric bounds, weight validation, ties by stable image ID, insufficient candidates, wrong profile/fit, and an independent hand-computed ranking oracle. Search the complete eligible gallery or prove equivalent exact results.
- [ ] **TC-04** Implement query service, UI trace and evaluation runner against explicit synthetic records and a labeled fixture-only mode. Include query upload, Top-5, masks, values, validity, distances, weights, coverage and failure states. Label fixture mode prominently and isolate it from production mode and report claims. Production should surface an unavailable dependency if the gallery or extractor is missing. A deterministic relevance fixture can test metric arithmetic without claiming real performance.

## Stage II — Integration

- [ ] **TC-05** Wire accepted trunk and canopy/branch metadata into roots/context with A. Verify the intended fallback on actual images, freeze/compare component candidates on development data, and publish root/context quality and limitations to **M2**. Keep the canonical root exclusion and isolate context failure.
- [ ] **TC-06** Replace query and gallery doubles with the M2 extractor and B's M3 database/normalization. Check gallery and fit compatibility, complete eligible search, same preprocessing, exact oracle results, and real trace reproducibility. Record the ranking profile after owner sign-off and keep fixtures from production output.
- [ ] **TC-07** Run real held-out retrieval evaluation after freeze. Record relevance rubric, Precision@5, Recall@5 where defined, completion/coverage, latency, failures, group ablation and weight sensitivity according to the evaluation protocol. Run the real unseen-image demonstration with five distinct eligible results and a separately degraded example using B's setup. Provide the UI walkthrough and observed trace at **M4** for A's combined report and release.

## Acceptance, evidence and handoff

- Apply `AC-X20`–`AC-X37`, `AC-Q-ROOT`, `AC-Q-CONTEXT`, `AC-P06`, `AC-P07`, `AC-P10`, `AC-P11` and C's retrieval/demo contribution to `AC-P12`. Use the [acceptance criteria and Definition of Done](../acceptance_criteria.md), [real-image protocol](../team_preparation/evaluation_protocol.md) and [test tiers](../testing.md) for M1/M4. Separate root visibility/false positives, exact rank agreement and judged relevance.
- Run the shared contract test, root/context tests, and `./.venv/Scripts/python.exe -m pytest -v tests/unit/test_similarity.py tests/unit/test_retrieval.py` once created. Validate real query and gallery compatibility with the configured DB integration suite and confirm fixture labeling/failure behavior. R04 requires five decreasing-similarity eligible results in the successful real case. Demonstrate deterministic ties, a degraded query without invented matches, and an intermediate trace that reproduces the rank.
- Record `docs/logs/TASK-C.md` with formula and real segmentation evidence separately, candidate runs, final gallery/fit/extractor/ranking IDs, query split and frozen relevance protocol, latency and coverage, exact metric commands, screenshot/trace and demo recipe. Track artifact paths and permission limits. Use the [evaluation requirements](../requirements.md#experimental-evaluation).
- Handoff using package/status, completed `TC-*` IDs, changed paths, tests and results, profile IDs, real vs fixture evidence, M1/M4 artifacts and unresolved approval/failure status. Stop at the shared round cap or when evidence shows no viable improvement. If M2 or M3 blocks real evaluation, preserve all independent results with the real gate reported `BLOCKED`. A `LIMITED` prototype requires owner review.
- Use the [evidence layout](../acceptance_criteria.md#evidence-layout) and [task handoff template](../templates/task_handoff.md). Label relevance metrics unavailable when judgments are insufficient.
- After claiming, branch `feature/root-context` from approved `develop`. Split reviewable root/context, retrieval and UI/evaluation PRs against `develop`. Request A for contract review and B for data/fit compatibility. [Git and PR workflow](../team_workflow.md#claim-and-branch-workflow)
