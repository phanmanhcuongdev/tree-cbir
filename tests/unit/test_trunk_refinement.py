import numpy as np

from tree_cbir.segmentation.trunk_candidates import Candidate
from tree_cbir.segmentation.trunk_refinement import refine_mask


def candidate(score=0.8):
    return Candidate(40, 40, 30, 120, 0.8, 0.5, 0.8, 0.8, 0.8, score)


def image():
    rgb = np.full((200, 120, 3), 120, np.uint8)
    rgb[40:160, 52:58] = (80, 60, 40)
    return rgb


def test_binary_shape_and_nonmutation():
    rgb = image()
    before = rgb.copy()
    mask, d = refine_mask(rgb, [candidate()])
    assert mask.shape == rgb.shape[:2] and mask.dtype == bool and np.array_equal(rgb, before)


def test_empty_and_weak_candidates_uncertain():
    mask, d = refine_mask(image(), [])
    assert not mask.any() and d["status"] == "UNCERTAIN_DETECTION"
    mask, d = refine_mask(image(), [candidate(0.1)])
    assert d["status"] in {"PARTIAL_DETECTION", "UNCERTAIN_DETECTION", "RELIABLE_DETECTION"}


def test_deterministic_and_noise_filtered():
    first, _ = refine_mask(image(), [candidate()])
    second, _ = refine_mask(image(), [candidate()])
    assert np.array_equal(first, second)
