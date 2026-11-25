# Guide

Start with [AGENTS.md](AGENTS.md) and the [task index](docs/tasks/README.md). Get the reviewed source baseline and its Git SHA from the project owner. The [handoff checklist](docs/team_preparation/handoff_checklist.md) distinguishes publication, external artifacts and local-only files.

## Python environment

The verified configuration is **CPython 3.14.3, Windows x64**. Reuse a working compatible venv or create one in the new checkout. Use `py -3.14` if the Windows launcher lists that installation, or the `python` command that reports 3.14.3. On other hosts use the corresponding venv executable and validate wheel availability and test results there. The Windows constraint file is a verified reference for this environment, not a certification of other platforms.

```powershell
python --version
python -m venv .venv
./.venv/Scripts/python.exe -m pip install --only-binary=:all: -r requirements-dev.txt -c constraints-win-py314.txt "setuptools==84.2.1"
./.venv/Scripts/python.exe -m pip install --no-deps --no-build-isolation -e .
./.venv/Scripts/python.exe -m pip check
./.venv/Scripts/python.exe -m pytest -v tests/unit/test_component_contracts.py
```

`requirements.txt` contains runtime libraries for Pillow preprocessing, NumPy contracts, OpenCV/scikit-image trunk analysis, scikit-learn and pandas experimentation/smoke checks, psycopg/pgvector and Streamlit. `requirements-dev.txt` adds pytest and Ruff. The current V3 foundation uses installed numerical/image libraries and needs no separate model runtime or pretrained weights. Keep that supported set until a validated optional split is needed.

For offline Windows setup, obtain `WHEELS-WIN` from the approved internal store, restore it with the [artifact command](docs/dataset_setup.md#restoring-named-archives), and add `--no-index --find-links wheelhouse` to the first pip install above. Do not copy an existing venv from another machine.

Stage I fixture tests run without images or a database. For data-dependent work, follow the [dataset and artifact setup](docs/dataset_setup.md). For integration, use a [local isolated PostgreSQL database](docs/database.md#local-isolated-database), then the [test tiers](docs/testing.md#test-tiers-and-commands). The [quickstart](docs/agent_quickstart.md) has copy-ready agent prompts.
