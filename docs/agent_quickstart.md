# Agent quickstart

Use these prompts with Codex, Antigravity or another coding agent. Repository files carry the task context. Start at [AGENTS.md](../AGENTS.md), pick one package in the [task index](tasks/README.md) and obtain claim approval through the [team workflow](team_workflow.md#claim-and-branch-workflow). Read your package and its progress record before expanding the file scope.

## Preflight in a new checkout

1. Obtain the approved clone and `develop` base SHA. Check `git status --short --branch` and `git log -1 --oneline develop`. Verify the task documents, `src/tree_cbir/component_contracts.py` and `tests/unit/test_component_contracts.py` are present before creating the claimed branch. A checkout missing prepared sources cannot substitute undocumented code. Ask for the approved base rather than starting from the older `main` snapshot.
2. Reuse a verified working environment or follow the [pinned Python setup](../GUIDE.md#python-environment) to create one for this checkout.
3. Begin Stage I with the [shared synthetic fixtures](module_contract.md#isolated-development-and-verification). They require no real dataset or PostgreSQL. For later gates, restore authorized files using the [dataset and artifact guide](dataset_setup.md) and configure a [local PostgreSQL service](database.md#local-isolated-database). [Test tiers](testing.md)

The preparation workspace has local `main`. Publication of an approved `develop` base and transfer of clone-excluded artifacts are separate from this onboarding step. Record missing prerequisites as blockers on the affected gate. Where the task and checkout are authorized, continue independent work without those artifacts.

## Manual skill loading

Open each listed `SKILL.md` as repository text when it applies. Use the four common skills below for executing, developing features, validating or handing off. Add the database skill for B's persistence/fit or C's DB/retrieval work. TASK-A can consult it for final PostgreSQL integration. Agents need no skill discovery feature or platform-specific install.

| Responsibility | File |
| --- | --- |
| Subtask execution and scope | [phase-execution](../.agents/skills/phase-execution/SKILL.md) |
| Features, fixtures and shared masks | [feature-development](../.agents/skills/feature-development/SKILL.md) |
| Testing and evidence | [testing-validation](../.agents/skills/testing-validation/SKILL.md) |
| Checkpoint, resume and handoff | [phase-handoff](../.agents/skills/phase-handoff/SKILL.md) |
| PostgreSQL, normalization and retrieval integration | [database-development](../.agents/skills/database-development/SKILL.md) |

## Copy-ready prompts

### Start TASK-A

> Follow `AGENTS.md` and `docs/tasks/TASK-A.md`, starting at its agent entry point and `docs/tasks/progress/TASK-A.md`. Verify the claim and branch. Use the existing P03 baseline and recovery evidence. Execute the first actionable unchecked subtask within the permitted paths, test it, checkpoint it and continue authorized work. Record gates and blockers using the task handoff template.

### Start TASK-B

> Follow `AGENTS.md` and `docs/tasks/TASK-B.md`, starting at its agent entry point and `docs/tasks/progress/TASK-B.md`. Verify the claim and branch. Begin with the canopy/branch and synthetic extraction/database fixtures. Implement the first actionable unchecked subtask, run the matching tests, checkpoint it and continue authorized work. Wait for the production extractor only at its integration gate.

### Start TASK-C

> Follow `AGENTS.md` and `docs/tasks/TASK-C.md`, starting at its agent entry point and `docs/tasks/progress/TASK-C.md`. Verify the claim and branch. Use synthetic root/context inputs and an explicitly labeled fixture gallery for independent work. Execute the first actionable unchecked subtask, test and checkpoint it, then continue authorized work. Reserve real retrieval claims for the production evaluation.

### Resume an interrupted task

> Resume TASK-<A/B/C> using `AGENTS.md`, its task entry point, progress record and the resume section in `docs/team_workflow.md`. Reconcile the recorded checkpoint, current diff, latest log and evidence. Preserve existing edits. Continue the first actionable unchecked subtask and update the checkpoint once the affected verification is done.

### Run task acceptance

> Verify TASK-<A/B/C> against `docs/acceptance_criteria.md`, `docs/testing.md` and its current progress record. Run only the applicable tiers, keep formula, real-image and integrated results separate, and record the actual outcomes and evidence. Carry pending approvals forward. Use `docs/templates/task_handoff.md` to structure the summary in the task log.

### Prepare a Pull Request

> Verify the TASK-<A/B/C> branch and scoped diff. Follow `docs/team_workflow.md` and `docs/templates/task_handoff.md` to prepare the PR against approved `develop`. List subtask IDs, changed paths, test results, versions, reviewers and blockers. Keep credentials and protected artifacts out. Submit or push only if already authorized.

### Perform authorized cross-task integration

> Integrate the authorized M<1/2/3/4> work using `docs/team_workflow.md`, `docs/tasks/README.md`, `docs/module_contract.md` and the shared-file owner map. Verify producer artifacts, consumer compatibility and profile versions. Make coordinated edits within the approved scope, run the applicable gate tests and update task progress/evidence. Escalate incompatible interfaces or missing artifacts.
