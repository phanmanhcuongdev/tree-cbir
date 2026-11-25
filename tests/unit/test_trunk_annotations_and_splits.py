"""Tests for annotation loading/rasterization, split disjointness, and leakage guards."""

from __future__ import annotations

import numpy as np
import pytest

from tree_cbir.config import IMAGE_HEIGHT, IMAGE_WIDTH, PROJECT_ROOT
from tree_cbir.segmentation.annotations import (
    TrunkAnnotation,
    load_legacy_strip_file,
    rasterize_annotation,
    rasterize_strips,
    validate_strips,
)
from tree_cbir.segmentation.region_features import FEATURE_SPECS
from tree_cbir.services.trunk_dataset import (
    DatasetSplitRecord,
    build_split_manifest,
    export_split_features,
    load_curated_annotations,
    validate_split_disjointness,
)


def test_annotation_rasterization_and_dimensions() -> None:
    mask = rasterize_strips(
        [[[10, 20, 40], [30, 20, 40]]],
        coord_width=192,
        coord_height=256,
        target_height=IMAGE_HEIGHT,
        target_width=IMAGE_WIDTH,
    )
    assert mask.shape == (IMAGE_HEIGHT, IMAGE_WIDTH)
    assert mask.dtype == np.bool_
    assert mask[40:121, 80:161].all()
    assert not mask[0, 0]

    # Legacy 384x512 annotation from P03.2-AUTO matches expected canonical dimensions.
    a_records = load_legacy_strip_file(
        PROJECT_ROOT / "outputs/trunk/p03_2_v2/references/A.json",
        source_group="A_auto",
        coord_width=384,
        coord_height=512,
        multi_strip=False,
    )
    mask_1 = rasterize_annotation(a_records["1.jpg"])
    assert mask_1.shape == (1024, 768)
    assert mask_1.dtype == np.bool_
    assert int(mask_1.sum()) == 2862


def test_malformed_strip_annotations_rejected() -> None:
    with pytest.raises(ValueError):
        validate_strips([], coord_width=192, coord_height=256)
    with pytest.raises(ValueError):
        validate_strips([[[10, 20, 30]]], coord_width=192, coord_height=256)
    with pytest.raises(ValueError):
        validate_strips([[[20, 10, 30], [10, 10, 30]]], coord_width=192, coord_height=256)
    with pytest.raises(ValueError):
        validate_strips([[[10, 40, 20], [30, 40, 20]]], coord_width=192, coord_height=256)
    with pytest.raises(ValueError):
        validate_strips([[[300, 10, 20], [310, 10, 20]]], coord_width=192, coord_height=256)


def test_split_disjointness_and_leakage_prevention(tmp_path) -> None:
    rec_a = DatasetSplitRecord("1.jpg", "train", "A", "ACCEPTED", "a")
    rec_b = DatasetSplitRecord("2.jpg", "val", "B", "ACCEPTED", "b")
    rec_c = DatasetSplitRecord("3.jpg", "test", "C", "SEALED", "c")
    buckets = validate_split_disjointness([rec_a, rec_b, rec_c])
    assert buckets["train"] == ["1.jpg"]
    assert buckets["val"] == ["2.jpg"]
    assert buckets["test"] == ["3.jpg"]

    with pytest.raises(ValueError, match="duplicate"):
        dup = DatasetSplitRecord("1.jpg", "val", "B", "ACCEPTED", "x")
        validate_split_disjointness([rec_a, dup])

    # Feature export strictly forbids generating training/val arrays for the test split.
    with pytest.raises(ValueError, match="forbidden split"):
        export_split_features(
            [rec_c],
            {},
            None,  # type: ignore[arg-type]
            tmp_path,
            tmp_path / "bad.npz",
            split_name="test",  # type: ignore[arg-type]
        )

    # Verify curated schema has zero ground-truth leakage column names.
    forbidden_tokens = ("ground_truth", "reference", "target_mask", "overlap", "trunk_base")
    for spec in FEATURE_SPECS:
        assert not any(tok in spec.name.lower() for tok in forbidden_tokens)


def test_curated_dataset_splits_disjoint_and_complete() -> None:
    evidence_dir = PROJECT_ROOT / "outputs/trunk/p03_final/01_dataset_features"
    active_annotations, _, _ = load_curated_annotations(PROJECT_ROOT, evidence_dir)
    records = build_split_manifest(PROJECT_ROOT, evidence_dir, active_annotations)
    assert len(records) == 507
    buckets = validate_split_disjointness(records)
    assert len(buckets["train"]) >= 30
    assert len(buckets["val"]) >= 12
    assert len(buckets["test"]) == 24
    assert set(buckets["excluded_unusable"]) == {"189.jpg", "339.jpg"}

    # Confirm annotation leakage into test split is explicitly caught if injected.
    leaked = dict(active_annotations)
    test_name = buckets["test"][0]
    leaked[test_name] = TrunkAnnotation(
        filename=test_name,
        source_group="leak",
        quality_status="ACCEPTED",
        coordinate_width=768,
        coordinate_height=1024,
        strips=(((100, 100, 120), (200, 100, 120)),),
    )
    with pytest.raises(ValueError, match="leakage"):
        build_split_manifest(PROJECT_ROOT, evidence_dir, leaked)
