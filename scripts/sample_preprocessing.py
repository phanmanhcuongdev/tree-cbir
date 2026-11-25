"""Create compact P02 evidence from deterministic real dataset samples."""

import json
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from tree_cbir.preprocessing import preprocess_image
from tree_cbir.utils.color import rgb_to_gray, rgb_to_hsv
from tree_cbir.utils.edges import canny
from tree_cbir.utils.morphology import closing, skeleton
from tree_cbir.utils.visualization import contour_overlay

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
OUT = ROOT / "outputs/preprocessing/samples"
OUT.mkdir(parents=True, exist_ok=True)
files = sorted(p for p in DATA.glob("*") if p.is_file() and p.name != ".gitkeep")[:12]
records = []
tiles = []
for path in files:
    start = time.perf_counter()
    original = Image.open(path)
    rgb = preprocess_image(path, path.name).rgb
    gray = rgb_to_gray(rgb)
    edges = canny(gray)
    demo = closing(gray > np.median(gray))
    contour = contour_overlay(rgb, demo)
    Image.fromarray(rgb).save(OUT / f"{path.stem}_rgb.jpg")
    Image.fromarray(gray).save(OUT / f"{path.stem}_gray.jpg")
    Image.fromarray(rgb_to_hsv(rgb)).save(OUT / f"{path.stem}_hsv.png")
    Image.fromarray(edges.astype(np.uint8) * 255).save(OUT / f"{path.stem}_edges.png")
    Image.fromarray(demo.astype(np.uint8) * 255).save(OUT / f"{path.stem}_generic_mask.png")
    Image.fromarray(contour).save(OUT / f"{path.stem}_contour.png")
    Image.fromarray(skeleton(demo).astype(np.uint8) * 255).save(OUT / f"{path.stem}_skeleton.png")
    tiles.append(cv2.resize(contour, (192, 256)))
    records.append(
        {
            "path": path.name,
            "format": original.format,
            "original_dimensions": original.size,
            "output_shape": list(rgb.shape),
            "dtype": str(rgb.dtype),
            "duration_seconds": round(time.perf_counter() - start, 4),
            "warning": "Generic threshold demonstration mask; not tree segmentation.",
        }
    )
sheet = np.vstack([np.hstack(tiles[i : i + 4]) for i in range(0, len(tiles), 4)])
Image.fromarray(sheet).save(OUT / "contact_sheet.jpg")
(OUT / "sample_results.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
print(json.dumps(records, indent=2))
