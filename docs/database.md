# Proposed database design (P09)

PostgreSQL 17 with pgvector will store image metadata and local file references, raw/normalized 38-vectors, validity masks, five component vectors (9, 8, 3, 6, 12), and Min–Max parameter provenance. Retrieval will use exact nearest-neighbor ranking and weighted group distances. Production schema is deliberately deferred to P09; P01 only initializes the extension.

## Local isolated database

Run a local Docker Engine and Docker Compose plugin with Linux containers. Pull the digest pinned in `compose.yaml`. Verified versions are PostgreSQL **17.12** and pgvector **0.8.7**. This setup initializes the `vector` extension on a new project volume through `sql/01_init.sql`. It sets up the development service and P01 smoke schema, with production migrations still assigned to P09.

For a fresh checkout only, copy `.env.example` to `.env`. Set a unique local `POSTGRES_PASSWORD`; `POSTGRES_USER` and `POSTGRES_DB` select the local DB identity, while `POSTGRES_PORT` is the host port. Choose a free port and a distinct Compose project name for each checkout. Keep the bind on `127.0.0.1` as defined by Compose. Example with an unused project name `tree-cbir-dev`:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
# Edit the new local .env before continuing.
docker compose -p tree-cbir-dev config --quiet
docker compose -p tree-cbir-dev up -d --wait postgres
docker compose -p tree-cbir-dev ps postgres
```

Confirm `healthy` and the expected localhost port. Use the process-local `DATABASE_URL` wrapper documented under [PostgreSQL and full regression](testing.md#postgresql-and-full-regression) with `tests/integration/test_database.py` appended after `-v`. The check connects to your DB, creates a temporary vector table and tests exact operator behavior. A skipped DB test is a blocked integration check. Use `docker compose -p tree-cbir-dev stop postgres` to stop your service while retaining its volume. A reused volume does not run initialization SQL again automatically. Avoid pointing at the owner's database or reusing another checkout's project/port.
