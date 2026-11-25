"""Tests for deterministic SLIC superpixels, regional features, and overlap labeling."""

from __future__ import annotations

import numpy as np
import pytest

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
    SuperpixelMap,
    draw_superpixel_boundaries,
    generate_superpixels,
)


def _synthetic_tree_scene(height: int = 128, width: int = 96) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(7)
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    # Sky top, green grass bottom, vertical brown trunk in center
    rgb[:80] = np.array([135, 190, 235], dtype=np.uint8)
    rgb[80:] = np.array([65, 135, 55], dtype=np.uint8)
    noise = rng.integers(-6, 7, size=(height, width, 3))
    rgb = np.clip(rgb.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    truth = np.zeros((height, width), dtype=bool)
    truth[35:115, 42:54] = True
    bark_noise = rng.integers(-8, 9, size=(80, 12, 3))
    bark = np.clip(np.array([105, 72, 48], dtype=np.int16) + bark_noise, 0, 255).astype(np.uint8)
    rgb[35:115, 42:54] = bark
    return rgb, truth


def test_superpixels_deterministic_coverage_and_non_mutation() -> None:
    rgb, _ = _synthetic_tree_scene()
    snapshot = rgb.copy()
    cfg = SlicConfig(name="test_60", n_segments=60, compactness=12.0, sigma=0.8)

    sp1 = generate_superpixels(rgb, cfg)
    sp2 = generate_superpixels(rgb, cfg)
    overlay = draw_superpixel_boundaries(rgb, sp1.labels)

    assert np.array_equal(rgb, snapshot)
    assert overlay.shape == rgb.shape and overlay.dtype == np.uint8
    assert np.array_equal(sp1.labels, sp2.labels)
    assert np.array_equal(sp1.region_areas, sp2.region_areas)
    assert sp1.labels.shape == rgb.shape[:2]
    assert sp1.n_regions >= 1
    assert int(sp1.region_areas.sum()) == rgb.shape[0] * rgb.shape[1]


def test_region_features_dimensions_finite_and_non_mutation() -> None:
    rgb, _ = _synthetic_tree_scene()
    snapshot = rgb.copy()
    cfg = SlicConfig(name="test_60", n_segments=60, compactness=12.0, sigma=0.8)
    sp = generate_superpixels(rgb, cfg)

    f1 = extract_region_features(rgb, sp)
    f2 = extract_region_features(rgb, sp)

    assert np.array_equal(rgb, snapshot)
    assert f1.features.shape == (sp.n_regions, FEATURE_DIMENSION)
    assert len(FEATURE_SPECS) == FEATURE_DIMENSION
    assert f1.features.dtype == np.float64
    assert np.isfinite(f1.features).all()
    assert np.allclose(f1.features, f2.features)


def test_constant_color_and_tiny_regions_remain_finite() -> None:
    rgb = np.full((32, 32, 3), (120, 120, 120), dtype=np.uint8)
    labels = np.zeros((32, 32), dtype=np.int32)
    # Force a 1-pixel region (id=1), a 2-pixel region (id=2), and rest id=0.
    labels[0, 0] = 1
    labels[10, 10:12] = 2
    areas = np.bincount(labels.ravel(), minlength=3).astype(np.int64)
    sp = SuperpixelMap(
        labels=labels,
        n_regions=3,
        region_ids=np.arange(3, dtype=np.int32),
        region_areas=areas,
        duration_seconds=0.0,
        config=SlicConfig(name="manual", n_segments=3),
    )

    feats = extract_region_features(rgb, sp)
    assert feats.features.shape == (3, FEATURE_DIMENSION)
    assert np.isfinite(feats.features).all()

    # Single-region constant image also produces finite features (no neighbors edge case).
    one_label = np.zeros((16, 16), dtype=np.int32)
    sp_one = SuperpixelMap(
        labels=one_label,
        n_regions=1,
        region_ids=np.array([0], dtype=np.int32),
        region_areas=np.array([256], dtype=np.int64),
        duration_seconds=0.0,
        config=SlicConfig(name="single", n_segments=1),
    )
    feats_one = extract_region_features(rgb[:16, :16], sp_one)
    assert feats_one.features.shape == (1, FEATURE_DIMENSION)
    assert np.isfinite(feats_one.features).all()


def test_label_overlap_and_ambiguous_region_handling() -> None:
    labels = np.zeros((10, 10), dtype=np.int32)
    # Region 0: rows 0..4 (50 px) -> 0% trunk -> NON_TRUNK
    # Region 1: rows 5..7 (30 px) -> 90% trunk (27/30) -> TRUNK
    # Region 2: rows 8..9 (20 px) -> 50% trunk (10/20) -> AMBIGUOUS
    labels[5:8, :] = 1
    labels[8:10, :] = 2
    sp = SuperpixelMap(
        labels=labels,
        n_regions=3,
        region_ids=np.array([0, 1, 2], dtype=np.int32),
        region_areas=np.array([50, 30, 20], dtype=np.int64),
        duration_seconds=0.0,
        config=SlicConfig(name="synthetic", n_segments=3),
    )
    ref = np.zeros((10, 10), dtype=bool)
    ref[5:8, :9] = True  # 27/30 = 0.90
    ref[8:10, :5] = True  # 10/20 = 0.50

    out = label_superpixels(sp, ref, LabelPolicy(0.80, 0.20, 0.50))
    assert np.allclose(out.overlaps, [0.0, 0.90, 0.50])
    assert np.array_equal(out.labels, [LABEL_NON_TRUNK, LABEL_TRUNK, LABEL_AMBIGUOUS])
    assert out.n_positive == 1 and out.n_negative == 1 and out.n_ambiguous == 1

    # Ambiguous region gets weight 0.0; usable regions sum to 1.0.
    assert out.image_uniform_weights[2] == 0.0
    assert np.isclose(out.image_uniform_weights.sum(), 1.0)

    # Oracle includes region 2 (overlap 0.50 >= 0.50), strict excludes it.
    assert out.oracle_mask[8, 0] and not out.strict_positive_mask[8, 0]
    assert out.oracle_metrics.recall > out.strict_positive_metrics.recall


def test_invalid_inputs_raise() -> None:
    rgb_bad = np.zeros((32, 32, 3), dtype=np.float32)
    with pytest.raises(ValueError):
        generate_superpixels(rgb_bad, SlicConfig("x", 10))  # type: ignore[arg-type]

    rgb_ok = np.zeros((32, 32, 3), dtype=np.uint8)
    sp = generate_superpixels(rgb_ok, SlicConfig("x", 4))
    with pytest.raises(ValueError):
        label_superpixels(sp, np.zeros((16, 16), dtype=bool))
    with pytest.raises(ValueError):
        extract_region_features(rgb_ok[:16, :16], sp)
