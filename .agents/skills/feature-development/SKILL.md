---
name: feature-development
description: Implement owned component features and validate formulas separately from segmentation.
---
1. Read the feature spec for your slice, `docs/module_contract.md` and the corresponding `AC-X` rows. Keep segmentation, measurements and semantic labels separate. Preserve canonical masks, units, feature positions, explicit validity and profile versions.
2. Start from `tests/conftest.py` and independent expected values on synthetic masks. Test numeric values, true zero, missing metadata and supported fallback before measuring real mask quality. A useful fallback must preserve uncertainty and must not turn fixture output into production predictions.
3. Use `docs/team_preparation/evaluation_protocol.md` for approved image splits and real-quality evidence. Reuse existing algorithms and record each meaningful improvement round. Keep holdouts out of selection. Report pending academic decisions and route changes to shared data contracts through the accountable package.
