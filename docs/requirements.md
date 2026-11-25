# Requirements

The academic assignment is to build a multimedia database system that stores and retrieves images of trees. `R` identifiers trace the assignment as reproduced in the **YÊU CẦU** section of Report 1. `E` identifiers identify engineering decisions for this project. The detailed formulas and unresolved parameters live in the [feature specification](feature_spec.md) and the [specification decisions](team_preparation/specification_decisions.md).

## Academic assignment

| ID | Requirement | Acceptance evidence |
| --- | --- | --- |
| R01 | Collect at least 500 images of mature woody trees. Each accepted image contains one complete, centered tree, photographed from a horizontal, side-on viewpoint with comparable framing, uniform output dimensions and comparable subject scale/aspect. File format is flexible. Describe similarities and differences observed in the dataset. | Manifest and automated decode/dimension checks for at least 500 accepted images, a visual review record for subject/framing, and examples of shared and differing traits. |
| R02 | Define features that describe both similarity and difference between trees. Explain each feature and its information value. | Ordered X0–X37 specification, worked examples, and evidence showing when groups help or hinder retrieval. |
| R03 | Implement the specified extraction algorithms/tools and a database to manage extracted image features. | Tested extraction and repeatable ingestion of the accepted corpus with database round trips for values, validity, group slices, and image references. |
| R04 | Accept a new tree image and return five images in decreasing order of content similarity. | End-to-end query from an image outside the gallery, with five distinct eligible gallery images and reproducible ranking. The insufficient-coverage failure case is tested separately. |
| R04A | Show the system block diagram and document each block's responsibilities, inputs, outputs, and the workflow. | An accurate architecture diagram, module and data contracts, and offline and online flows corresponding to the delivered implementation. |
| R04B | Illustrate intermediate feature values and similarity calculations during an image query. | A trace linking preprocessing and masks to raw and normalized values, validity, group distances, weights, coverage adjustments and final scores for a demonstrable query. |
| R04C | Evaluate the results achieved. | A reproducible evaluation on held-out queries with defined relevance judgments, comparisons, measurements, and documented limitations. |
| R05 | Demonstrate the working system. | A runnable local setup and demo showing ingestion, an unseen input query, ranked results and an inspectable calculation trace. |

## Project engineering requirements

| ID | Requirement |
| --- | --- |
| E01 | Standardize to 768 px wide × 1024 px high, 3:4, RGB. Apply EXIF orientation, preserve source files, record transformations and checksums, and use the same pixel contract for ingestion and queries. For the corpus, review the subject and framing separately from technical conformity. |
| E02 | Preserve the ordered 38-dimensional handcrafted representation and slices of size 9, 8, 3, 6 and 12. Keep ROI/mask production, numeric extraction and semantic interpretation distinct. Record validity per dimension and provenance for extraction configuration. |
| E03 | Persist image IDs, file references, raw and normalized vectors, validity, five group slices and versioned normalization provenance in the local PostgreSQL/pgvector system. Keep credentials private. Preserve reproducibility across ingestion, database writes and query evaluation. |
| E04 | Fit per-dimension Min–Max using valid values from the indexed database fit corpus. Freeze parameters per index version and reuse them for queries. Explicitly handle constant dimensions, dimensions with no valid observations, and observations outside the fitted range. |
| E05 | Use five size-adjusted group distances on shared valid dimensions, and nonnegative group weights summing to one. Prioritize trunk and canopy, and use context as supplementary evidence. Require adequate shared evidence and apply the same configured scoring policy to every candidate for a query. A missing dimension/group must never improve a candidate's score or eligibility. Preserve deterministic ordering at ties and report inadequate coverage explicitly. |
| E06 | Use held-out queries for evaluation and keep annotations and evaluation labels out of runtime inference. Freeze extraction, normalization, weights and thresholds before evaluating the holdout. Record data and config versions, failed queries, coverage, latency and limitations alongside quality results. |
| E07 | Enforce the algorithm policy below. Document any deviation from the report's proposed methodology with evidence, impact on the feature contract, and approval where a definition changes. |
| E08 | Keep presentation, services, core processing and persistence separated. Provide a reproducible local setup, a block diagram, and a query trace in the demo. |

