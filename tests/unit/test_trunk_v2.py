import cv2
import numpy as np
import pytest

from tree_cbir.features.trunk import extract_trunk_features
from tree_cbir.segmentation.trunk import TrunkSegmentation, segment_trunk
from tree_cbir.segmentation.trunk_measurements import measurements


@pytest.mark.parametrize(
    "shape", ["narrow", "wide", "short", "inclined", "curved", "fork", "occluded"]
)
def test_visible_bole_and_measurement_provenance(shape):
    rgb = np.full((320, 240, 3), (175, 191, 205), np.uint8)
    truth = np.zeros(rgb.shape[:2], bool)
    for y in range(229 if shape == "short" else 95, 286):
        x = 119 + (
            int(8 * np.sin(y / 50))
            if shape == "curved"
            else (y - 200) // 8
            if shape == "inclined"
            else 0
        )
        radius = 23 if shape == "wide" else 5 if shape == "narrow" else 10
        truth[y, x - radius : x + radius] = True
        if shape == "fork" and y < 180:
            truth[y, x + 12 : x + 20] = True
    if shape == "occluded":
        truth[160:175] = False
    rgb[truth] = (69, 56, 51)
    original = rgb.copy()
    segmented = segment_trunk(rgb, method="v2")
    assert np.array_equal(rgb, original)
    assert segmented.mask.dtype == bool and segmented.mask.shape == truth.shape
    assert (segmented.mask & truth).sum() > 0.20 * truth.sum()
    assert (segmented.mask & ~truth).sum() < 0.2 * truth.sum()
    info = measurements(segmented)
    assert info.median_width and info.centerline
    assert segmented.expected_height == 0.6 * rgb.shape[0]
    values, valid, _ = extract_trunk_features(rgb, segmented.mask, segmented.expected_height)
    assert values.shape == valid.shape == (9,)
    if segmented.diagnostics["status"] == "UNCERTAIN_DETECTION":
        assert info.quality["base"] == info.quality["upper"] == "unreliable"


def test_evidence_free_foliage_determinism_and_invalid_input():
    rgb = np.full((192, 144, 3), (58, 146, 63), np.uint8)
    first = segment_trunk(rgb, method="v2")
    second = segment_trunk(rgb, method="v2")
    assert first.diagnostics["status"] == "UNCERTAIN_DETECTION"
    assert np.array_equal(first.mask, second.mask) and not first.mask.any()
    assert measurements(first).quality["width"] == "unavailable"
    with pytest.raises(ValueError):
        segment_trunk(rgb.astype(float), method="v2")


def test_separate_stems_and_clipped_base_are_explicit():
    mask = np.zeros((70, 50), np.uint8)
    cv2.rectangle(mask, (14, 20), (19, 69), 1, -1)
    cv2.rectangle(mask, (29, 15), (34, 69), 1, -1)
    result = TrunkSegmentation(
        mask.astype(bool),
        (14, 15, 21, 55),
        (19, 69),
        (34, 15),
        42,
        0.9,
        {"status": "RELIABLE_DETECTION"},
    )
    info = measurements(result)
    assert info.multiple_stem_evidence and info.quality["multiple_stem_evidence"] == "unreliable"
    assert info.quality["base"] == "unreliable"
