# Task allocation and coverage matrix — 04/08

Every row has one accountable package. Supporting packages contribute named artifacts or reviews. This is technical allocation only. The three packages remain **UNASSIGNED** to people. [TASK-A](../tasks/TASK-A.md) · [TASK-B](../tasks/TASK-B.md) · [TASK-C](../tasks/TASK-C.md) · [Executable contracts](../module_contract.md)

Acceptance references `TA-*`, `TB-*` and `TC-*` resolve to the respective package checklists. M1–M4 are defined in the [task index](../tasks/README.md#stages-and-synchronization-milestones). Feature fixtures and academic gates are in the [feature specification](../feature_spec.md) and [requirements](../requirements.md). P01/P02 remain accepted input foundations.

## Phase coverage

| Phase | Accountable | Supporting | Dependency | Expected deliverable | Acceptance |
| --- | --- | --- | --- | --- | --- |
| P03 | TASK-A | TASK-B, TASK-C | P02 and existing AUTO/V2/V3 evidence | Versioned trunk observation and X0–X8 with numerical and actual-data validation | TA-01–03, TA-06, M1/M2 |
| P04 | TASK-B | TASK-A | P02, optional trunk contract at M1 | Canopy ROI/foliage and X9–X16, including optional-trunk fallback | TB-01, TB-05, M1/M2 |
| P05 | TASK-B | TASK-A | P04 shared ROI and optional trunk | Branch observation, skeleton and X17–X19 | TB-02, TB-05, M1/M2 |
| P06 | TASK-C | TASK-A | P02, optional trunk base and measured width | Root observation and X20–X25 with explicit fallback/quality | TC-01, TC-05, M1/M2 |
| P07 | TASK-C | TASK-A, TASK-B | Available trunk, canopy, branch and root masks | Ground/background exclusions, diagnostics and X26–X37 | TC-02, TC-05, M1/M2 |
| P08 | TASK-A | TASK-B, TASK-C | M1 compatible component observations | One registered extractor profile, 38D assembly, provenance and failure isolation | TA-04–06, M2 |
| P09 | TASK-B | TASK-A, TASK-C | Fixture or M2 extractor, accepted corpus | Schema, Min–Max, replayable gallery ingestion and candidate reads | TB-03–04, TB-06–07, M3 |
| P10 | TASK-C | TASK-A, TASK-B | Synthetic vectors or M2/M3 profile and gallery | Exact eligible Top-5, validity-aware scoring and trace | TC-03, TC-06, M4 |
| P11 | TASK-C | TASK-A, TASK-B | Retrieval service and fixture or M3 data | Query UI, actual intermediate results and explicit degraded/fixture views | TC-04, TC-07, M4 |
| P12 | TASK-A | TASK-B, TASK-C | M2–M4 and all package evidence | Combined extraction, batch/DB, retrieval and demo evaluation and release verification | TA-06–07, TB-07, TC-07 |

## Academic and engineering requirement coverage

| Requirement | Accountable | Supporting | Dependency | Expected deliverable | Acceptance |
| --- | --- | --- | --- | --- | --- |
| R01 | TASK-B | TASK-A, TASK-C | Accepted P02 and A24 framing rule | Versioned ≥500-image manifest, valid format/size, visual framing evidence, trait descriptions | TB-06 and R01 acceptance evidence |
| R02 | TASK-A | TASK-B, TASK-C | Feature spec and held-out relevance protocol | Combined inventory, formulas and group information value with examples and ablation | TA-02, TA-07, TC-07 and R02 |
| R03 | TASK-A | TASK-B, TASK-C | P03–P09 | Integrated extractor and B's compatible persistence and corpus ingest | TA-05, TB-06 and R03 |
| R04 | TASK-C | TASK-A, TASK-B | M2/M3 and approved ranking profile | Real unseen query with exact, eligible Top-5 and deterministic ties | TC-06–07 and R04 |
| R04A | TASK-A | TASK-B, TASK-C | M2–M4 actual interfaces | Block diagram, module I/O and matching offline/online workflows | TA-07 and R04A |
| R04B | TASK-C | TASK-A, TASK-B | Extractor diagnostics, fit and final ranking profile | Recomputable intermediate extraction/normalization and similarity trace | TC-04, TC-06–07 and R04B |
| R04C | TASK-A | TASK-B, TASK-C | Three P12 workstreams and frozen protocols | Combined reproducible results with quality gates and failures identified | TA-06–07, TB-07, TC-07 and R04C |
| R05 | TASK-C | TASK-A, TASK-B | M2 extractor, B demo gallery/setup and A release candidate | Reproducible live demo including query and score trace | TC-07 and R05 |
| E01 | TASK-A | TASK-B | Accepted P02 contracts and R01 data | Preserve canonical preprocessing and source/transform provenance across clients | TA-05 and TB-06 |
| E02 | TASK-A | TASK-B, TASK-C | Shared feature and component types | 38 fixed positions, validity, group slices and extraction provenance | TA-04–05 |
| E03 | TASK-B | TASK-A, TASK-C | Schema, corpus manifest and group outputs | Local database persistence with validity and compatible paths/versions | TB-03, TB-06 |
| E04 | TASK-B | TASK-A, TASK-C | Indexed valid corpus observations | Frozen Min–Max fit with constant/unavailable/out-of-range behavior | TB-04, TB-06–07 |
| E05 | TASK-C | TASK-A, TASK-B | Compatible normalized gallery and approved scoring | Group distance, weights, monotone missingness, exact order and eligibility | TC-03, TC-06 |
| E06 | TASK-A | TASK-B, TASK-C | Development/holdout manifests and frozen versions | Combined evaluation with leakage controls and separate quality/coverage | TA-06–07, TB-07, TC-07 |
| E07 | TASK-A | TASK-B, TASK-C | Report methods and approved deviations | Recorded approaches and evidence for alternative algorithms | TA-03, TA-07, B/C experiment logs |
| E08 | TASK-A | TASK-B, TASK-C | Modular monolith and local setup | Boundary review, diagram and a repeatable local demonstration with trace | TA-07, TB-07, TC-07 |

## Feature coverage

| Feature | Accountable | Supporting | Dependency | Expected deliverable | Acceptance |
| --- | --- | --- | --- | --- | --- |
| X0 | TASK-A | — | Trunk mask, geometry and approved profile | Trunk visibility and validity | TA-02, X0 mathematical fixture |
| X1 | TASK-A | — | Trunk mask, geometry and approved profile | Bark descriptor L* or approved equivalent and validity | TA-02, X1 mathematical fixture |
| X2 | TASK-A | — | Trunk mask, geometry and approved profile | Bark descriptor a* or approved equivalent and validity | TA-02, X2 mathematical fixture |
| X3 | TASK-A | — | Trunk mask, geometry and approved profile | Bark descriptor b* or approved equivalent and validity | TA-02, X3 mathematical fixture |
| X4 | TASK-A | — | Trunk mask, geometry and approved profile | Relative trunk width and validity | TA-02, X4 mathematical fixture |
| X5 | TASK-A | — | Trunk mask, geometry and approved profile | Absolute inclination and validity | TA-02, X5 mathematical fixture |
| X6 | TASK-A | — | Trunk mask, geometry and approved profile | Relative curvature and validity | TA-02, X6 mathematical fixture |
| X7 | TASK-A | — | Trunk mask, geometry and approved profile | Median basal runs and validity | TA-02, X7 mathematical fixture |
| X8 | TASK-A | — | Trunk mask, geometry and approved profile | Lower-trunk junction count and validity | TA-02, X8 mathematical fixture |
| X9 | TASK-B | TASK-A | Canopy ROI and foliage mask; optional trunk | Foliage area ratio and validity | TB-01, X9 mathematical fixture |
| X10 | TASK-B | TASK-A | Canopy ROI and foliage mask; optional trunk | Mean hue and validity | TB-01, X10 mathematical fixture |
| X11 | TASK-B | TASK-A | Canopy ROI and foliage mask; optional trunk | Mean saturation and validity | TB-01, X11 mathematical fixture |
| X12 | TASK-B | TASK-A | Canopy ROI and foliage mask; optional trunk | Mean value and validity | TB-01, X12 mathematical fixture |
| X13 | TASK-B | TASK-A | Canopy ROI and foliage mask; optional trunk | Canopy solidity and validity | TB-01, X13 mathematical fixture |
| X14 | TASK-B | TASK-A | Canopy ROI and foliage mask; optional trunk | Canopy aspect ratio and validity | TB-01, X14 mathematical fixture |
| X15 | TASK-B | TASK-A | Canopy ROI and foliage mask; optional trunk | Canopy circularity and validity | TB-01, X15 mathematical fixture |
| X16 | TASK-B | TASK-A | Canopy ROI and foliage mask; optional trunk | Vertical widest-row position and validity | TB-01, X16 mathematical fixture |
| X17 | TASK-B | TASK-A | Selected canopy ROI and branch mask or skeleton | Branch exposure ratio and validity | TB-02, X17 mathematical fixture |
| X18 | TASK-B | TASK-A | Selected canopy ROI and branch mask or skeleton | Relative skeleton length and validity | TB-02, X18 mathematical fixture |
| X19 | TASK-B | TASK-A | Selected canopy ROI and branch mask or skeleton | Branch junction count and validity | TB-02, X19 mathematical fixture |
| X20 | TASK-C | TASK-A | Root observation and optional reliable trunk geometry | Exposed root-area ratio and validity | TC-01, X20 mathematical fixture |
| X21 | TASK-C | TASK-A | Root observation and optional reliable trunk geometry | Relative lateral spread and validity | TC-01, X21 mathematical fixture |
| X22 | TASK-C | TASK-A | Root observation and optional reliable trunk geometry | Relative thickness using trunk width and validity | TC-01, X22 mathematical fixture |
| X23 | TASK-C | TASK-A | Root observation and optional reliable trunk geometry | Relative skeleton length and validity | TC-01, X23 mathematical fixture |
| X24 | TASK-C | TASK-A | Root observation and optional reliable trunk geometry | Main root departures and validity | TC-01, X24 mathematical fixture |
| X25 | TASK-C | TASK-A | Root observation and optional reliable trunk geometry | Root edge density and validity | TC-01, X25 mathematical fixture |
| X26 | TASK-C | TASK-A, TASK-B | Ground ROI/mask with tree and root exclusions | Ground green fraction and validity | TC-02, X26 mathematical fixture |
| X27 | TASK-C | TASK-A, TASK-B | Ground ROI/mask with tree and root exclusions | Ground brown fraction and validity | TC-02, X27 mathematical fixture |
| X28 | TASK-C | TASK-A, TASK-B | Ground ROI/mask with tree and root exclusions | Ground gray fraction and validity | TC-02, X28 mathematical fixture |
| X29 | TASK-C | TASK-A, TASK-B | Ground ROI/mask with tree and root exclusions | Ground grayscale variance and validity | TC-02, X29 mathematical fixture |
| X30 | TASK-C | TASK-A, TASK-B | Ground ROI/mask with tree and root exclusions | Ground edge density and validity | TC-02, X30 mathematical fixture |
| X31 | TASK-C | TASK-A, TASK-B | Ground ROI/mask with tree and root exclusions | Ground line density and validity | TC-02, X31 mathematical fixture |
| X32 | TASK-C | TASK-A, TASK-B | Background mask with tree, root and ground exclusions | Background blue fraction and validity | TC-02, X32 mathematical fixture |
| X33 | TASK-C | TASK-A, TASK-B | Background mask with tree, root and ground exclusions | Background green fraction and validity | TC-02, X33 mathematical fixture |
| X34 | TASK-C | TASK-A, TASK-B | Background mask with tree, root and ground exclusions | Background white fraction and validity | TC-02, X34 mathematical fixture |
| X35 | TASK-C | TASK-A, TASK-B | Background mask with tree, root and ground exclusions | Background grayscale variance and validity | TC-02, X35 mathematical fixture |
| X36 | TASK-C | TASK-A, TASK-B | Background mask with tree, root and ground exclusions | Background edge density and validity | TC-02, X36 mathematical fixture |
| X37 | TASK-C | TASK-A, TASK-B | Background mask with tree, root and ground exclusions | Background line density and validity | TC-02, X37 mathematical fixture |

## Production module coverage

Complete path authority, including tests, scripts, environment and shared docs, is in [shared-file ownership](shared_file_ownership.md). This view maps key production seams to a deliverable and an acceptance gate.

| Production module or seam | Accountable | Supporting | Dependency | Expected deliverable | Acceptance |
| --- | --- | --- | --- | --- | --- |
| `src/tree_cbir/preprocessing.py` and non-visual shared `utils/` | TASK-A | TASK-B, TASK-C | Accepted P02 | Stable image/utility contract for both paths | TA-05, P02 regression |
| `src/tree_cbir/models.py`, `config.py`, `component_contracts.py` | TASK-A | TASK-B, TASK-C | 03/08 contracts | Validated shared types, order, ownership and provenance | TA-04, M1 |
| `src/tree_cbir/segmentation/trunk.py`, related `trunk_*.py` and `features/trunk.py` | TASK-A | TASK-B, TASK-C | RGB and baseline | Trunk mask and canonical geometry/feature observations | TA-01–03, TA-06 |
| `src/tree_cbir/segmentation/canopy.py`, `segmentation/branch.py`, `features/canopy.py`, `features/branch.py` | TASK-B | TASK-A, TASK-C | Shared canopy ROI and optional trunk | Independent canopy/branch observations | TB-01–02, TB-05 |
| `src/tree_cbir/segmentation/root.py`, `segmentation/context.py`, `features/root.py`, `features/context.py` | TASK-C | TASK-A, TASK-B | Optional upstream measurements and masks | Reliable root/context outputs and exclusion/fallback diagnostics | TC-01–02, TC-05 |
| `src/tree_cbir/extractor.py` | TASK-A | TASK-B, TASK-C | M1 component outputs | Shared production extraction entry point and profile | TA-04–05, M2 |
| `src/tree_cbir/database.py`, `sql/`, `compose.yaml` | TASK-B | TASK-A, TASK-C | Local PostgreSQL/pgvector and finalized schema | Tested migrations, versioned gallery, setup, read contract | TB-03, TB-06, M3 |
| `src/tree_cbir/normalization.py` | TASK-B | TASK-A, TASK-C | Canonical measurements and validity | Fit/transform API with frozen gallery artifact | TB-04, TB-07 |
| `src/tree_cbir/services/dataset.py`, `scripts/build_dataset.py` | TASK-B | TASK-A, TASK-C | P02 manifest and M2 extractor | Repeatable full batch entry point and metrics | TB-04, TB-06, M3 |
| `src/tree_cbir/similarity.py`, `services/retrieval.py` | TASK-C | TASK-A, TASK-B | M2/M3 compatible versions | Exact Top-5 and trace with coverage and degraded outcomes | TC-03, TC-06 |
| `app.py`, `src/tree_cbir/utils/visualization.py` | TASK-C | TASK-A, TASK-B | Retrieval trace and gallery | Demo UI and intermediate feature visualization | TC-04, TC-07, M4 |
| `scripts/evaluate.py` | TASK-C | TASK-A, TASK-B | Held-out evaluation protocol and real gallery | Retrieval quality and ablation runner with frozen inputs | TC-07, P12 evidence |
| `tests/conftest.py`, `tests/unit/test_component_contracts.py`, shared dependency manifests and release integration | TASK-A | TASK-B, TASK-C | All shared compatibility paths | Reusable synthetic fixtures and release verification | TA-04, TA-07 |

## Final demonstration and report deliverables

| ID / deliverable | Accountable | Supporting | Dependency | Expected artifact | Acceptance |
| --- | --- | --- | --- | --- | --- |
| D01 · Corpus and examples | TASK-B | TASK-A, TASK-C | P02 and final manifest review | Accepted-gallery manifest, framing/trait evidence and counts | R01, TB-06 |
| D02 · Architecture and extraction report | TASK-A | TASK-B, TASK-C | M2 component profiles | Actual diagram, workflow, X0–X37 mapping, failure behavior and measured examples | R02/R04A, TA-05–07 |
| D03 · Extraction validation | TASK-A | TASK-B, TASK-C | Algorithm freeze and evaluation records | Separate formula/segmentation checks, actual-data coverage and latency | P12, TA-06 |
| D04 · Reproducible database and demo startup | TASK-B | TASK-A, TASK-C | M2 and accepted corpus | Migration, seed/ingest and startup commands with populated real gallery and fit IDs | R03/R05, TB-06–07 |
| D05 · Storage/batch evaluation | TASK-B | TASK-A, TASK-C | M3 replay | Round trip, integrity and normalized validity, errors/recovery and throughput | P12, TB-07 |
| D06 · Real query and intermediate trace | TASK-C | TASK-A, TASK-B | M2/M3 production versions | Real UI output, five ranked images, masks, values, validity, distances and contribution trace | R04/R04B, TC-06–07 |
| D07 · Held-out ranking and evidence | TASK-C | TASK-A, TASK-B | Frozen gallery/query/profile and judgments | Precision@5, applicable Recall@5, ablations, coverage, latency and limitations | R04C, TC-07 |
| D08 · Observed demonstration | TASK-C | TASK-A, TASK-B | M4 and B startup recipe | Reproducible setup walkthrough using real data, successful query and explicit degraded example | R05, TC-07 |
| D09 · Release and academic evidence bundle | TASK-A | TASK-B, TASK-C | D01–D08 and owner decisions | Pinned commit/profile manifest, integrated test results, all three evidence logs, known limitations and approval record | P12, TA-07 |

## Evaluators for pending decisions

The [decision register](specification_decisions.md#ambiguity-register) controls semantics. **Owner sign-off** below is required before an affected choice becomes a production feature, label, ranking policy or acceptance claim. It leaves fixtures and invariant implementation work available immediately. **Calibrate** means version the setting and attach development results before release. Reviewer/owner decisions are distinct from package evaluation responsibility.

| Decision | Accountable evaluator | Supporting | Dependency | Expected evidence or recommendation | Acceptance |
| --- | --- | --- | --- | --- | --- |
| A01 | TASK-A | TASK-B, TASK-C | Trunk references and quality metadata | Expected-height estimator and clipping/validity policy | Owner sign-off on estimator/policy, then calibrated freeze |
| A02 | TASK-A | TASK-C | Bark masks and source meaning | Lab median comparison vs legacy HSV and version/migration consequence | Owner sign-off before production X1–X3 profile |
| A03 | TASK-B | TASK-A, TASK-C | Foliage HSV and hue fixtures | Preserve physical-degree arithmetic mean. Evaluate hue-label bands and wrap diagnostics | Calibrate labels, owner sign-off to enable ambiguous labels or alter hue math |
| A04 | TASK-A | TASK-B, TASK-C | Canonical grid and spec | One width/height/row convention and regression fixtures | Shared contract review |
| A05 | TASK-A | TASK-C | Reliable trunk rows and base | Select sampling/OLS support and basal-run reliability | Calibrate with fixed X7 band |
| A06 | TASK-A | — | Straight, tilted and curved dev examples | Curvature label boundary and performance | Calibrate, record threshold |
| A07 | TASK-A | TASK-B, TASK-C | Shared skeleton math | Common graph convention and component pruning evidence | Shared contract review, calibrate pruning per component |
| A08 | TASK-A | TASK-B, TASK-C | Shared junction fixture semantics | Common merging convention and supported regional policies | Shared contract review, calibrate noise support |
| A09 | TASK-B | TASK-A | Canopy fixtures/reference masks | Hull, matching perimeter/area and minimum support results | Calibrate and honor canonical formula |
| A10 | TASK-B | TASK-A, TASK-C | Optional trunk and canopy/branch contract | Versioned ROI fallback and evidence | Calibrate, demonstrate M1/M2 behavior |
| A11 | TASK-B | TASK-A | Labeled branch visibility/topology | Separate area/length thresholds and label precedence | Owner sign-off on semantics, calibrate thresholds |
| A12 | TASK-C | TASK-A | Reliable base/width and root masks | Root ROI geometry, support and fallback policy | Calibrate and preserve unavailable/uncertain states |
| A13 | TASK-C | TASK-A | Thickness annotations and skeleton support | Compare supported root thickness measurements | Calibrate sample support |
| A14 | TASK-C | TASK-A, TASK-B | Anchored root topology | Main-root count rule, minimum links and ambiguous cases | Owner sign-off on counting interpretation, then calibrate |
| A15 | TASK-C | TASK-B, TASK-A | Context colors and B's foliage appearance labels | Versioned predicates and their thresholds, with B validating foliage labels | Calibrate, owner sign-off for ambiguous categories |
| A16 | TASK-C | TASK-A, TASK-B | Shared gray/edge utility | Versioned Canny settings and division of shared versus local use | Calibrate, request changes to shared utilities via A |
| A17 | TASK-C | TASK-A | Context masks and straight-line fixtures | Detector settings and clipped unique-support validation | Calibrate and document retained line convention |
| A18 | TASK-C | TASK-A, TASK-B | Label candidates and normalized root profile | Assemble root/context score and tie/unknown policy; A/B supply trunk/canopy/branch decisions | Owner sign-off before enabling semantic scores, then calibrate |
| A19 | TASK-C | TASK-A, TASK-B | Root and above-ground masks | Root exclusion interpretation and coverage/fallback evidence | Owner sign-off on explicit background correction; retain shared guard |
| A20 | TASK-A | TASK-B, TASK-C | Per-component coverage and quality | Common validity rules; component evidence for thresholds/reasons | Shared contract review, calibrate by group |
| A21 | TASK-B | TASK-A, TASK-C | Accepted indexed fit corpus | Valid-only Min–Max and locked clipping/constant/unavailable handling | TB-04, TB-06, version increment on change |
| A22 | TASK-C | TASK-A, TASK-B | Retrieval dev corpus and bounded distance fixtures | Exact reference metric comparison and missingness results | Owner sign-off on production distance profile |
| A23 | TASK-C | TASK-A, TASK-B | Score evidence, dev coverage and morphology gate | Proposed weights, eligibility and degraded behavior | Owner sign-off on profile before evaluation freeze |
| A24 | TASK-A | TASK-B, TASK-C | B framing review, A segmentation results, C relevance/evaluation protocol | Consolidated release thresholds, corpus/holdout checks and demo criteria | Owner sign-off before final framing acceptance and held-out run |
| A25 | TASK-A | TASK-B, TASK-C | Legacy prototypes and canonical feature tests | Versioned change/compatibility record for trunk differences | Owner sign-off for any semantic deviation, genuine formula fixes tested |

Do not wait for owner decisions to write invariant calculations, test explicit experimental profiles or integrate shape-compatible fixtures. Obtain decisions before committing a production semantics change or freeze. A records decisions and B/C update dependent profiles and evidence.
