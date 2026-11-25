"""Boolean masks are H×W and indexed [y, x]."""

import cv2
import numpy as np


def validate_mask(mask):
    if mask.ndim != 2:
        raise ValueError("mask must be 2D")
    return mask.astype(bool, copy=False)


def to_cv_mask(mask):
    return validate_mask(mask).astype(np.uint8) * 255


def union(a, b):
    return validate_mask(a) | validate_mask(b)


def intersection(a, b):
    return validate_mask(a) & validate_mask(b)


def subtract(a, b):
    return validate_mask(a) & ~validate_mask(b)


def area(mask):
    return int(validate_mask(mask).sum())


def area_ratio(mask, denominator):
    return area(mask) / denominator if denominator else 0.0


def components(mask):
    count, labels = cv2.connectedComponents(to_cv_mask(mask))
    return count - 1, labels


def remove_small(mask, minimum_area):
    count, labels, stats, _ = cv2.connectedComponentsWithStats(to_cv_mask(mask))
    return np.isin(
        labels, [i for i in range(1, count) if stats[i, cv2.CC_STAT_AREA] >= minimum_area]
    )
