"""Requires Docker PostgreSQL; skips only if DATABASE_URL is not configured."""

import os

import pytest


@pytest.mark.integration
def test_pgvector_round_trip() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not configured; run after compose service is healthy")
    import psycopg
    from pgvector import Vector
    from pgvector.psycopg import register_vector

    with psycopg.connect(database_url) as connection:
        register_vector(connection)
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cursor.execute("CREATE TEMP TABLE p01_vectors (id int, embedding vector(38))")
            for value in range(6):
                cursor.execute(
                    "INSERT INTO p01_vectors VALUES (%s, %s)",
                    (value, Vector([float(value)] * 38)),
                )
            cursor.execute(
                "SELECT id FROM p01_vectors ORDER BY embedding <-> %s LIMIT 5",
                (Vector([0.0] * 38),),
            )
            rows = cursor.fetchall()
            assert [row[0] for row in rows] == [0, 1, 2, 3, 4]

            first_axis = Vector([1.0] + [0.0] * 37)
            second_axis = Vector([0.0, 1.0] + [0.0] * 36)
            cursor.execute(
                "SELECT %s::vector <-> %s::vector, %s::vector <+> %s::vector, "
                "%s::vector <=> %s::vector, %s::vector <#> %s::vector",
                (
                    first_axis,
                    second_axis,
                    first_axis,
                    second_axis,
                    first_axis,
                    second_axis,
                    first_axis,
                    second_axis,
                ),
            )
            l2, l1, cosine, inner_product = cursor.fetchone()
            assert l2 == pytest.approx(2**0.5)
            assert l1 == pytest.approx(2.0)
            assert cosine == pytest.approx(1.0)
            assert inner_product == pytest.approx(0.0)
