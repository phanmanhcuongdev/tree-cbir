"""Prepare P03-FINAL Prompt 1 dataset splits, SLIC/oracle experiments, and region features."""

from __future__ import annotations

import json
from dataclasses import asdict

from tree_cbir.config import PROJECT_ROOT
from tree_cbir.segmentation.region_features import FEATURE_DIMENSION, FEATURE_SPECS
from tree_cbir.segmentation.superpixel_labels import LabelPolicy
from tree_cbir.segmentation.superpixels import SlicConfig
from tree_cbir.services.trunk_dataset import (
    build_split_manifest,
    export_split_features,
    load_curated_annotations,
    run_slic_experiments,
    write_csv,
)


def main() -> None:
    root = PROJECT_ROOT
    data_dir = root / "data/standardized"
    out_dir = root / "outputs/trunk/p03_final/01_dataset_features"
    out_dir.mkdir(parents=True, exist_ok=True)

    active_annotations, inventory_rows, quality_rows = load_curated_annotations(root, out_dir)
    write_csv(out_dir / "annotation_inventory.csv", inventory_rows)
    write_csv(out_dir / "annotation_quality_review.csv", quality_rows)

    split_records = build_split_manifest(root, out_dir, active_annotations)
    manifest_rows = [
        {
            "filename": r.filename,
            "split": r.split,
            "source_group": r.source_group,
            "quality_status": r.quality_status,
            "sha256": r.sha256,
            "traits": ";".join(r.traits),
            "notes": r.notes,
        }
        for r in split_records
    ]
    write_csv(out_dir / "dataset_split_manifest.csv", manifest_rows)

    # Evaluate four candidate SLIC configurations across all 52 dev (train+val) images.
    slic_configs = [
        SlicConfig(name="slic_500_c15", n_segments=500, compactness=15.0, sigma=1.0),
        SlicConfig(name="slic_1000_c15", n_segments=1000, compactness=15.0, sigma=1.0),
        SlicConfig(name="slic_2000_c15", n_segments=2000, compactness=15.0, sigma=1.0),
        SlicConfig(name="slic_3000_c10", n_segments=3000, compactness=10.0, sigma=0.8),
    ]
    policy = LabelPolicy(positive_threshold=0.80, negative_threshold=0.20, oracle_threshold=0.50)
    agg_rows, oracle_rows, best_config = run_slic_experiments(
        split_records,
        active_annotations,
        slic_configs,
        data_dir,
        out_dir / "superpixel_contact_sheets",
        policy=policy,
    )
    write_csv(out_dir / "slic_experiment_results.csv", agg_rows)
    write_csv(out_dir / "superpixel_oracle_results.csv", oracle_rows)

    train_dist, train_summary = export_split_features(
        split_records,
        active_annotations,
        best_config,
        data_dir,
        out_dir / "train_features.npz",
        split_name="train",
        policy=policy,
    )
    val_dist, val_summary = export_split_features(
        split_records,
        active_annotations,
        best_config,
        data_dir,
        out_dir / "validation_features.npz",
        split_name="val",
        policy=policy,
    )
    write_csv(out_dir / "label_distribution.csv", train_dist + val_dist)

    schema_payload = {
        "feature_dimension": FEATURE_DIMENSION,
        "selected_slic_config": asdict(best_config),
        "label_policy": asdict(policy),
        "leakage_policy": (
            "Feature matrix X contains only handcrafted RGB/superpixel descriptors computed "
            "from unseen input images. Ground-truth overlap, image_id, split, and sample "
            "weights are stored in separate arrays as metadata only."
        ),
        "groups": {
            group: sum(1 for spec in FEATURE_SPECS if spec.group == group)
            for group in sorted({spec.group for spec in FEATURE_SPECS})
        },
        "features": [asdict(spec) for spec in FEATURE_SPECS],
    }
    (out_dir / "feature_schema.json").write_text(
        json.dumps(schema_payload, indent=2), encoding="utf-8"
    )

    split_counts = {}
    for rec in split_records:
        split_counts[rec.split] = split_counts.get(rec.split, 0) + 1
    trait_counts: dict[str, int] = {}
    for rec in split_records:
        if rec.split in ("train", "val"):
            for trait in rec.traits:
                trait_counts[trait] = trait_counts.get(trait, 0) + 1

    split_summary = {
        "total_standardized_images": len(split_records),
        "split_counts": split_counts,
        "selected_slic_config": asdict(best_config),
        "train_feature_summary": train_summary,
        "validation_feature_summary": val_summary,
        "new_annotation_trait_counts": trait_counts,
        "independent_test_status": "FROZEN_AND_EXCLUDED_NO_INFERENCE_RUN",
    }
    (out_dir / "dataset_split_summary.json").write_text(
        json.dumps(split_summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(split_summary, indent=2))


if __name__ == "__main__":
    main()
