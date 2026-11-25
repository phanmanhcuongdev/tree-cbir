"""Practical tests for installed libraries; database/Streamlit are separately service-dependent."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

root = Path(__file__).resolve().parents[1]
results = {}


def run(name, operation):
    started = time.perf_counter()
    try:
        operation()
        results[name] = {
            "status": "PASS",
            "duration_seconds": round(time.perf_counter() - started, 4),
        }
    except Exception as error:
        results[name] = {"status": "FAIL", "error": repr(error)}


def numpy_test():
    import numpy as np

    assert np.linalg.norm(np.array([3, 4])) == 5


def pillow_test():
    from PIL import Image

    path = root / "outputs/environment/smoke.png"
    Image.new("RGB", (4, 4)).save(path)
    assert Image.open(path).convert("RGB").resize((2, 2)).size == (2, 2)
    path.unlink()


def cv_test():
    import cv2
    import numpy as np

    image = np.zeros((8, 8, 3), dtype=np.uint8)
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    mask = cv2.threshold(hsv[:, :, 0], 1, 255, cv2.THRESH_BINARY)[1]
    cv2.findContours(
        cv2.Canny(cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)), 1, 2),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )


def skimage_test():
    import numpy as np
    from skimage.morphology import skeletonize

    assert skeletonize(np.array([[1, 1, 1]], dtype=bool)).shape == (1, 3)


def sklearn_test():
    from sklearn.preprocessing import MinMaxScaler

    assert MinMaxScaler().fit_transform([[0, 1], [1, 2]]).shape == (2, 2)


def pandas_test():
    import pandas as pd

    path = root / "outputs/environment/smoke.csv"
    pd.DataFrame({"x": [1]}).to_csv(path, index=False)
    assert int(pd.read_csv(path).iloc[0, 0]) == 1
    path.unlink()


def dotenv_test():
    from dotenv import dotenv_values

    path = root / "outputs/environment/smoke.env"
    path.write_text("SMOKE_VALUE=ok\n", encoding="utf-8")
    assert dotenv_values(path)["SMOKE_VALUE"] == "ok"
    path.unlink()


def database_test():
    import psycopg
    from pgvector import Vector
    from pgvector.psycopg import register_vector

    with psycopg.connect(os.environ["DATABASE_URL"]) as connection:
        register_vector(connection)
        with connection.cursor() as cursor:
            cursor.execute("CREATE TEMP TABLE smoke_vectors (embedding vector(38))")
            cursor.execute("INSERT INTO smoke_vectors VALUES (%s)", (Vector([0.0] * 38),))
            cursor.execute("SELECT count(*) FROM smoke_vectors")
            assert cursor.fetchone()[0] == 1


def command_test(*args):
    subprocess.run([sys.executable, "-m", *args], check=True, cwd=root)


def streamlit_test():
    with urlopen(os.environ["STREAMLIT_HEALTH_URL"], timeout=10) as response:
        assert response.read().decode("utf-8").strip() == "ok"


for name, test in {
    "numpy": numpy_test,
    "Pillow": pillow_test,
    "OpenCV": cv_test,
    "scikit-image": skimage_test,
    "scikit-learn": sklearn_test,
    "pandas": pandas_test,
    "python-dotenv": dotenv_test,
    "psycopg/pgvector": database_test,
    "Streamlit": streamlit_test,
    "pytest": lambda: command_test("pytest", "-q"),
    "Ruff": lambda: command_test("ruff", "check", "."),
}.items():
    run(name, test)
(root / "outputs/environment/smoke_test_results.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
(root / "outputs/environment/smoke_test_results.md").write_text(
    "# Smoke tests\n\n"
    + "\n".join(f"- {key}: {value['status']}" for key, value in results.items())
    + "\n",
    encoding="utf-8",
)
print(json.dumps(results, indent=2))
