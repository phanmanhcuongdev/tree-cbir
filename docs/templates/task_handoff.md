# Task handoff template

## Identification

- Assigned task and phase(s): `<TASK-A/B/C, Pxx>`
- Commit SHA, branch, base SHA and evidence run ID: `<filled>`
- Overall status: `<PASS | PARTIAL | FAIL | BLOCKED | LIMITED>`
- Milestone and receiving package: `<M1–M4, recipient and received/supplied artifact IDs>`
- Date/time, reviewer and release scope: `<filled>`

## Completed, failed and pending criteria

Use [acceptance criteria](../acceptance_criteria.md). List completed and unmet IDs separately. Separate mathematical correctness, real-image quality and integrated functionality even when rows use related inputs.

| Criterion ID and layer | Status | Expected gate and actual result | Evidence relative path or approved artifact reference | Owner/action and reason if unmet |
| --- | --- | --- | --- | --- |
| `<AC-Xnn / AC-Q-* / AC-Pnn / M1–M4>` | `<status>` | `<expected, observed and denominator>` | `<path or digest>` | `<next step or blocker>` |

## Files and test results

- Files changed and their purpose: `<repo-relative paths>`
- Preserved configurations/checkpoints and changed semantics: `<IDs and differences>`

| Tier and command | Prerequisites, data mode and versions | Exit code, pass/fail/skip counts and elapsed time | Log/evidence |
| --- | --- | --- | --- |
| `<paste exact command>` | `<versions, dataset or synthetic, DB and profile>` | `<actual result, duration and any blocked verification>` | `<path>` |

## Evidence and reproducibility

- Run directory or internal storage, access route and artifact SHA-256: `<filled>`
- Algorithm/config/model versions, commit and seed; dataset and annotation manifest/hash; fit, gallery and ranking profile IDs: `<filled, or state why inapplicable>`
- Per-feature validity and operands, segmentation overlay/reference, metric and timing files: `<paths>`
- Actual failures, limitations and leakage/exposure notes: `<filled>`
- Reproduction steps, verified demo paths and real/fixture labeling: `<filled>`

## Dependencies and owner decisions

| Dependency or decision | Compatibility/status | Impact and responsible task | Owner sign-off reference or action still needed |
| --- | --- | --- | --- |
| `<incoming/outgoing artifact, M-gate or A decision>` | `<present, version, approved/pending/blocked>` | `<scope and accountable task>` | `<link or next input>` |

- For `LIMITED`, include owner approval date and scope, underlying failed/blocked criteria, affected positions and the permitted prototype use. Pending approval leaves the gate failed or blocked as observed.
- Next action and newly known blockers: `<filled>`
