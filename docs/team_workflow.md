# Team workflow

The three packages and their readiness gates are defined in the [task index](tasks/README.md). Technical path accountability is defined in [shared-file ownership](team_preparation/shared_file_ownership.md). All packages remain **UNASSIGNED** at handoff.

## Claim and branch workflow

1. The project owner confirms claims in the team coordination channel or in a reviewed edit to the claim table in `docs/tasks/README.md`. Each member selects a distinct package. When a claim is accepted, record it in the index, package header and corresponding progress record. An agent prompt selecting a package does not replace owner confirmation.
2. Use the approved GitHub `develop` baseline after publication and remote-clone verification. See the [final handoff](team_preparation/final_handoff.md) for status and member clone commands. Check `git status --short` before switching branches and use a separate clean worktree when needed.
3. From a clean checkout after `develop` is available and its SHA is communicated, create only the claimed branch from it. Verify the base with `git log -1 --oneline develop`. Run one matching branch command:

   ```powershell
   git switch -c feature/trunk develop
   git switch -c feature/canopy-branch develop
   git switch -c feature/root-context develop
   ```

4. Use small commits with scope and stable checklist ID, for example `feat(trunk): preserve X7 basal band (TA-02)` or `test(retrieval): cover missing-group ties (TC-03)`. Stage explicit reviewed paths. Exclude `.env`, dataset binaries, sealed labels, caches, unapproved reports and large experiment outputs. Store approved artifacts through the team's internal channel and reference their hashes/versions. Preserve original evidence and checkpoints when adding experiments.
5. After remote publication is authorized in a later preparation step, submit PRs to `develop`. The description lists task and subtask IDs, stage/milestones, changed interfaces, validation commands and real/fixture status, data/artifact provenance and pending approvals. Request the accountable shared-file task and affected consumers for review. An independent Stage I PR may merge first when its test paths run without a producer. Avoid unrelated reformatting and coordinate database migrations and changing schemas with B.

## Coordination and integration order

- Open a shared-change request with the target path, behavior, compatibility plan, milestone and test. The accountable package owns the edit and coordinates review. Academic changes require the project owner's decision in the [decision register](team_preparation/specification_decisions.md). Do not fork a shared contract to bypass a pending decision.
- **M1:** Merge contract changes and compatible component adapters before merging consumer integration. All three packages can complete Stage I against fixtures. A publishes the pinned base and verifies synthetic contract tests. B shares the canopy ROI/storage shape, C shares root/context and retrieval-behavior expectations.
- **M2:** Merge accepted component implementations before A wires the production extractor. Give B and C the same extractor/profile ID and evidence. No live ingestion or online ranking depends on unfinished hand-coded mocks at this gate.
- **M3:** B migrates and ingests the approved manifest with the M2 extractor, publishes the compatible gallery/fit and replay instructions. C confirms exact candidate reads and normalization reuse. Stage I ranking/UI can advance in parallel with M2/M3 work.
- **M4:** C integrates real query and gallery inputs, runs evaluation and demo. B verifies the startup/replay procedure. A runs integrated regression and consolidates P12 and release records. [Milestone exit criteria and artifacts](tasks/README.md#stages-and-synchronization-milestones)

## Progress, evidence and interrupted work

### Execute and checkpoint

1. Read `AGENTS.md`, your task's entry point and required references, verify the confirmed claim and branch, then read `docs/tasks/progress/TASK-*.md` for that package. Reconcile the next incomplete item with its checklist. Inspect only the code and tests needed for the first authorized actionable subtask.
2. Implement inside the owned paths, run focused checks and diagnose and fix ordinary errors. Generate evidence before marking a subtask complete. Continue fixture-based or other independent authorized work when a real-data or integration gate is blocked. Follow the [experimentation budget](tasks/README.md#rules-for-all-packages) and the [Definition of Done](acceptance_criteria.md#definition-of-done).
3. After each meaningful subtask, update the stable checklist and applicable progress record. Use `docs/logs/TASK-A.md`, `docs/logs/TASK-B.md` or `docs/logs/TASK-C.md` for the detailed timeline, exact commands/results, touched paths, base SHA, versions, stage, dependencies, artifact locations/hashes, experiment-round ledger and approval references. Create the log on the first substantive work turn. Keep the progress record a short index of current state and the next action. Runner skips stay in the log; a skipped mandatory gate is `BLOCKED`.
4. Review `git status --short --branch`, the scoped diff and `git diff --check`. If local commits are available and authorized, stage explicit task paths and commit the scoped work with its checklist ID. Record the verified **code checkpoint SHA** in the progress record. When recording it in a subsequent documentation-only commit, keep that field pointing to the code checkpoint. Use the approved Git workflow for publication.
5. If commit is unavailable, record the base SHA and save a private scoped binary diff against `HEAD` plus exact copies of new untracked task files at their repository-relative paths. Store both with a checksum manifest and a recoverable location in the progress record. A Git diff alone omits new untracked files. Exclude secrets, other users' edits, sealed references and bulky datasets by default. Use the [evidence layout](acceptance_criteria.md#evidence-layout), and an approved internal store for data/large artifacts. Where neither checkpoint mechanism is available, record the exact workspace and recoverable state and flag that limitation.
6. Continue the next in-scope actionable item. Escalate unresolved academic semantics, incompatible interfaces, unavailable required data/credentials, persistent mandatory quality failure after the authorized budget, or ownership boundaries. Consolidate the [handoff](templates/task_handoff.md) when scope is complete, the user asks to stop, or only blocking work remains.

### Resume after interruption

1. Open the same task entry point and its progress record. Verify claim and branch with `git status --short --branch`. Compare `git log -5 --oneline`, `git diff` and `git diff --cached` with the recorded checkpoint. Read the newest relevant task-log entry if more evidence is needed.
2. If the checkout diverges, preserve all edits and resolve only the task's scoped state. To restore a patch checkpoint, use an isolated checkout at the recorded base and verify hashes. Check the saved patch with `git apply --check` before applying it there, then restore the recorded untracked files. Do not reset or force a checkout to match a log.
3. Confirm that required artifact versions are accessible. If the prior interruption left progress behind code, reconcile with the diff and test evidence. Continue the first actionable incomplete subtask, preserving verified work. Re-run only affected checks when content, configuration or environment changed or evidence is missing. An unverified subtask stays incomplete.
4. Update the progress record and checkpoint as you go. At handoff include verified readiness, blocked gates, exact next action and consuming package/profile versions. TASK-A coordinates the combined release record and academic evidence.
