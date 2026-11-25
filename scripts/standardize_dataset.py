"""Derive a standardized P02 dataset without modifying source files."""

import csv
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image, ImageOps

from tree_cbir.preprocessing import preprocess_image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/processed"
TARGET = ROOT / "data/standardized"
OUT = ROOT / "outputs/preprocessing/standardization"
TARGET.mkdir(exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


before = {
    p.relative_to(SOURCE).as_posix(): digest(p)
    for p in SOURCE.rglob("*")
    if p.is_file() and p.name != ".gitkeep"
}
rows = []
for source in sorted(SOURCE.rglob("*")):
    if not source.is_file() or source.name == ".gitkeep":
        continue
    relative = source.relative_to(SOURCE)
    target = TARGET / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"naming collision: {target}")
    with Image.open(source) as image:
        adjusted = ImageOps.exif_transpose(image)
        original = image.size
        copy = (
            adjusted.size == (768, 1024)
            and image.mode == "RGB"
            and image.getexif().get(274, 1) == 1
        )
    if copy:
        shutil.copy2(source, target)
        transform = "copied"
    else:
        result = preprocess_image(source, relative.as_posix())
        Image.fromarray(result.rgb).save(target, format="JPEG", quality=95, subsampling=0)
        transform = "resized" if original[0] / original[1] == 0.75 else "center-cropped-and-resized"
    with Image.open(target) as output:
        valid = output.size == (768, 1024) and output.mode == "RGB"
        dimensions = f"{output.width}x{output.height}"
    rows.append(
        {
            "source_path": relative.as_posix(),
            "standardized_path": relative.as_posix(),
            "original_dimensions": f"{original[0]}x{original[1]}",
            "output_dimensions": dimensions,
            "applied_transformation": transform,
            "source_sha256": before[relative.as_posix()],
            "output_sha256": digest(target),
            "validation_status": "PASS" if valid else "FAIL",
        }
    )
after = {
    p.relative_to(SOURCE).as_posix(): digest(p)
    for p in SOURCE.rglob("*")
    if p.is_file() and p.name != ".gitkeep"
}
if before != after:
    raise RuntimeError("source integrity check failed")
with (OUT / "standardization_manifest.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
summary = {
    "standardized_images": len(rows),
    "copied": sum(r["applied_transformation"] == "copied" for r in rows),
    "resized": sum(r["applied_transformation"] == "resized" for r in rows),
    "cropped": sum(r["applied_transformation"] == "center-cropped-and-resized" for r in rows),
    "source_integrity": "PASS",
    "valid_outputs": sum(r["validation_status"] == "PASS" for r in rows),
    "duplicate_output_groups": len(rows) - len({r["output_sha256"] for r in rows}),
}
(OUT / "standardization_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
(OUT / "valid_candidates.txt").write_text(
    "\n".join(r["standardized_path"] for r in rows if r["validation_status"] == "PASS") + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2))
