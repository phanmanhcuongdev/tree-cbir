"""Create human-review contact sheets for P02 CROP_RESIZE pairs."""

import csv
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed"
STANDARDIZED = ROOT / "data/standardized"
OUTPUT = ROOT / "outputs/preprocessing/standardization/visual_review"
MANIFEST = ROOT / "outputs/preprocessing/standardization/standardization_manifest.csv"
OUTPUT.mkdir(parents=True, exist_ok=True)
font = ImageFont.load_default()
with MANIFEST.open(encoding="utf-8") as file:
    rows = [
        row
        for row in csv.DictReader(file)
        if row["applied_transformation"] == "center-cropped-and-resized"
    ]
for number, start in enumerate(range(0, len(rows), 6), start=1):
    pairs = rows[start : start + 6]
    sheet = Image.new("RGB", (1200, 900 * len(pairs)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(pairs):
        y = index * 900
        original = Image.open(SOURCE / row["source_path"]).convert("RGB")
        output = Image.open(STANDARDIZED / row["standardized_path"]).convert("RGB")
        original.thumbnail((560, 780))
        output.thumbnail((560, 780))
        sheet.paste(original, ((580 - original.width) // 2, y + 55))
        sheet.paste(output, (620 + (560 - output.width) // 2, y + 55))
        label = " | ".join(
            [
                row["source_path"],
                f"ORIGINAL {row['original_dimensions']}",
                f"STANDARDIZED {row['output_dimensions']}",
            ]
        )
        draw.text(
            (10, y + 10),
            label,
            fill="black",
            font=font,
        )
        draw.text((10, y + 35), "Original", fill="black", font=font)
        draw.text((620, y + 35), "Center-crop + resize", fill="black", font=font)
    sheet.save(OUTPUT / f"crop_resize_review_{number:02d}.jpg", quality=90)
