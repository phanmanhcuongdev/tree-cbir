"""Dataset preparation, leakage checks, SLIC/oracle evaluation, and NPZ export."""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import cv2
import numpy as np
from PIL import Image, ImageDraw

from tree_cbir.config import IMAGE_HEIGHT, IMAGE_WIDTH
from tree_cbir.preprocessing import preprocess_image
from tree_cbir.segmentation.annotations import (
    TrunkAnnotation,
    load_canonical_annotation_file,
    load_legacy_strip_file,
    rasterize_annotation,
)
from tree_cbir.segmentation.region_features import (
    FEATURE_DIMENSION,
    FEATURE_SPECS,
    extract_region_features,
)
from tree_cbir.segmentation.superpixel_labels import (
    LABEL_AMBIGUOUS,
    LABEL_NON_TRUNK,
    LABEL_TRUNK,
    LabelPolicy,
    label_superpixels,
)
from tree_cbir.segmentation.superpixels import (
    SlicConfig,
    draw_superpixel_boundaries,
    generate_superpixels,
)

SplitName = Literal["train", "val", "test", "excluded_unusable", "unused"]

UNUSABLE_IMAGES: dict[str, str] = {
    "189.jpg": (
        "Heavy foreground occlusion by frosted drooping twigs plus jagged two-strip "
        "staircase polygon; trunk boundary ambiguous."
    ),
    "339.jpg": (
        "Banyan with intertwined aerial prop roots; C.json draws three disjoint "
        "horizontal mid-stem cutoffs with background gaps."
    ),
}


@dataclass(frozen=True)
class DatasetSplitRecord:
    """Image-level split assignment with SHA-256 integrity checksum."""

    filename: str
    split: SplitName
    source_group: str
    quality_status: str
    sha256: str
    traits: tuple[str, ...] = ()
    notes: str = ""


