"""Read-only deterministic audit of data/processed."""

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
OUT = ROOT / "outputs/preprocessing"
OUT.mkdir(parents=True, exist_ok=True)
rows = []
hashes = defaultdict(list)
for path in sorted(p for p in DATA.rglob("*") if p.is_file() and p.name != ".gitkeep"):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    row = {
        "relative_path": str(path.relative_to(DATA)),
        "filename": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": len(raw),
        "sha256": digest,
        "decoded_format": "",
        "original_dimensions": "",
        "exif_dimensions": "",
        "aspect_ratio": "",
        "color_mode": "",
        "decode_status": "FAIL",
        "resolution_compliant": False,
        "aspect_ratio_compliant": False,
        "duplicate_content": False,
        "warning": "",
    }
    try:
        with Image.open(path) as image:
            original = image.size
            adjusted = ImageOps.exif_transpose(image).size
            row.update(
                decoded_format=image.format or "",
                original_dimensions=f"{original[0]}x{original[1]}",
                exif_dimensions=f"{adjusted[0]}x{adjusted[1]}",
                aspect_ratio=adjusted[0] / adjusted[1],
                color_mode=image.mode,
                decode_status="PASS",
                resolution_compliant=adjusted == (768, 1024),
                aspect_ratio_compliant=abs(adjusted[0] / adjusted[1] - 0.75) < 1e-9,
            )
            if path.suffix.lower().lstrip(".") not in {"jpg", "jpeg", "png", "webp"}:
                row["warning"] = "unexpected extension"
            elif image.format and path.suffix.lower().lstrip(".") not in (
                {"jpg", "jpeg"} if image.format == "JPEG" else {image.format.lower()}
            ):
                row["warning"] = "extension/format mismatch"
        hashes[digest].append(row["relative_path"])
    except (UnidentifiedImageError, OSError) as error:
        row["warning"] = str(error)
    rows.append(row)
for group in hashes.values():
    if len(group) > 1:
        for row in rows:
            if row["relative_path"] in group:
                row["duplicate_content"] = True
fields = list(rows[0]) if rows else ["relative_path"]
with (OUT / "dataset_audit.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
decoded = [r for r in rows if r["decode_status"] == "PASS"]
summary = {
    "total_local_files": len(rows),
    "successfully_decoded_images": len(decoded),
    "failed_image_decodes": len(rows) - len(decoded),
    "non_image_files": sum(r["decode_status"] == "FAIL" for r in rows),
    "correct_resolution": sum(r["resolution_compliant"] for r in decoded),
    "correct_aspect_ratio": sum(r["aspect_ratio_compliant"] for r in decoded),
    "duplicate_content_groups": sum(len(v) > 1 for v in hashes.values()),
    "unique_compliant_images": sum(
        r["resolution_compliant"] and r["aspect_ratio_compliant"] and not r["duplicate_content"]
        for r in decoded
    ),
    "total_dataset_size_bytes": sum(r["size_bytes"] for r in rows),
    "format_distribution": dict(Counter(r["decoded_format"] for r in decoded)),
}
(OUT / "dataset_audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
(OUT / "dataset_audit_summary.md").write_text(
    "# Dataset audit\n\n" + "\n".join(f"- {k}: {v}" for k, v in summary.items()) + "\n",
    encoding="utf-8",
)
(OUT / "valid_candidates.txt").write_text(
    "\n".join(
        r["relative_path"]
        for r in rows
        if r["resolution_compliant"] and r["aspect_ratio_compliant"] and not r["duplicate_content"]
    )
    + "\n",
    encoding="utf-8",
)
print(json.dumps(summary, indent=2))
