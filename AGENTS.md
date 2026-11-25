# tree-cbir agent instructions

Build a local modular monolith that stores and retrieves mature woody-tree images using the fixed handcrafted X0–X37 vector. Preserve the accepted P01/P02 foundation, interfaces and user work.

## Start or resume

1. Open the [task index](docs/tasks/README.md), select TASK-A/B/C and verify the owner's claim approval and task branch in the [team workflow](docs/team_workflow.md#claim-and-branch-workflow). A selection alone does not assign a person or authorize implementation. The [copy-ready prompts](docs/agent_quickstart.md) work with any coding agent.
2. Read the selected package's agent entry point, [project status](docs/status.md) and the corresponding `docs/tasks/progress/TASK-*.md`. On resume, follow its checkpoint and next incomplete subtask. Read the other package documents only where an approved integration requires their interfaces.
3. Read the relevant canonical sections listed below and manually open the task's `.agents/skills/<name>/SKILL.md` files. The [skill map](docs/agent_quickstart.md#manual-skill-loading) requires no automatic discovery. Then inspect the relevant code and targeted tests for the first actionable subtask.

## Authoritative references

| Concern | Source |
| --- | --- |
| Academic requirements and algorithm policy | [Requirements](docs/requirements.md) |
| Feature semantics and validity | [Feature specification](docs/feature_spec.md) |
| Architecture and shared interfaces | [Architecture](docs/architecture.md) and [module contract](docs/module_contract.md), respectively |
| Assigned work and permitted edits | [Selected task](docs/tasks/README.md) and [shared-file owner map](docs/team_preparation/shared_file_ownership.md) |
| Acceptance and test procedure | [Acceptance criteria](docs/acceptance_criteria.md) and [testing](docs/testing.md), respectively |
| Git, collaboration, checkpoint and resume | [Team workflow](docs/team_workflow.md) |
| Technical decisions and owner approval | [Specification decision register](docs/team_preparation/specification_decisions.md) |
| Implementation and current task state | [Project status](docs/status.md) and [task progress records](docs/tasks/progress/), respectively |

If sources conflict, report the references and impact, then route the decision through the accountable package or project owner. Pending decisions remain pending. Continue unrelated authorized work while the affected change is blocked.

## Work within the task

- For real-image work, use the official [500 Ảnh](https://drive.google.com/drive/folders/1GcqBCnZpZZ9-VF6Kf1MTsOCyAioII_4h?usp=drive_link) Drive dataset or the owner's verified `DATA-STD` archive. Follow the [dataset verification guide](docs/dataset_setup.md#obtain-the-authorized-files). If access or checksums fail, record the gap and request the authorized version. Do not collect replacement images.
- Edit only authorized task paths. Route shared-file changes through the accountable package. Keep presentation, services, core image processing and persistence separate. Preserve typed contracts, RGB `(1024, 768, 3)` `uint8`, bool masks, X0–X37 order and explicit validity. Use parameterized SQL. Synthetic observations belong in explicit test/fixture paths.
- Use classical CV, handcrafted features, and supervised models trained only on authorized group-owned data. Prohibit pretrained models, external AI inference, filename-specific production rules, ground-truth inputs to production, evaluation leakage and fabricated evidence. Preserve source images and frozen results. Keep `.env` and credentials private.
- Implement and fix ordinary failures within scope. Reuse utilities, the audit, previous test evidence and synthetic fixtures. Prefer targeted tests and reserve full regression for substantive integration or release checkpoints. Reuse working dependencies and reports. At most three meaningful additional algorithm-improvement rounds per package by default. Stop ineffective rounds early and keep holdouts out of tuning.
- Follow the [execution and resume workflow](docs/team_workflow.md#progress-evidence-and-interrupted-work). After each meaningful subtask, record commands, results, evidence, changed paths and a recoverable checkpoint. Update the task progress record and continue the next authorized actionable subtask. Use [Definition of Done](docs/acceptance_criteria.md#definition-of-done) and the [handoff template](docs/templates/task_handoff.md). Separate mathematical, real-image and integrated acceptance. Only the project owner can approve `LIMITED`.
- Stop when the authorized scope is complete, the user asks to stop, or no safe in-scope work remains. Escalate unresolved academic semantics, incompatible shared interfaces, missing required data/credentials, unmet quality gates after the experiment budget, or out-of-scope changes. Preserve partial work and state the next action. Push and submit PRs only in the authorized collaboration workflow.
