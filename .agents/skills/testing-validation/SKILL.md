---
name: testing-validation
description: Run focused or integrated validation and record reproducible acceptance evidence.
---
1. Select the acceptance IDs and tier in `docs/acceptance_criteria.md` and `docs/testing.md`. Reuse the existing synthetic fixtures for unit and contract tests. Record exact commands, exit status, counts, timing and artifact/profile IDs. Run a full regression at integration or release rather than after each isolated edit.
2. Keep numeric correctness, actual-image quality and integrated functionality separate. Apply the frozen split, annotation and scoring protocol in `docs/team_preparation/evaluation_protocol.md`. A missing reference, credential, test selector or required skipped test leaves that verification blocked. Keep measured failures visible.
3. Use PASS, PARTIAL, FAIL, BLOCKED and owner-approved LIMITED for acceptance. Record runner skips as execution evidence. Preserve assertions and evidence, log the affected subtask and update its progress record before handing off.
