"""Frozen P03.2 calibration comparison against preserved baseline evidence."""

import csv
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from tree_cbir.preprocessing import preprocess_image
from tree_cbir.segmentation.trunk_candidates import generate_candidates
from tree_cbir.segmentation.trunk_refinement import refine_mask

root = Path(__file__).resolve().parents[1]
baseline = root / "outputs/trunk/p03_2"
out = root / "outputs/trunk/p03_2_quality_fix"
out.mkdir(parents=True, exist_ok=True)
names = ["1.jpg", "10.jpg", "100.jpg", "101.jpg", "102.jpg", "103.jpg"]
rows = []
panels = []
for name in names:
    rgb = preprocess_image(root / "data/standardized" / name, name).rgb
    candidates, _ = generate_candidates(rgb)
    mask, d = refine_mask(rgb, candidates)
    old = np.array(Image.open(baseline / f"{Path(name).stem}_mask.png").convert("L")) > 0
    old_overlay = np.array(Image.open(baseline / f"{Path(name).stem}_overlay.jpg").convert("RGB"))
    overlay = rgb.copy()
    pts = cv2.findNonZero(mask.astype(np.uint8))
    box = None
    if pts is not None:
        x, y, w, h = cv2.boundingRect(pts)
        box = (x, y, w, h)
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 0, 0), 3)
    c = candidates[0] if candidates else None
    rows.append(
        {
            "filename": name,
            "previous_mask_area": int(old.sum()),
            "updated_mask_area": int(mask.sum()),
            "updated_candidate_dimensions": None if c is None else f"{c.width}x{c.height}",
            "updated_bbox": box,
            "candidate_score": 0 if c is None else c.score,
            "segmentation_confidence": d.get("confidence", 0),
            "vertical_roi_coverage": d.get("coverage", 0),
            "status": d["status"],
        }
    )
    panels.append(
        [
            rgb,
            np.repeat(old[:, :, None] * 255, 3, 2),
            old_overlay,
            np.repeat(mask[:, :, None] * 255, 3, 2),
            overlay,
        ]
    )
for page in range(2):
    sheet = Image.new("RGB", (1500, 800), "white")
    for row, panel in enumerate(panels[page * 3 : page * 3 + 3]):
        for col, item in enumerate(panel):
            tile = cv2.resize(item.astype(np.uint8), (300, 250), interpolation=cv2.INTER_NEAREST)
            sheet.paste(Image.fromarray(tile), (col * 300, row * 250))
    sheet.save(out / f"comparison_{page + 1}.jpg")
with (out / "comparison_results.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=rows[0])
    w.writeheader()
    w.writerows(rows)
print(rows)
