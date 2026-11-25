"""Render the six P03.2 calibration cases using the production segmentation entry point."""

import csv
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
from PIL import Image, ImageDraw

from tree_cbir.preprocessing import preprocess_image
from tree_cbir.segmentation.trunk import segment_trunk

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("1.jpg", "10.jpg", "100.jpg", "101.jpg", "102.jpg", "103.jpg")


def main() -> None:
    output = ROOT / "outputs/trunk/p03_2_localization"
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for page in range(2):
        sheet = Image.new("RGB", (960, 1056), "#f5f5f5")
        draw = ImageDraw.Draw(sheet)
        for column, label in enumerate(
            ("Original", "Coarse axis region + seed", "Mask", "Overlay")
        ):
            draw.text((column * 240 + 8, 8), label, fill="black", font_size=16)
        for row, name in enumerate(NAMES[page * 3 : page * 3 + 3]):
            rgb = preprocess_image(ROOT / "data/standardized" / name).rgb
            started = perf_counter()
            result = segment_trunk(rgb)
            elapsed = perf_counter() - started
            diagnostic = result.diagnostics
            proposal = rgb.copy()
            overlay = rgb.copy()
            overlay[result.mask] = 0.55 * rgb[result.mask] + 0.45 * np.array([255, 70, 35])
            for key, color in (("coarse_region", (35, 190, 255)), ("selected_roi", (255, 180, 0))):
                if box := diagnostic.get(key):
                    x, y, w, h = box
                    cv2.rectangle(proposal, (x, y), (x + w - 1, y + h - 1), color, 3)
            if seed := diagnostic.get("seed"):
                y, left, right = seed
                cv2.line(proposal, (left, y), (right, y), (255, 50, 200), 5)
            if base := diagnostic.get("probable_base"):
                cv2.circle(proposal, base, 9, (35, 190, 255), -1)
            if result.base is not None:
                cv2.circle(overlay, result.base, 9, (255, 220, 0), -1)
            mask = Image.fromarray(result.mask.astype(np.uint8) * 255)
            mask.save(output / f"{Path(name).stem}_mask.png")
            Image.fromarray(overlay).save(output / f"{Path(name).stem}_overlay.jpg")
            top = 32 + row * 340
            draw.text((8, top), f"{name}   {diagnostic['status']}", fill="black", font_size=16)
            panels = [
                Image.fromarray(rgb),
                Image.fromarray(proposal),
                mask,
                Image.fromarray(overlay),
            ]
            for column, panel in enumerate(panels):
                method = Image.Resampling.NEAREST if column == 2 else Image.Resampling.LANCZOS
                sheet.paste(panel.resize((228, 304), method), (column * 240 + 6, top + 25))
            keys = (
                "status",
                "reason",
                "probable_base",
                "selected_roi",
                "candidate_score",
                "axis_agreement",
                "base_agreement",
                "paired_boundary_support",
                "interior_color_rejection",
                "strong_green_fraction",
                "pixels_outside_candidate",
            )
            records.append(
                {
                    "filename": name,
                    "mask_area": int(result.mask.sum()),
                    "bbox": result.bbox,
                    "tracked_base": result.base,
                    "confidence": round(result.confidence, 4),
                    "seconds": round(elapsed, 4),
                    **{key: diagnostic.get(key) for key in keys},
                }
            )
        sheet.save(output / f"contact_sheet_{page + 1}.jpg", quality=92)
    with (output / "localization_results.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


if __name__ == "__main__":
    main()
