import numpy as np
import pytest

from tree_cbir.config import BRANCH, CANOPY, CONTEXT, FEATURE_DIMENSION, ROOT, TRUNK
from tree_cbir.models import FeatureExtractionResult, SegmentationResult


def test_feature_groups_cover_exactly_38_dimensions() -> None:
    groups = (TRUNK, CANOPY, BRANCH, ROOT, CONTEXT)
    assert sum(group.stop - group.start for group in groups) == FEATURE_DIMENSION
    assert [item for group in groups for item in range(group.start, group.stop)] == list(range(38))


def test_invalid_zero_is_distinguishable_from_valid_zero() -> None:
    result = FeatureExtractionResult(np.zeros(38), np.array([False] + [True] * 37))
    assert result.values[0] == 0 and not result.valid[0]
    assert result.values[1] == 0 and result.valid[1]


def test_nonfinite_valid_feature_is_rejected() -> None:
    values = np.zeros(38)
    values[0] = np.nan
    with pytest.raises(ValueError, match="finite"):
        FeatureExtractionResult(values, np.ones(38, dtype=bool))


def test_binary_mask_convention_is_enforced() -> None:
    with pytest.raises(ValueError, match="bool"):
        SegmentationResult({"trunk": np.zeros((2, 2), dtype=np.uint8)})
