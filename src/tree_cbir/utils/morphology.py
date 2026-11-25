import cv2
import numpy as np
from scipy.ndimage import binary_fill_holes
from skimage.morphology import skeletonize

from .masks import to_cv_mask, validate_mask


def _k(size):
    return np.ones((size, size), np.uint8)


def erode(mask, size=3):
    return cv2.erode(to_cv_mask(mask), _k(size)).astype(bool)


def dilate(mask, size=3):
    return cv2.dilate(to_cv_mask(mask), _k(size)).astype(bool)


def opening(mask, size=3):
    return cv2.morphologyEx(to_cv_mask(mask), cv2.MORPH_OPEN, _k(size)).astype(bool)


def closing(mask, size=3):
    return cv2.morphologyEx(to_cv_mask(mask), cv2.MORPH_CLOSE, _k(size)).astype(bool)


def fill_holes(mask):
    return binary_fill_holes(validate_mask(mask))


def skeleton(mask):
    return skeletonize(validate_mask(mask))
