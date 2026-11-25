import cv2
import numpy as np

from tree_cbir.segmentation.trunk import _grabcut_corridor, segment_trunk
from tree_cbir.segmentation.trunk_candidates import Candidate
from tree_cbir.segmentation.trunk_localization import (
    localize_trunk,
    select_seed,
    track_boundaries,
)


def scene():
    rgb = np.full((320, 220, 3), (163, 176, 188), dtype=np.uint8)
    rgb[263:, :] = (74, 143, 70)
    for y in range(65, 251):
        left = 74 + (y - 65) // 11
        rgb[y, left : left + 25] = (78, 65, 56)
    return rgb


def test_leafless_axis_and_base_above_ground_band():
    rgb = scene()
    result = segment_trunk(rgb)
    assert result.mask.dtype == bool and result.mask.shape == rgb.shape[:2]
    assert result.bbox is not None and result.base is not None
    assert abs(result.base[1] - 250) <= 6
    assert abs(result.diagnostics["probable_base"][1] - 250) <= 8
    assert not result.mask[263:].any()
    assert result.mask[91, 91] and result.mask[220, 101]


def test_supported_seed_expands_and_rejects_higher_ranked_background():
    lab = cv2.cvtColor(scene(), cv2.COLOR_RGB2LAB).astype(np.float32)
    location = localize_trunk(lab)
    assert location is not None
    distractor = Candidate(150, 210, 55, 100, 1, 1, 1, 1, 1, 1)
    seed_window = Candidate(60, 125, 70, 70, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
    selection = select_seed(lab, location, [distractor, seed_window])
    assert selection is not None
    candidate, seed, trace = selection
    assert candidate == seed_window
    assert track_boundaries(lab, seed) == trace
    assert trace[0][0] < seed_window.y - 25
    assert trace[-1][0] > seed_window.y + seed_window.height + 25
    assert trace[-1][1] > trace[0][1] + 8


def test_grass_only_with_horizontal_transition_is_uncertain():
    rgb = scene()
    rgb[:263] = (163, 176, 188)
    result = segment_trunk(rgb)
    assert result.diagnostics["status"] == "UNCERTAIN_DETECTION"
    assert result.base is None and not result.mask.any()


def test_trace_does_not_fill_large_unsupported_gap():
    rgb = scene()
    rgb[135:156] = (163, 176, 188)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    trace = track_boundaries(lab, (100, 77, 102))
    assert len(trace) > 50
    assert trace[-1][0] < 140


def test_base_priority_recovers_short_exposed_band():
    rgb = np.full((320, 220, 3), (170, 155, 125), np.uint8)
    rgb[224:250, 103:114] = (62, 49, 40)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    location = localize_trunk(lab, base_first=True)
    assert location is not None and abs(location.base[1] - 249) <= 7


def test_bands_reject_horizontal_ground_and_keep_trunk():
    rgb = scene()
    result = segment_trunk(rgb, method="bands")
    assert result.mask[150, 94] and not result.mask[280:].any()
    rgb[:263] = (163, 176, 188)
    assert not segment_trunk(rgb, method="bands").mask.any()


def test_grabcut_expands_into_observed_bark_and_leaves_unsupported_rows():
    rgb = np.full((90, 90, 3), (180, 195, 220), np.uint8)
    rgb[10:75, 33:57] = (85, 69, 48)
    rows = [y for y in range(10, 75) if not 35 <= y < 43]
    axis = tuple((y, 37, 53) for y in rows)
    observed = np.zeros(rgb.shape[:2], bool)
    observed[rows, 37:53] = True
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    mask = _grabcut_corridor(rgb, lab, axis, observed)
    assert mask[20, 34] and mask[20, 55]
    assert not mask[35:43].any()
    assert not mask[:, :33].any() and not mask[:, 57:].any()


def test_production_hybrid_matches_frozen_backend():
    rgb = scene()
    default = segment_trunk(rgb)
    frozen = segment_trunk(rgb, method="hybrid")
    assert default.mask.any() and np.array_equal(default.mask, frozen.mask)
