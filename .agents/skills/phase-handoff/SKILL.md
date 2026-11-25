---
name: phase-handoff
description: Record task progress, preserve a checkpoint and hand work to another agent or package.
---
1. After each meaningful subtask, update the task checklist and `docs/tasks/progress/TASK-*.md`. Put detailed tests, evidence and experiment history in the assigned `docs/logs/TASK-*.md`. Record the code commit or a scoped patch with separately saved untracked files, using `docs/team_workflow.md`.
2. On resume, reconcile the progress record with branch, checkpoint, working diff and artifact hashes. Start from the first actionable incomplete subtask. Preserve another person's edits and re-run checks only when the affected inputs changed or evidence is missing.
3. Use `docs/templates/task_handoff.md` for task handoff or phase close. Carry forward readiness, failed or blocked gates and pending owner decisions. Have the accountable package update status or release documents for verified changes. Share artifacts or submit a PR only through the authorized team workflow.
