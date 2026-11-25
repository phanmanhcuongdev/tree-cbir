# ADR-0003: PostgreSQL + pgvector

Status: Accepted. Context: vectors, metadata and relational integrity are required. Decision: PostgreSQL 17 plus pgvector via local Compose. Alternatives: SQLite or remote managed DB. Rationale: local exact-vector support. Consequence: Docker Engine is required for integration validation; P01 validated PostgreSQL 17.12, pgvector 0.8.7 and exact Top-5 operations locally.
