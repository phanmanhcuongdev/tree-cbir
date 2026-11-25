"""Reproducible P03.2 experiment runner. References are used only for evaluation."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np
from PIL import Image, ImageDraw

from tree_cbir.preprocessing import preprocess_image
from tree_cbir.segmentation.trunk import segment_trunk

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/standardized"
OUT = ROOT / "outputs/trunk/p03_2_auto"
REFERENCE = OUT / "references/annotations.json"


def reference_mask(rows, shape):
    height, width = shape
    polygon = [(left, y) for y, left, _ in rows]
    polygon.extend((right, y) for y, _, right in reversed(rows))
    points = np.rint(np.array(polygon) * [width / 384, height / 512]).astype(np.int32)
    return cv2.fillPoly(np.zeros(shape, np.uint8), [points], 1).astype(bool)


def metrics(mask, reference):
    if reference is None:
        return {}
    hit = int(np.count_nonzero(mask & reference))
    reference_area = int(reference.sum())
    area = int(mask.sum())
    return {
        "iou": hit / (area + reference_area - hit),
        "dice": 2 * hit / (area + reference_area),
        "precision": hit / max(1, area),
        "recall": hit / reference_area,
    }


def review(name, reference_rows, directory, method):
    rgb = preprocess_image(DATA / name).rgb
    started = perf_counter()
    result = segment_trunk(rgb, method=method)
    duration = perf_counter() - started
    mask, diag = result.mask, result.diagnostics
    reference = reference_mask(reference_rows, mask.shape) if reference_rows else None
    stats = metrics(mask, reference)
    yy, xx = np.where(mask)
    area = len(yy)
    overlay = rgb.copy()
    overlay[mask] = 0.55 * rgb[mask] + 0.45 * np.array([255, 64, 24])
    proposal = rgb.copy()
    x, y, w, h = diag.get("selected_roi") or (0, 0, 0, 0)
    if w:
        cv2.rectangle(proposal, (x, y), (x + w - 1, y + h - 1), (255, 210, 0), 2)
    for axis_y, left, right in diag.get("axis", ()):
        cv2.circle(proposal, ((left + right) // 2, axis_y), 2, (255, 80, 255), -1)
    for point, color in ((result.base, (255, 230, 0)), (result.upper, (0, 240, 255))):
        if point is not None:
            cv2.circle(overlay, point, 6, color, -1)
    seed = diag.get("seed")
    if seed:
        sy, sl, sr = seed
        cv2.line(proposal, (sl, sy), (sr, sy), (255, 0, 230), 4)
    diagnostics = {
        "filename": name,
        "seconds": round(duration, 4),
        "status": diag["status"],
        "confidence": result.confidence,
        "reason": diag.get("reason"),
        "area": area,
        "bbox": result.bbox,
        "base": result.base,
        "upper": result.upper,
        "vertical_extent": int(yy.max() - yy.min() + 1) if area else 0,
        "components": cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)[0] - 1,
        "rectangularity": area / (result.bbox[2] * result.bbox[3]) if result.bbox else 0,
        "structural_continuity": len(np.unique(yy)) / (yy.max() - yy.min() + 1) if area else 0,
        "outside_candidate_fraction": (
            1 - int(mask[y : y + h, x : x + w].sum()) / area if area and w else None
        ),
    }
    for field in (
        "candidate_score",
        "paired_boundary_support",
        "strong_green_fraction",
        "axis_agreement",
        "interior_color_rejection",
    ):
        diagnostics[field] = diag.get(field)
    if reference_rows:
        landmarks = reference_rows[1:-1]
        height, width = mask.shape
        points = [(round(a * height / 512), round((b + c) * width / 768)) for a, b, c in landmarks]
        radius = max(2, round(min(mask.shape) * 0.015))
        distances = [float(np.min(np.hypot(yy - py, xx - px))) for py, px in points] if area else []
        predicted_axis = diag.get("axis", ())
        diagnostics.update(
            stats,
            landmark_hit_rate=sum(d <= radius for d in distances) / len(points),
            axis_landmark_distance_px=float(
                np.mean(
                    [
                        min(
                            np.hypot(py - ay, px - (left + right) / 2)
                            for ay, left, right in predicted_axis
                        )
                        for py, px in points
                    ]
                )
            )
            if predicted_axis
            else None,
            seed_on_reference=bool(reference[seed[0], (seed[1] + seed[2]) // 2]) if seed else None,
            base_error_px=float(
                np.hypot(
                    result.base[0] - (reference_rows[-1][1] + reference_rows[-1][2]) * width / 768,
                    result.base[1] - reference_rows[-1][0] * height / 512,
                )
            )
            if result.base
            else None,
            usable=stats["iou"] >= 0.50 and stats["precision"] >= 0.70 and stats["recall"] >= 0.60,
        )
    panels = [rgb, proposal, mask.astype(np.uint8) * 255, overlay]
    if reference is not None:
        reference_path = OUT / "references" / f"{Path(name).stem}_reference.png"
        if not reference_path.exists():
            Image.fromarray(reference.astype(np.uint8) * 255).save(reference_path)
        panels.append(reference.astype(np.uint8) * 255)
    samples = directory / "samples"
    samples.mkdir(exist_ok=True)
    for label, panel in zip(("original", "candidate", "mask", "overlay"), panels, strict=False):
        ext = "png" if label == "mask" else "jpg"
        Image.fromarray(panel).save(samples / f"{Path(name).stem}_{label}.{ext}")
    return diagnostics, panels


def run(directory, names, references, independent, method):
    directory.mkdir(parents=True, exist_ok=True)
    records = []
    for first in range(0, len(names), 4 if independent else 6):
        group = names[first : first + (4 if independent else 6)]
        columns = 4 if independent else 5
        sheet = Image.new("RGB", (220 * columns, 30 + 304 * len(group)), "#f6f6f6")
        draw = ImageDraw.Draw(sheet)
        labels = ("Original", "Candidate / axis", "Mask", "Overlay", "Approx. reference")
        for index in range(columns):
            draw.text((index * 220 + 8, 6), labels[index], fill="black", font_size=15)
        for row_index, name in enumerate(group):
            record, panels = review(name, references.get(name), directory, method)
            records.append(record)
            y = 28 + 304 * row_index
            draw.text(
                (8, y),
                f"{name}  {record['status']}  {record['confidence']:.2f}",
                fill="black",
                font_size=15,
            )
            for column, panel in enumerate(panels):
                tile = Image.fromarray(panel)
                resample = Image.Resampling.NEAREST if panel.ndim == 2 else Image.Resampling.LANCZOS
                sheet.paste(tile.resize((207, 276), resample), (column * 220 + 6, y + 23))
        filename = f"contact_sheet_{first // 4 + 1}.jpg" if independent else "contact_sheet.jpg"
        sheet.save(directory / filename, quality=90)
        with Image.open(directory / filename) as check:
            check.load()
    with (directory / "results.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    summary = {
        "method": method,
        "images": list(names),
        "reference_sha256": hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
        "median_seconds": float(np.median([record["seconds"] for record in records])),
        "reliable": sum(record["status"] == "RELIABLE_DETECTION" for record in records),
    }
    if not independent:
        summary.update(
            usable=sum(record["usable"] for record in records),
            mean_iou=float(np.mean([record["iou"] for record in records])),
            unreliable_masks_marked_reliable=sum(
                not record["usable"] and record["status"] == "RELIABLE_DETECTION"
                for record in records
            ),
        )
    (directory / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("label")
    parser.add_argument("--independent", action="store_true")
    parser.add_argument("--method", default="baseline")
    args = parser.parse_args()
    refs = json.loads(REFERENCE.read_text(encoding="utf-8"))["rows"]
    names = list(refs)
    if args.independent:
        manifest = ROOT / "outputs/preprocessing/standardization/valid_candidates.txt"
        pool = sorted(set(manifest.read_text(encoding="utf-8").splitlines()) - set(names))
        names = [pool[(2 * i + 1) * len(pool) // 24] for i in range(12)]
        refs = {}
    run(OUT / args.label, names, refs, args.independent, args.method)
