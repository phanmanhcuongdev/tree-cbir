import numpy as np

from tree_cbir.segmentation.trunk_candidates import generate_candidates
from tree_cbir.segmentation.trunk_scoring import weighted_score


def test_multiscale_candidates_are_bounded_scored_and_deterministic():
    image = np.full((400, 300, 3), 120, np.uint8)
    image[:, 140:160] = (80, 60, 40)
    first, _ = generate_candidates(image)
    second, _ = generate_candidates(image)
    assert len({(item.width, item.height) for item in first}) > 1
    assert len({(item.x, item.y) for item in first}) > 1
    assert first == second
    for item in first:
        assert (
            0 <= item.x
            and item.x + item.width <= 300
            and 0 <= item.y
            and item.y + item.height <= 400
        )
        assert all(
            0 <= score <= 1
            for score in (
                item.color,
                item.edge,
                item.shape,
                item.position,
                item.continuity,
                item.score,
            )
        )


def test_weighted_score_and_invalid_input():
    assert weighted_score((1, 0, 0, 0, 0), (0.2, 0.2, 0.2, 0.2, 0.2)) == 0.2
    assert generate_candidates(np.zeros((3, 3), np.uint8))[0] == []
