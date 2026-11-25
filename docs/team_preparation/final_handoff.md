# Final team handoff — 08/08

**Publication scope:** The project owner confirmed [phanmanhcuongdev/tree-cbir](https://github.com/phanmanhcuongdev/tree-cbir) as the public destination for the filtered source snapshot. The original repository history, datasets, research archives and restricted reference material are handled separately. Team handover remains pending until collaborators can restore the authorized artifacts.

## Preparation checkpoints

| Step | Result |
| --- | --- |
| 01/08 | Repository audit and local recovery checkpoints preserve the historical work. |
| 02/08 | Traceable requirements and all 38 feature definitions, with unresolved decisions registered. |
| 03/08 | Shared component interfaces, validity and version metadata, synthetic fixtures and 14 contract tests. |
| 04/08 | Three independent packages and M1–M4 ownership and integration sequencing. |
| 05/08 | Feature and phase acceptance criteria, evaluation controls and evidence requirements. |
| 06/08 | Agent entry points, progress records, checkpoint procedures and resume prompts. |
| 07/08 | Reviewed source snapshot and external artifacts. Local clean clone passed 55 dataset-independent tests and 58 after external restore, including pgvector. |
| 08/08 | Source gate, final onboarding and local smoke completed. The owner approved public release of the filtered snapshot. Team artifact delivery awaits owner action. |

## Source provenance and product status

The 07/08 input was the 172-file archive with SHA-256 `e9c69e2533c486d1cb9b1382cd20425bb149957b4feb5a8167615ff0bd70f25a`, scratch commit `2d800a0b7843a6253b0ae167e8289fbf19382a97`. All members were compared to that Git tree. This preparation adds this handoff document and updates README, team/branch instructions, task progress branch names and portable setup commands. Use [the 07/08 allowlist](publication_candidate_files.txt) plus `docs/team_preparation/final_handoff.md`. The 173-file source tree uses a fresh, isolated Git history. It retains the official dataset acquisition link and academic references by section. Direct links to restricted course material and local executable paths were omitted from the public snapshot. Original branches, datasets, experiments and checkpoints stay local.

P01/P02 are accepted. P03 remains partial, with the default hybrid trunk baseline. The V2 and supervised V3 assets are experimental. Shared P08 contracts and fixtures work, while the production extractor, remaining feature groups, persistence, retrieval, UI and full product evaluation are unfinished. See [status](../status.md), [readiness evidence](readiness_report.md) and [acceptance criteria](../acceptance_criteria.md).

The 08/08 filtered local workspace passed its RGB import/preprocessing smoke and 26 dataset-independent tests, including all 14 shared contract tests. The 07/08 full regression evidence still applies to the unchanged source. The updated documents pass the staged whitespace check. The initial staged diff flags inherited blank lines at the end of six V2 experiment files, which were preserved byte-for-byte. Use the published develop branch for clone verification.

## Packages and integration

| Package | Status | Scope | Intended member branch |
| --- | --- | --- | --- |
| [TASK-A](../tasks/TASK-A.md) | UNASSIGNED | P03 trunk, P08 extraction, integration | `feature/trunk` |
| [TASK-B](../tasks/TASK-B.md) | UNASSIGNED | P04 canopy, P05 branches, P09 persistence and normalization | `feature/canopy-branch` |
| [TASK-C](../tasks/TASK-C.md) | UNASSIGNED | P06 roots, P07 context, P10 retrieval, P11 interface | `feature/root-context` |

M1 supplies compatible component contracts and fixture evidence. At M2, A publishes the integrated extractor profile. At M3, B delivers the real gallery and matching normalization fit. At M4, C delivers exact eligible retrieval, UI traces and demo evidence. All packages supply P12 evidence. The [task index](../tasks/README.md) defines the gates and links each progress record.

## Private artifact delivery

The owner designated [500 Ảnh](https://drive.google.com/drive/folders/1GcqBCnZpZZ9-VF6Kf1MTsOCyAioII_4h?usp=drive_link) as the official image source. The folder listing shows 508 JPEG entries with 507 unique names and a duplicate `475.jpg`. Names and sizes match original inputs; the 37 transformed images differ in size from the standardized version. Team members should use their own authorized Drive account, verify source hashes, and follow the [download and preprocessing guide](../dataset_setup.md#obtain-the-authorized-files). The listing exposed only JPEGs. Deliver TASK-A research archives separately and keep the independent holdout under the custodian's access.

The files below are verified and staged in the owner's local 07/08 artifact directory outside the Git baseline. The owner still needs to invite three members, confirm which users can access the data and research bundles, and select a custodian for the separate holdout. Share privately through an authorized channel and verify recipient restoration. Keep the sealed split out of development and training distribution.

| Artifact | ZIP filename | SHA-256 |
| --- | --- | --- |
| DATA-STD | `data-std-507.zip` | `e1662da9ce7c8db25be5a957842793d42a760a9c1ee16b07d31350ee571524bd` |
| P03-DEV | `p03-development-evidence-r2.zip` | `e994c547516414b7128a2ac0ddf0734857225d32de801482844b6194cc4c2c6f` |
| P03-FEATURES | `p03-v3-train-val-features.zip` | `6d4ebaa0c7c8d2cdaaa89781ec99d030ae360d2cf0d3c54875a893c8b70bb735` |
| P03-SEALED | `p03-v3-frozen-split.zip` | `c44f1cb37db821ffcaa384a31b3cd8d8ef9241464bb629ba7abb7cd49de140ad` |

The [artifact manifest](artifact_manifest.csv) records all sizes, digests and member paths including optional originals and the Windows wheelhouse. Historical research and the independent holdout remain outside the source snapshot.

## Member onboarding after publication is verified

1. Clone the public repository and confirm the package claim with the owner. Configure GitHub authentication with your own credentials for contributions. Then run:

   ```powershell
   git clone https://github.com/phanmanhcuongdev/tree-cbir.git
   cd tree-cbir
   git switch develop
   # Run only the command for the confirmed package:
   git switch -c feature/trunk
   git switch -c feature/canopy-branch
   git switch -c feature/root-context
   ```

2. Follow the [Python 3.14.3 setup](../../GUIDE.md#python-environment). Start on fixtures with `./.venv/Scripts/python.exe -m pytest -v tests/unit/test_component_contracts.py`. Stage I does not need the images or PostgreSQL.
3. For images, follow the official Drive route above or restore the verified DATA-STD alternative. For authorized archives, place the ZIPs in a neighboring private `handoff-artifacts` folder. Run the commands appropriate to your permission and task:

   ```powershell
   ./.venv/Scripts/python.exe scripts/restore_handoff_artifact.py DATA-STD ../handoff-artifacts/data-std-507.zip
   ./.venv/Scripts/python.exe scripts/verify_dataset.py
   # TASK-A after approved research access:
   ./.venv/Scripts/python.exe scripts/restore_handoff_artifact.py P03-DEV ../handoff-artifacts/p03-development-evidence-r2.zip
   ./.venv/Scripts/python.exe scripts/restore_handoff_artifact.py P03-FEATURES ../handoff-artifacts/p03-v3-train-val-features.zip
   # Approved custodian or regression runner only:
   ./.venv/Scripts/python.exe scripts/restore_handoff_artifact.py P03-SEALED ../handoff-artifacts/p03-v3-frozen-split.zip
   ```

4. Give your coding agent the [quickstart prompt](../agent_quickstart.md) for the claimed package. Update its progress record after each checkpoint. Follow the [team workflow](../team_workflow.md) to stage only owned files. When authorized to publish your feature branch, run `git push -u origin HEAD`. In GitHub choose **New pull request**, base `develop`, compare your feature branch and request the affected reviewers.

## Pending owner decisions

- Grant contributor access as needed, confirm package claims later, and verify that each can open the official Drive folder. Authorize separate private artifact access for TASK-A and the holdout custodian as applicable. Verify recipient restoration. Full handover remains incomplete until these steps pass.
- Preserve the approvals in the [decision register](specification_decisions.md) for bark representation, expected trunk height, hue/branch thresholds, root exclusion, similarity weights/coverage, and any `LIMITED` acceptance.
