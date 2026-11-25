"""P03.2 six-image refinement evidence."""

import csv
import json
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from tree_cbir.preprocessing import preprocess_image
from tree_cbir.segmentation.trunk_candidates import generate_candidates
from tree_cbir.segmentation.trunk_refinement import refine_mask

root = Path(__file__).resolve().parents[1]
out = root / "outputs/trunk/p03_2"
out.mkdir(parents=True, exist_ok=True)
rows = []
panels = []
for path in sorted((root / "data/standardized").glob("*.jpg"))[:6]:
    start = time.perf_counter()
    rgb = preprocess_image(path, path.name).rgb
    candidates, _ = generate_candidates(rgb)
    mask, d = refine_mask(rgb, candidates)
    overlay = rgb.copy()
    selected = rgb.copy()
    if candidates:
        c = candidates[0]
        cv2.rectangle(selected, (c.x, c.y), (c.x + c.width, c.y + c.height), (255, 0, 0), 3)
        score = c.score
    else:
        score = 0.0
    points = cv2.findNonZero(mask.astype(np.uint8))
    bbox = None
    if points is not None:
        x, y, w, h = cv2.boundingRect(points)
        bbox = (x, y, w, h)
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (255, 0, 0), 3)
        cv2.circle(overlay, (x + w // 2, y + h - 1), 5, (0, 255, 0), -1)
    Image.fromarray(rgb).save(out / f"{path.stem}_original.jpg")
    Image.fromarray(selected).save(out / f"{path.stem}_candidate.jpg")
    Image.fromarray(mask.astype(np.uint8) * 255).save(out / f"{path.stem}_mask.png")
    Image.fromarray(overlay).save(out / f"{path.stem}_overlay.jpg")
    rows.append(
        {
            "filename": path.name,
            "selected_candidate_score": score,
            "mask_area": int(mask.sum()),
            "component_count": d["components"],
            "segmentation_confidence": d.get("confidence", 0),
            "segmentation_status": d["status"],
            "expected_height": 614.4,
            "expected_height_confidence": "low",
            "duration_seconds": round(time.perf_counter() - start, 4),
            "uncertainty_reason": d.get("reason"),
            "bbox": bbox,
        }
    )
    mask_vis = mask.astype(np.uint8) * 255
    panels.append([rgb, selected, cv2.cvtColor(mask_vis, cv2.COLOR_GRAY2RGB), overlay])
for page in range(2):
    subset = panels[page * 3 : page * 3 + 3]
    sheet = Image.new("RGB", (1200, 600 * len(subset)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, panel in enumerate(subset):
        for j, image in enumerate(panel):
            resized = cv2.resize(image, (300, 400), interpolation=cv2.INTER_NEAREST)
            sheet.paste(Image.fromarray(resized), (j * 300, i * 600 + 30))
        draw.text(
            (5, i * 600 + 5),
            rows[page * 3 + i]["filename"] + " | " + rows[page * 3 + i]["segmentation_status"],
            fill="black",
            font=ImageFont.load_default(),
        )
    sheet.save(out / f"contact_sheet_{page + 1}.jpg")
with (out / "refinement_results.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0])
    writer.writeheader()
    writer.writerows(rows)
summary = {
    "images": 6,
    "statuses": {
        s: sum(r["segmentation_status"] == s for r in rows)
        for s in {r["segmentation_status"] for r in rows}
    },
    "expected_height_note": (
        "0.6 image height is a low-confidence provisional fallback, not actual trunk height."
    ),
}
(out / "refinement_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
