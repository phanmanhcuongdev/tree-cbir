"""Run the existing mandatory DB test with project-local connection settings."""
import os
import sys
from pathlib import Path
from dotenv import dotenv_values
from psycopg.conninfo import make_conninfo
import pytest
cfg = dotenv_values(".env")
os.environ["DATABASE_URL"] = make_conninfo(host="127.0.0.1", port=cfg["POSTGRES_PORT"], dbname=cfg["POSTGRES_DB"], user=cfg["POSTGRES_USER"], password=cfg["POSTGRES_PASSWORD"], connect_timeout=5)
with (Path(__file__).parent/"final/pytest_results.txt").open("w",encoding="utf8") as stream:
    from contextlib import redirect_stdout, redirect_stderr
    with redirect_stdout(stream), redirect_stderr(stream):
        print("Command: .venv/Scripts/python.exe outputs/trunk/p03_2_v2/regression.py")
        code=pytest.main(["-v","--tb=no","--color=no"])
sys.exit(code)

