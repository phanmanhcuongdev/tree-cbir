# tree-cbir

Local Multimedia Database Systems course project for storing and retrieving mature woody-tree images using 38 handcrafted features.

This filtered snapshot is a collaborative development baseline. P01/P02 are accepted, the hybrid trunk pipeline is partial, and the shared contracts and synthetic fixtures are ready. The production CBIR application is still under development. See [implementation status](docs/status.md) and the [final handoff](docs/team_preparation/final_handoff.md).

**Start here:** Read [AGENTS.md](AGENTS.md), check availability in the [task index](docs/tasks/README.md), and follow the [claim and branch workflow](docs/team_workflow.md#claim-and-branch-workflow) for one package.

| Package | What it covers | Resume from |
| --- | --- | --- |
| [TASK-A](docs/tasks/TASK-A.md#agent-entry-point) | Trunk, extraction and integration | [A progress](docs/tasks/progress/TASK-A.md) |
| [TASK-B](docs/tasks/TASK-B.md#agent-entry-point) | Canopy, branches, normalization and database | [B progress](docs/tasks/progress/TASK-B.md) |
| [TASK-C](docs/tasks/TASK-C.md#agent-entry-point) | Roots, context, retrieval and UI | [C progress](docs/tasks/progress/TASK-C.md) |

[Agent prompts and local setup](docs/agent_quickstart.md) · [Implementation status](docs/status.md) · [Authoritative references](AGENTS.md#authoritative-references) · [Testing](docs/testing.md) · [Acceptance](docs/acceptance_criteria.md)

[Install from a clean checkout](GUIDE.md#python-environment) · [Dataset and artifact setup](docs/dataset_setup.md) · [Publication checklist](docs/team_preparation/handoff_checklist.md)

Dataset-independent smoke: `./.venv/Scripts/python.exe -m pytest -v tests/unit/test_component_contracts.py`. Restore authorized external artifacts only for the corresponding task or integration gate.

## Dataset Download and Setup

1. Sign in to Google Drive with your authorized team account and download the JPEGs from [500 Ảnh](https://drive.google.com/drive/folders/1GcqBCnZpZZ9-VF6Kf1MTsOCyAioII_4h?usp=drive_link), the official source. Extract the download into a temporary folder and keep both copies of `475.jpg` separate until you check their hashes.
2. Follow the [dataset setup guide](docs/dataset_setup.md#obtain-the-authorized-files) to match source SHA-256 values, place the 507 accepted originals directly under `data/processed/`, and generate `data/standardized/`. Alternatively, restore the verified `DATA-STD` archive from the project owner.
3. From the repository root run `./.venv/Scripts/python.exe scripts/verify_dataset.py`. Expect 507 JPEG RGB images at 768 × 1024 px. Keep all downloaded and generated images outside Git.
