# Publication and handoff checklist — 07/08

Use the [readiness report](readiness_report.md) and its exact candidate list. Any sharing or repository publication is a separate authorized action.

- [ ] Owner chooses repository visibility and approved history route. Use the screened source snapshot if the historical image contact sheets have not been cleared for distribution. Preserve the original repository and checkpoints locally.
- [ ] Confirm selected sources, contracts, synthetic tests, skills, setup and publication instructions match the reviewed candidate inventory. Review staged paths against the allowlist. Omit owner `.env`, venv, protected course documents, caches, snapshots, images, dumps and generated outputs.
- [ ] Approve image use and internal recipients. Transfer `DATA-STD`, task-A `P03-DEV`/`P03-FEATURES`, and only optional archives the recipients need. Verify archive digests and restored dataset hashes using the [artifact guide](../dataset_setup.md).
- [ ] Designate a V3 holdout custodian before distributing split metadata. Keep `P03-SEALED` separate, with access only for approved independent evaluation or regression. Keep original research checkpoints and unpublished material local unless separately reviewed.
- [ ] Publish the approved baseline SHA and task workflow after authorization. All task claims remain UNASSIGNED. Independent work can use synthetic tests after obtaining the baseline. Real component and DB gates retain their own prerequisites.
- [ ] Retain recorded clean-workspace validation and the release evidence checksums. If contents or environment change before publication, rerun the affected checks.
