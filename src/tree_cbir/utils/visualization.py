import cv2
import numpy as np

from .geometry import bounding_box, contours
from .masks import to_cv_mask


def mask_image(mask):
    return to_cv_mask(mask)


def overlay(rgb, mask, color=(255, 0, 0), alpha=0.4):
    output = rgb.copy()
    layer = np.zeros_like(rgb)
    layer[to_cv_mask(mask) > 0] = color
    return cv2.addWeighted(output, 1, layer, alpha, 0)


def contour_overlay(rgb, mask):
    output = rgb.copy()
    cv2.drawContours(output, contours(mask), -1, (255, 0, 0), 2)
    return output


def box_overlay(rgb, mask):
    output = rgb.copy()
    box = bounding_box(mask)
    if box:
        x, y, w, h = box
        cv2.rectangle(output, (x, y), (x + w, y + h), (255, 0, 0), 2)
    return output
