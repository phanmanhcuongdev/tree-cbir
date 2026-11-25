# Testing

Test mathematical correctness, real-image quality and integrated functionality separately. Record exact commands, commit/profile, environment, exit code, counts, actual results and elapsed time. Use the [acceptance criteria](acceptance_criteria.md) for status and the [evaluation protocol](team_preparation/evaluation_protocol.md) for real evidence.

## Test tiers and commands

Run from the repository root in PowerShell with Python dependencies installed in `.venv`. **Available** commands target current files. **Planned** selectors list files/tests that owners must add under their package scope. Run a planned command when its files and prerequisites exist. A missing selector or no collected cases leaves the required verification `BLOCKED`.

| Tier | Exact command | Prerequisites and required evidence |
| --- | --- | --- |
| T1 · Unit/math, available | `./.venv/Scripts/python.exe -m pytest -v tests/unit/test_models.py tests/unit/test_preprocessing_utils.py` | Venv only. Assure explicit validity, shape, RGB and generic utilities. Log actual cases and statuses. |
| T1 · Unit/math by package, planned | A: `./.venv/Scripts/python.exe -m pytest -v tests/unit/test_trunk_features.py`<br>B: `./.venv/Scripts/python.exe -m pytest -v tests/unit/test_canopy_features.py tests/unit/test_branch_features.py tests/unit/test_normalization.py`<br>C: `./.venv/Scripts/python.exe -m pytest -v tests/unit/test_root_features.py tests/unit/test_context_features.py tests/unit/test_similarity.py` | Venv and local synthetic fixtures only. Include parameterized `AC-X00`–`AC-X37` case IDs in pytest output, numerical fixtures and missing-value tests. Scope X IDs by package. Keep masks/operands pinned while testing feature math. |
| T2 · Shared contract, available | `./.venv/Scripts/python.exe -m pytest -v tests/unit/test_component_contracts.py` | Venv and `synthetic_tree_factory` only. Verify 14 existing cases, plus any later additions. Keep fixture outputs tagged `test-only`. |
| T3 · Component integration, planned | `./.venv/Scripts/python.exe -m pytest -v tests/unit/test_extractor.py tests/unit/test_dataset_ingestion.py tests/unit/test_retrieval.py tests/unit/test_demo_ui.py` | Venv, synthetic observations, a DB/read double and explicitly tagged fixture mode. A owns extractor wiring/failed component, B owns batch/retry/normalization consumption, C owns query/trace and fixture-vs-production separation. Log compatibility and failure-path assertions. |
| T4 · PostgreSQL/pgvector, available | `./.venv/Scripts/python.exe -m pytest -v tests/integration/test_database.py` | Healthy local PostgreSQL/pgvector and process `DATABASE_URL`. Preserve round-trip and distance tests. Record actual integration status, including skips. |
| T4 · Persistence and retrieval integration, planned | `./.venv/Scripts/python.exe -m pytest -v tests/integration/test_database.py tests/integration/test_dataset_ingestion.py tests/integration/test_retrieval.py` | Local DB schema/extensions, verified disposable test data/gallery, process `DATABASE_URL`. B records migrations, idempotency, rollback, fit/provenance and reads; C records exact rank and eligibility against independent reference. Synthetic data validates DB/API behavior, not real relevance. |
| T5 · Real-image quality, planned | `./.venv/Scripts/python.exe -m pytest -v tests/integration/test_end_to_end.py -k real_image_evaluation` | A wires the planned selector to the frozen real-image run manifests and A/B/C outputs. Supply the run manifest and writable evidence directory as below. Provide overlays, per-feature operands/validity, quality metrics and aggregate/failure summaries. Verify versions, constraints and provenance; execute the versioned component runners or verify their linked immutable results by hash. Do not use fixtures as references. |
| T6 · End-to-end and demonstration, planned | `./.venv/Scripts/python.exe -m pytest -v tests/integration/test_end_to_end.py -k demo_acceptance` followed by `./.venv/Scripts/python.exe -m streamlit run app.py` | Compatible production extractor, real gallery/fit, PostgreSQL URL, unseen real query and approved degraded example. Verify full ordered trace, database/score evidence and expected failure status. Manually capture the real UI state and exact results or record why the demo gate is blocked. |

