---
name: database-development
description: Develop PostgreSQL persistence, normalization and compatible retrieval integration.
---
1. Read `docs/database.md`, the normalization/ranking contract in `docs/requirements.md`, `AC-P09`/`AC-P10` and assigned paths. TASK-B owns writes, schema, fit and candidate reads. TASK-C integrates reads and owns ranking. Use synthetic 38-position results or a fixture gallery before the production extractor/gallery exists.
2. Use parameterized queries, reproducible migrations and a local test database. Preserve raw and normalized values, explicit validity, valid-only fit metadata, idempotent replay and gallery/fit/profile compatibility. Keep credentials out of logs and require explicit authorization for destructive DB operations.
3. Verify round trips, rollback/replay, constant and missing dimensions with `docs/testing.md`. Compare retrieval against an independent exact reference at integration. Exchange versioned artifacts at M3/M4. A skipped database integration check is blocked acceptance, even if fixtures pass.