def file_sha256(path: Path) -> str:
    """Compute SHA-256 hex digest for a file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_split_disjointness(records: list[DatasetSplitRecord]) -> dict[str, list[str]]:
    """Assert image-level disjointness across train, val, test, and excluded splits."""
    buckets: dict[str, list[str]] = {
        "train": [],
        "val": [],
        "test": [],
        "excluded_unusable": [],
        "unused": [],
    }
    seen: set[str] = set()
    for rec in records:
        if rec.filename in seen:
            raise ValueError(f"duplicate filename across split manifest: {rec.filename}")
        seen.add(rec.filename)
        buckets[rec.split].append(rec.filename)
    for left, right in (("train", "val"), ("train", "test"), ("val", "test")):
        overlap = set(buckets[left]) & set(buckets[right])
        if overlap:
            msg = f"split leakage detected between {left} and {right}: {sorted(overlap)}"
            raise ValueError(msg)
    return buckets


def load_curated_annotations(
    project_root: Path,
    evidence_dir: Path,
) -> tuple[dict[str, TrunkAnnotation], list[dict[str, Any]], list[dict[str, Any]]]:
    """Load legacy and curated annotations while keeping original files immutable."""
    a_path = project_root / "outputs/trunk/p03_2_v2/references/A.json"
    b_path = project_root / "outputs/trunk/p03_2_v2/references/B.json"
    c_path = project_root / "outputs/trunk/p03_2_v2/references/C.json"
    corr_path = evidence_dir / "corrected_annotations.json"
    new_path = evidence_dir / "new_dev_annotations.json"

    a_legacy = load_legacy_strip_file(
        a_path, source_group="A_auto", coord_width=384, coord_height=512, multi_strip=False
    )
    b_legacy = load_legacy_strip_file(
        b_path, source_group="B_v2", coord_width=192, coord_height=256, multi_strip=True
    )
    c_legacy = load_legacy_strip_file(
        c_path, source_group="C_v2", coord_width=192, coord_height=256, multi_strip=True
    )
    corrected = load_canonical_annotation_file(
        corr_path, source_group="curated_corrected", quality_status="CORRECTED"
    )
    new_dev = load_canonical_annotation_file(
        new_path, source_group="new_dev", quality_status="ACCEPTED"
    )

    inventory_rows: list[dict[str, Any]] = []
    quality_rows: list[dict[str, Any]] = []
    active_annotations: dict[str, TrunkAnnotation] = {}

    for group_name, legacy_map in (
        ("A_auto", a_legacy),
        ("B_v2", b_legacy),
        ("C_v2", c_legacy),
    ):
        for fname, ann in legacy_map.items():
            mask_orig = rasterize_annotation(ann)
            orig_area = int(mask_orig.sum())
            touches_bottom = any(
                row[0] >= ann.coordinate_height - 1 for strip in ann.strips for row in strip
            )
            inventory_rows.append(
                {
                    "filename": fname,
                    "source_group": group_name,
                    "source_file": ann.original_source,
                    "coord_space": f"{ann.coordinate_width}x{ann.coordinate_height}",
                    "n_strips": len(ann.strips),
                    "n_vertices": sum(len(s) for s in ann.strips),
                    "reconstructed_area_px": orig_area,
                    "area_fraction": round(orig_area / float(IMAGE_WIDTH * IMAGE_HEIGHT), 6),
                    "touches_coord_bottom": touches_bottom,
                    "valid_schema": True,
                }
            )
            if fname in UNUSABLE_IMAGES:
                quality_rows.append(
                    {
                        "filename": fname,
                        "source_group": group_name,
                        "review_status": "UNUSABLE",
                        "active_source": "EXCLUDED",
                        "final_area_px": 0,
                        "note": UNUSABLE_IMAGES[fname],
                    }
                )
            elif fname in corrected:
                corr_ann = corrected[fname]
                corr_mask = rasterize_annotation(corr_ann)
                active_annotations[fname] = corr_ann
                quality_rows.append(
                    {
                        "filename": fname,
                        "source_group": group_name,
                        "review_status": "REQUIRES_CORRECTION",
                        "active_source": str(corr_path.relative_to(project_root)),
                        "final_area_px": int(corr_mask.sum()),
                        "note": corr_ann.notes,
                    }
                )
            else:
                active_annotations[fname] = ann
                quality_rows.append(
                    {
                        "filename": fname,
                        "source_group": group_name,
                        "review_status": "ACCEPTED",
                        "active_source": ann.original_source,
                        "final_area_px": orig_area,
                        "note": "Visually verified clean alignment with visible main trunk.",
                    }
                )

    for fname, ann in new_dev.items():
        mask_new = rasterize_annotation(ann)
        active_annotations[fname] = ann
        area_new = int(mask_new.sum())
        inventory_rows.append(
            {
                "filename": fname,
                "source_group": "new_dev",
                "source_file": str(new_path.relative_to(project_root)),
                "coord_space": f"{ann.coordinate_width}x{ann.coordinate_height}",
                "n_strips": len(ann.strips),
                "n_vertices": sum(len(s) for s in ann.strips),
                "reconstructed_area_px": area_new,
                "area_fraction": round(area_new / float(IMAGE_WIDTH * IMAGE_HEIGHT), 6),
                "touches_coord_bottom": any(row[0] >= 1023 for s in ann.strips for row in s),
                "valid_schema": True,
            }
        )
        quality_rows.append(
            {
                "filename": fname,
                "source_group": "new_dev",
                "review_status": "ACCEPTED_NEW",
                "active_source": str(new_path.relative_to(project_root)),
                "final_area_px": area_new,
                "note": f"Newly annotated for diversity: {', '.join(ann.traits)}",
            }
        )

    return active_annotations, inventory_rows, quality_rows


def build_split_manifest(
    project_root: Path,
    evidence_dir: Path,
    active_annotations: dict[str, TrunkAnnotation],
) -> list[DatasetSplitRecord]:
    """Build and verify image-level disjoint split assignments across all 507 images."""
    candidates_file = project_root / "outputs/preprocessing/standardization/valid_candidates.txt"
    all_names = sorted(candidates_file.read_text(encoding="utf-8").splitlines())
    data_dir = project_root / "data/standardized"

    frozen_test_payload = json.loads(
        (evidence_dir / "frozen_independent_test_set.json").read_text(encoding="utf-8")
    )
    frozen_test = {item["filename"]: item["sha256"] for item in frozen_test_payload["images"]}
    if len(frozen_test) != 24:
        raise ValueError(f"expected 24 frozen test images, got {len(frozen_test)}")

    leak_test = set(active_annotations) & set(frozen_test)
    if leak_test:
        raise ValueError(f"annotation leakage into frozen test set: {sorted(leak_test)}")
    leak_unusable = set(active_annotations) & set(UNUSABLE_IMAGES)
    if leak_unusable:
        raise ValueError(f"unusable images present in active annotations: {sorted(leak_unusable)}")

    val_new = {"398.jpg", "418.jpg"}
    b_names = set(
        json.loads(
            (project_root / "outputs/trunk/p03_2_v2/references/B.json").read_text(encoding="utf-8")
        )["rows"]
    )
    val_set = b_names | val_new
    train_set = set(active_annotations) - val_set

    records: list[DatasetSplitRecord] = []
    for fname in all_names:
        digest = file_sha256(data_dir / fname)
        if fname in frozen_test:
            if digest != frozen_test[fname]:
                raise ValueError(f"SHA-256 mismatch on frozen independent test image {fname}")
            records.append(
                DatasetSplitRecord(
                    filename=fname,
                    split="test",
                    source_group="frozen_holdout_p03_final",
                    quality_status="SEALED_UNANNOTATED",
                    sha256=digest,
                    notes="Frozen independent test image; reserved for Prompt 3.",
                )
            )
        elif fname in UNUSABLE_IMAGES:
            records.append(
                DatasetSplitRecord(
                    filename=fname,
                    split="excluded_unusable",
                    source_group="C_v2",
                    quality_status="UNUSABLE",
                    sha256=digest,
                    notes=UNUSABLE_IMAGES[fname],
                )
            )
        elif fname in train_set:
            ann = active_annotations[fname]
            records.append(
                DatasetSplitRecord(
                    filename=fname,
                    split="train",
                    source_group=ann.source_group,
                    quality_status=ann.quality_status,
                    sha256=digest,
                    traits=ann.traits,
                    notes=ann.notes,
                )
            )
        elif fname in val_set:
            ann = active_annotations[fname]
            records.append(
                DatasetSplitRecord(
                    filename=fname,
                    split="val",
                    source_group=ann.source_group,
                    quality_status=ann.quality_status,
                    sha256=digest,
                    traits=ann.traits,
                    notes=ann.notes,
                )
            )
        else:
            records.append(
                DatasetSplitRecord(
                    filename=fname,
                    split="unused",
                    source_group="pool",
                    quality_status="UNANNOTATED",
                    sha256=digest,
                )
            )

    validate_split_disjointness(records)
    return records


def run_slic_experiments(
    split_records: list[DatasetSplitRecord],
    annotations: dict[str, TrunkAnnotation],
    configs: list[SlicConfig],
    data_dir: Path,
    sheets_dir: Path,
    *,
    policy: LabelPolicy = LabelPolicy(),
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], SlicConfig]:
    """Evaluate SLIC configurations and superpixel oracle bounds on train+val dev images."""
    dev_records = [r for r in split_records if r.split in ("train", "val")]
    sheets_dir.mkdir(parents=True, exist_ok=True)
    oracle_rows: list[dict[str, Any]] = []
    agg_rows: list[dict[str, Any]] = []

    best_config = configs[0]
    best_score = -1.0

    # Sample 6 visually diverse dev images for superpixel boundary & oracle contact sheets.
    sample_names = ["1.jpg", "100.jpg", "120.jpg", "160.jpg", "205.jpg", "333.jpg"]
    sample_names = [n for n in sample_names if n in annotations]

    for cfg in configs:
        cfg_rows: list[dict[str, Any]] = []
        sample_panels: list[tuple[str, np.ndarray, np.ndarray, np.ndarray, Any]] = []
        for rec in dev_records:
            rgb = preprocess_image(data_dir / rec.filename, rec.filename).rgb
            ref_mask = rasterize_annotation(annotations[rec.filename])
            sp = generate_superpixels(rgb, cfg)
            sp_lbl = label_superpixels(sp, ref_mask, policy)

            # Estimate median trunk width in pixels across non-empty reference rows
            ref_row_widths = ref_mask.sum(axis=1)
            nz_widths = ref_row_widths[ref_row_widths > 0]
            median_trunk_w = float(np.median(nz_widths)) if len(nz_widths) else 0.0
            trunk_size_bucket = (
                "thin" if median_trunk_w < 40.0 else "wide" if median_trunk_w >= 90.0 else "medium"
            )

            areas = sp.region_areas
            row = {
                "config_name": cfg.name,
                "n_segments_target": cfg.n_segments,
                "compactness": cfg.compactness,
                "sigma": cfg.sigma,
                "filename": rec.filename,
                "split": rec.split,
                "trunk_size_bucket": trunk_size_bucket,
                "median_trunk_width_px": round(median_trunk_w, 2),
                "ref_area_px": int(ref_mask.sum()),
                "actual_n_regions": sp.n_regions,
                "duration_seconds": round(sp.duration_seconds, 4),
                "area_min": int(areas.min()),
                "area_p10": float(np.percentile(areas, 10)),
                "area_median": float(np.median(areas)),
                "area_p90": float(np.percentile(areas, 90)),
                "area_max": int(areas.max()),
                "boundary_recall": round(sp_lbl.boundary_recall, 6),
                "undersegmentation_error": round(sp_lbl.undersegmentation_error, 6),
                "oracle_iou": round(sp_lbl.oracle_metrics.iou, 6),
                "oracle_dice": round(sp_lbl.oracle_metrics.dice, 6),
                "oracle_precision": round(sp_lbl.oracle_metrics.precision, 6),
                "oracle_recall": round(sp_lbl.oracle_metrics.recall, 6),
                "strict_pos_iou": round(sp_lbl.strict_positive_metrics.iou, 6),
                "strict_pos_precision": round(sp_lbl.strict_positive_metrics.precision, 6),
                "strict_pos_recall": round(sp_lbl.strict_positive_metrics.recall, 6),
                "n_positive": sp_lbl.n_positive,
                "n_negative": sp_lbl.n_negative,
                "n_ambiguous": sp_lbl.n_ambiguous,
            }
            cfg_rows.append(row)
            oracle_rows.append(row)
            if rec.filename in sample_names:
                sample_panels.append((rec.filename, rgb, ref_mask, sp.labels, sp_lbl))

        # Render visual contact sheet for this SLIC config
        sheet = Image.new("RGB", (1020, len(sample_panels) * 320), "white")
        draw = ImageDraw.Draw(sheet)
        for idx, (fname, rgb, ref_m, sp_labels, sp_lbl) in enumerate(sample_panels):
            bound_img = draw_superpixel_boundaries(rgb, sp_labels)
            oracle_ov = rgb.copy()
            oracle_ov[sp_lbl.oracle_mask] = (
                oracle_ov[sp_lbl.oracle_mask].astype(np.float32) * 0.50
                + np.array([0, 255, 100], np.float32) * 0.50
            ).astype(np.uint8)
            ct, _ = cv2.findContours(
                ref_m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            cv2.drawContours(oracle_ov, ct, -1, (255, 255, 0), 2)

            label_vis = rgb.copy()
            pos_m = (sp_lbl.labels == LABEL_TRUNK)[sp_labels]
            amb_m = (sp_lbl.labels == LABEL_AMBIGUOUS)[sp_labels]
            label_vis[pos_m] = (
                label_vis[pos_m].astype(np.float32) * 0.40
                + np.array([0, 230, 60], np.float32) * 0.60
            ).astype(np.uint8)
            label_vis[amb_m] = (
                label_vis[amb_m].astype(np.float32) * 0.35
                + np.array([255, 180, 0], np.float32) * 0.65
            ).astype(np.uint8)

            # Zoomed boundary/oracle comparison around trunk
            ys, xs = np.where(ref_m | sp_lbl.oracle_mask)
            y0 = max(0, int(ys.min()) - 60)
            y1 = min(IMAGE_HEIGHT, int(ys.max()) + 60)
            x0 = max(0, int(xs.min()) - 60)
            x1 = min(IMAGE_WIDTH, int(xs.max()) + 60)
            zoom_b = bound_img[y0:y1, x0:x1]
            ch, cw = zoom_b.shape[:2]
            sc = min(225 / cw, 280 / ch)
            zoom_pil = Image.fromarray(zoom_b).resize(
                (max(1, int(cw * sc)), max(1, int(ch * sc))), Image.Resampling.LANCZOS
            )

            y_off = idx * 320
            m_iou = sp_lbl.oracle_metrics.iou
            m_p = sp_lbl.oracle_metrics.precision
            m_r = sp_lbl.oracle_metrics.recall
            draw.text(
                (8, y_off + 4),
                f"{cfg.name} | {fname} | K={len(np.unique(sp_labels))} | "
                f"Oracle IoU={m_iou:.3f} (P={m_p:.3f}, R={m_r:.3f}) | "
                f"pos={sp_lbl.n_positive} amb={sp_lbl.n_ambiguous}",
                fill="black",
            )
            tiles = [
                Image.fromarray(bound_img).resize((216, 288), Image.Resampling.LANCZOS),
                Image.fromarray(oracle_ov).resize((216, 288), Image.Resampling.LANCZOS),
                Image.fromarray(label_vis).resize((216, 288), Image.Resampling.LANCZOS),
                zoom_pil,
            ]
            for c_idx, tile in enumerate(tiles):
                sheet.paste(tile, (c_idx * 250 + 8, y_off + 24))
        sheet.save(sheets_dir / f"{cfg.name}_contact_sheet.jpg", quality=92)

        thin_rows = [r for r in cfg_rows if r["trunk_size_bucket"] == "thin"]
        wide_rows = [r for r in cfg_rows if r["trunk_size_bucket"] == "wide"]
        mean_oracle_iou = float(np.mean([r["oracle_iou"] for r in cfg_rows]))
        mean_thin_iou = float(np.mean([r["oracle_iou"] for r in thin_rows])) if thin_rows else 0.0
        mean_wide_iou = float(np.mean([r["oracle_iou"] for r in wide_rows])) if wide_rows else 0.0
        agg = {
            "config_name": cfg.name,
            "n_segments_target": cfg.n_segments,
            "compactness": cfg.compactness,
            "sigma": cfg.sigma,
            "n_images": len(cfg_rows),
            "mean_actual_regions": round(
                float(np.mean([r["actual_n_regions"] for r in cfg_rows])), 2
            ),
            "mean_duration_seconds": round(
                float(np.mean([r["duration_seconds"] for r in cfg_rows])), 4
            ),
            "median_region_area_px": round(
                float(np.median([r["area_median"] for r in cfg_rows])), 2
            ),
            "mean_boundary_recall": round(
                float(np.mean([r["boundary_recall"] for r in cfg_rows])), 6
            ),
            "mean_undersegmentation_error": round(
                float(np.mean([r["undersegmentation_error"] for r in cfg_rows])), 6
            ),
            "mean_oracle_iou": round(mean_oracle_iou, 6),
            "median_oracle_iou": round(float(np.median([r["oracle_iou"] for r in cfg_rows])), 6),
            "mean_oracle_precision": round(
                float(np.mean([r["oracle_precision"] for r in cfg_rows])), 6
            ),
            "mean_oracle_recall": round(float(np.mean([r["oracle_recall"] for r in cfg_rows])), 6),
            "mean_strict_pos_iou": round(
                float(np.mean([r["strict_pos_iou"] for r in cfg_rows])), 6
            ),
            "thin_trunk_mean_oracle_iou": round(mean_thin_iou, 6),
            "wide_trunk_mean_oracle_iou": round(mean_wide_iou, 6),
            "total_positive_regions": sum(r["n_positive"] for r in cfg_rows),
            "total_negative_regions": sum(r["n_negative"] for r in cfg_rows),
            "total_ambiguous_regions": sum(r["n_ambiguous"] for r in cfg_rows),
        }
        agg_rows.append(agg)
        if mean_oracle_iou > best_score:
            best_score = mean_oracle_iou
            best_config = cfg

    return agg_rows, oracle_rows, best_config


def export_split_features(
    split_records: list[DatasetSplitRecord],
    annotations: dict[str, TrunkAnnotation],
    config: SlicConfig,
    data_dir: Path,
    output_path: Path,
    *,
    split_name: Literal["train", "val"],
    policy: LabelPolicy = LabelPolicy(),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build superpixel features and supervised labels for train or val split only."""
    if split_name not in ("train", "val"):
        raise ValueError(f"forbidden split for feature export: {split_name!r}")

    targets = [r for r in split_records if r.split == split_name]
    x_chunks: list[np.ndarray] = []
    y_chunks: list[np.ndarray] = []
    overlap_chunks: list[np.ndarray] = []
    image_id_chunks: list[np.ndarray] = []
    sp_id_chunks: list[np.ndarray] = []
    area_chunks: list[np.ndarray] = []
    split_chunks: list[np.ndarray] = []
    w_img_chunks: list[np.ndarray] = []
    dist_rows: list[dict[str, Any]] = []

    for rec in targets:
        rgb = preprocess_image(data_dir / rec.filename, rec.filename).rgb
        ref_mask = rasterize_annotation(annotations[rec.filename])
        sp = generate_superpixels(rgb, config)
        feat_mat = extract_region_features(rgb, sp)
        sp_lbl = label_superpixels(sp, ref_mask, policy)

        if not np.array_equal(feat_mat.region_ids, sp_lbl.region_ids):
            raise RuntimeError("region_ids mismatch between features and labels")
        if feat_mat.features.shape[1] != FEATURE_DIMENSION:
            raise RuntimeError("unexpected feature dimension")

        n = sp.n_regions
        x_chunks.append(feat_mat.features)
        y_chunks.append(sp_lbl.labels)
        overlap_chunks.append(sp_lbl.overlaps)
        image_id_chunks.append(np.full(n, rec.filename, dtype="<U32"))
        sp_id_chunks.append(sp.region_ids)
        area_chunks.append(sp.region_areas)
        split_chunks.append(np.full(n, split_name, dtype="<U16"))
        w_img_chunks.append(sp_lbl.image_uniform_weights)

        dist_rows.append(
            {
                "filename": rec.filename,
                "split": split_name,
                "n_regions": n,
                "n_positive": sp_lbl.n_positive,
                "n_negative": sp_lbl.n_negative,
                "n_ambiguous": sp_lbl.n_ambiguous,
                "positive_fraction_usable": round(
                    sp_lbl.n_positive / max(1, sp_lbl.n_positive + sp_lbl.n_negative), 6
                ),
                "oracle_iou": round(sp_lbl.oracle_metrics.iou, 6),
                "feature_duration_s": round(feat_mat.duration_seconds, 4),
            }
        )

    X = np.vstack(x_chunks)
    y = np.concatenate(y_chunks)
    overlaps = np.concatenate(overlap_chunks)
    image_ids = np.concatenate(image_id_chunks)
    sp_ids = np.concatenate(sp_id_chunks)
    areas = np.concatenate(area_chunks)
    splits = np.concatenate(split_chunks)
    w_img = np.concatenate(w_img_chunks)

    # Compute image-uniform + class-balanced sample weights on usable (non-ambiguous) regions.
    usable = y != LABEL_AMBIGUOUS
    w_bal = np.zeros_like(w_img)
    pos_mask = y == LABEL_TRUNK
    neg_mask = y == LABEL_NON_TRUNK
    sum_pos = float(w_img[pos_mask].sum())
    sum_neg = float(w_img[neg_mask].sum())
    if sum_pos > 0.0 and sum_neg > 0.0:
        w_bal[pos_mask] = w_img[pos_mask] * (0.5 / sum_pos) * float(np.count_nonzero(usable))
        w_bal[neg_mask] = w_img[neg_mask] * (0.5 / sum_neg) * float(np.count_nonzero(usable))

    feature_names = np.array([spec.name for spec in FEATURE_SPECS], dtype="<U64")
    np.savez_compressed(
        output_path,
        X=X,
        y=y,
        overlap=overlaps,
        image_id=image_ids,
        superpixel_id=sp_ids,
        split=splits,
        region_area=areas,
        sample_weight_image_uniform=w_img,
        sample_weight_image_class_balanced=w_bal,
        feature_names=feature_names,
    )

    summary = {
        "split": split_name,
        "n_images": len(targets),
        "n_regions_total": int(len(y)),
        "n_positive": int(np.count_nonzero(pos_mask)),
        "n_negative": int(np.count_nonzero(neg_mask)),
        "n_ambiguous": int(np.count_nonzero(y == LABEL_AMBIGUOUS)),
        "feature_dimension": int(X.shape[1]),
        "neg_to_pos_ratio": round(
            float(np.count_nonzero(neg_mask)) / max(1, int(np.count_nonzero(pos_mask))), 2
        ),
    }
    return dist_rows, summary


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write non-empty dictionary rows to UTF-8 CSV."""
    if not rows:
        raise ValueError(f"cannot write empty CSV to {path}")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