T1–T3 use no 507-image corpus or PostgreSQL. Use the exact selectors above and [shared synthetic fixture documentation](module_contract.md#isolated-development-and-verification). Running all of `tests/unit` today also selects annotation/split tests that reference real/curated artifacts. Those tests retain their existing prerequisites and do not belong in a dataset-free selector.

### PostgreSQL and full regression

Use the [local isolated database](database.md#local-isolated-database) and keep `.env` values out of logs. With the service ready and `DATABASE_URL` already set for the test process, the full command is `./.venv/Scripts/python.exe -m pytest -v`. To construct a process-local connection string from this repository's `.env`, use the following wrapper. It defaults to the full suite. Add `tests/integration/test_database.py` after `-v` to select the existing database-only test or use the other T4 selectors when implemented.

```powershell
@'
import os
import sys
from dotenv import dotenv_values
from psycopg.conninfo import make_conninfo
import pytest

cfg = dotenv_values('.env')
os.environ['DATABASE_URL'] = make_conninfo(
    host='127.0.0.1', port=cfg.get('POSTGRES_PORT') or '5432',
    dbname=cfg['POSTGRES_DB'], user=cfg['POSTGRES_USER'],
    password=cfg['POSTGRES_PASSWORD'], connect_timeout=5,
)
raise SystemExit(pytest.main(sys.argv[1:]))
'@ | .\.venv\Scripts\python.exe - -v
```

Wait until the database is healthy before executing pytest. Use the [dataset and artifact guide](dataset_setup.md#full-regression-and-holdout-custody) for the legacy annotation/split fixtures and standardized corpus required by the full suite. Verify the database test appears as passed before claiming DB coverage. A skipped DB test leaves T4 blocked. Run release hygiene with `./.venv/Scripts/python.exe -m pip check`, `./.venv/Scripts/python.exe -m ruff check .`, `./.venv/Scripts/python.exe -m ruff format --check .` and `git diff --check`. Record process exit codes, especially after collecting logs.

### Real-data command and evidence configuration

The following is the planned P12 test harness configuration for T5/T6. Before running it, point the paths to the actual approved evaluation manifest and an unused output directory. The manifest cites immutable split/gallery and reference versions, artifact hashes, approved metric profiles, and exact commands needed for each component/evaluator. B supplies gallery/fit and replay IDs, C supplies the real query and relevance protocol, and A verifies them in the integration harness. Document actual runner commands in each task log rather than simulating a passed run when the harness or labeled data is unavailable.

```powershell
$env:TREE_CBIR_EVALUATION_MANIFEST = (Resolve-Path 'evaluation-manifest.json').Path
$env:TREE_CBIR_EVIDENCE_DIR = (Join-Path (Get-Location) 'outputs/evaluation/task-a/release-run')
.\.venv\Scripts\python.exe -m pytest -v tests/integration/test_end_to_end.py -k real_image_evaluation
.\.venv\Scripts\python.exe -m pytest -v tests/integration/test_end_to_end.py -k demo_acceptance
```

T5 may use the historical trunk runners for reproducibility from a separate workspace with preserved originals. The audit and AUTO evidence identify baselines and their execution commands. Neither historical evidence nor blocked references should be used to claim a fresh quality result. For T6, document one real upload, same-profile trace, indices 1–5 and comparison to the reference score, then separately exercise insufficient coverage or an error and check that the UI identifies it. Link actual screenshots or trace. When fixture demo mode is used to validate wiring, identify it as T3 evidence only.

## Foundation and missing tests

The preserved [03/08 run](../outputs/evaluation/team_preparation_03/validation.md) recorded **58 passed including local pgvector**, with **14 synthetic contract cases**. Existing tests cover preprocessing/utility checks, shared shape/ID/order/failure/context rules, trunk candidate/localization/refinement/V2 behavior, superpixel/region-feature mechanics, annotation/split integrity and a temporary pgvector table. They do not establish implementation of the remaining production feature blocks, gallery or UI. Two annotation/split tests read curated artifacts, and full suite reproduction must make them available.

| Accountable package | Tests still required |
| --- | --- |
| TASK-A | X0–X8 exact math including 15–60% band, multiple lower junctions, profile and validity checks; real P03 evaluation versus recorded targets; production 38-vector extractor, canonical preprocess parity, error isolation and cross-component metadata; end-to-end real evidence harness and regression. |
| TASK-B | X9–X19 mask/shape/HSV/skeleton and shared ROI coverage; real canopy/branch quality; valid-only fit cases, round trip and versions, migration/replay/rollback, all-507 accounting and query-fit reproducibility. |
| TASK-C | X20–X37 thickness/anchoring/edge/line and known-root exclusion; real root/context visibility and pixel quality; exact-reference score/rank, missing-evidence behavior, labeled fixture UI, real upload/UI trace and independently judged retrieval evaluation. |

Keep assertions and existing tests intact. 05/08 updates documentation only, and the 58-test evidence remains historical. [Evidence layout](acceptance_criteria.md#evidence-layout) · [Task handoff template](templates/task_handoff.md)
