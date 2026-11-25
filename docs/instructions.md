# Local workflow

Use `.\.venv\Scripts\python.exe` directly. Create `.env` from `.env.example` only if absent; start the database with `docker compose up -d`; then run pip check, Ruff and pytest. Use `DATABASE_URL` only for database integration tests. No cloud or CI/CD is configured.
