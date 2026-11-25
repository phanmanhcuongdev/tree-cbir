"""Upper-left origin; x right, y down; arrays index [y, x]."""

import cv2
import numpy as np

from .masks import to_cv_mask, validate_mask


def bounding_box(mask):
    points = cv2.findNonZero(to_cv_mask(mask))
    return tuple(cv2.boundingRect(points)) if points is not None else None


def extract_roi(image, bounds):
    x, y, w, h = bounds
    if x < 0 or y < 0 or w < 0 or h < 0 or x + w > image.shape[1] or y + h > image.shape[0]:
        raise ValueError("invalid ROI")
    return image[y : y + h, x : x + w]


def contours(mask):
    return cv2.findContours(to_cv_mask(mask), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]


def solidity(contour):
    hull = cv2.convexHull(contour)
    return cv2.contourArea(contour) / cv2.contourArea(hull) if cv2.contourArea(hull) else 0.0


def circularity(contour):
    p = cv2.arcLength(contour, True)
    return 4 * np.pi * cv2.contourArea(contour) / (p * p) if p else 0.0


def horizontal_runs(mask, y):
    row = validate_mask(mask)[y]
    edges = np.diff(np.r_[False, row, False].astype(np.int8))
    return list(zip(np.where(edges == 1)[0], np.where(edges == -1)[0]))
