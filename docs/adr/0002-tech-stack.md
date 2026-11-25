# ADR-0002: Python 3.14.3 local stack

Status: Accepted. Context: host provides Python 3.14.3. Decision: use venv and specified Python packages locally. Alternatives: older Python or global packages. Rationale: project constraint. Consequence: CPython 3.14 wheels, functional smoke tests, editable package installation and local PostgreSQL integration succeeded on 2026-11-25; future upgrades still require revalidation.
