from io import BytesIO

import numpy as np
import pytest
from PIL import Image

from tree_cbir.preprocessing import PreprocessingError, preprocess_image
from tree_cbir.utils.color import hsv_mask, rgb_to_hsv
from tree_cbir.utils.geometry import bounding_box, horizontal_runs
from tree_cbir.utils.masks import area, area_ratio, components, intersection, union
from tree_cbir.utils.morphology import skeleton
from tree_cbir.utils.visualization import overlay


def encoded(mode, size, color):
    result = BytesIO()
    Image.new(mode, size, color).save(result, format="PNG")
    return result.getvalue()


@pytest.mark.parametrize(
    "mode,size",
    [
        ("RGB", (768, 1024)),
        ("RGB", (1200, 600)),
        ("RGB", (700, 700)),
        ("L", (20, 40)),
        ("RGBA", (20, 40)),
    ],
)
def test_preprocess_contract(mode, size):
    result = preprocess_image(encoded(mode, size, 0))
    assert result.rgb.shape == (1024, 768, 3) and result.rgb.dtype == np.uint8


def test_bytes_channel_order_and_invalid():
    assert preprocess_image(encoded("RGB", (3, 4), (255, 0, 0))).rgb[0, 0].tolist() == [255, 0, 0]
    with pytest.raises(PreprocessingError):
        preprocess_image(b"")


def test_masks_geometry_and_overlay():
    a = np.zeros((5, 5), bool)
    a[1:3, 1:3] = 1
    b = np.zeros((5, 5), bool)
    b[2:4, 2:4] = 1
    assert (
        area(a) == 4
        and area(union(a, b)) == 7
        and area(intersection(a, b)) == 1
        and area_ratio(a, 0) == 0
    )
    assert (
        components(a)[0] == 1
        and bounding_box(a) == (1, 1, 2, 2)
        and horizontal_runs(a, 1) == [(1, 3)]
    )
    rgb = np.zeros((5, 5, 3), np.uint8)
    assert not np.shares_memory(overlay(rgb, a), rgb)
    assert skeleton(a).dtype == bool


def test_hsv_wrap_and_invalid_shape():
    hsv = rgb_to_hsv(np.array([[[255, 0, 0]]], np.uint8))
    assert hsv_mask(hsv, (170, 100, 100), (10, 255, 255)).any()
    with pytest.raises(ValueError):
        area(np.zeros((2, 2, 2)))