The 768 × 1024 convention and five-group feature design come from Report 1. Local stack and contracts are engineering decisions. See the [traceability matrix](team_preparation/requirements_traceability.md) for package and phase references.

## Normalization and ranking contract

1. Retain finite raw values and explicit validity. A valid zero is an observation. Invalid positions are excluded from fitting and comparison even if a storage format uses a zero placeholder. Retain explicit validity in persisted and exposed data.
2. For each dimension `k`, fit `min_k` and `max_k` only from valid observations in the indexed fit corpus. Store the bounds, valid count, eligibility flag, fit manifest ID and extractor/config version. A dimension with no observations is unavailable. A valid constant dimension is normalized to zero and excluded from discrimination and coverage denominators. A query with a different raw value on that dimension may record the discrepancy but uses the same normalization state until a new index version is fitted.
3. For active dimensions, compute `z_k = (x_k − min_k)/(max_k − min_k)` for valid data. Use the same fit artifact for database and query, with the proposed convention of clipping to `[0,1]` and recording out-of-range diagnostics. Store raw and normalized values so clipping remains auditable. A raw-invalid query observation stays invalid. A raw-valid observation in an unavailable dimension has no normalized score.
4. Compute five distances, using only dimensions valid in both images for the measured differences and using the same frozen set of active dimensions for all candidates. Report per-group shared counts and coverage. All comparisons use compatible feature and fit versions. Groups with no active dimensions are handled at profile validation, with zero configured weight and the remaining weights specified in advance. A per-image absence never triggers weight redistribution. Require active positive-weight evidence from trunk and canopy in the index profile.
5. Integrate using `D_total = Σ_g w_g D_g`. The candidate reference policy, mathematical coverage adjustment and open choices are in [A21–A23](team_preparation/specification_decisions.md#normalization-and-ranking-reference-policy). Define `similarity = 1 − D_total` for the proposed bounded policy. Rank by descending similarity, then ascending stable image ID. Return five distinct eligible images for the successful case. If fewer than five qualify, show the eligible records, flag inadequate coverage and give the available count. A query with no comparable evidence reports that outcome. Do not fill the list with unsupported matches. This degraded case is an engineering policy and does not transfer the R04 acceptance goal to a partial list.

## Experimental evaluation

- Version the gallery, unseen query split, relevance criteria, relevance judgments, extractor, fit artifact, and ranking profile. Define content relevance independently of the system output. Use the same query and gallery set for comparisons and prevent exact duplicates and leakage between development and held-out evaluation.
- Record per-query results, relevance decisions, per-feature validity and failure cases. Report Precision@5 as relevant results in five slots divided by five, and Recall@5 when the number of relevant gallery images is known and positive. State how unjudged results and insufficient-coverage queries are handled. Report successful-query quality and end-to-end success/coverage separately with denominators, latency on a declared environment, and examples of visual or scoring failures.
- Compare complete-vector retrieval with group-only and group-ablation runs. Include weight sensitivity and examples where context helps or dominates. Keep coverage rules and variant configurations explicit so differences in which queries qualify are visible. Validate segmentation and feature math separately before attributing ranking differences to information value. Calibration and quality acceptance gates remain open in [A24](team_preparation/specification_decisions.md#ambiguity-register).

## Algorithm policy

Classical image processing, handcrafted descriptors, morphology, clustering, KNN, Random Forest and other supervised methods trained on group-owned data, and standard numerical/image-processing libraries are allowed. Training labels may be used in training, calibration and evaluation within their designated splits. Runtime extraction accepts image data and a versioned configuration or an approved model fitted on group-owned data.

Pretrained vision models, external AI inference services, hardcoded filename-specific rules in production, ground-truth annotations as production inference inputs and learned embeddings in place of the 38 dimensions are prohibited. Preserve the proposed segmentation methodology where practical. Compare deviations using the same interface and evaluation split, and record the baseline, rationale, and impact on measurement semantics before adoption.
