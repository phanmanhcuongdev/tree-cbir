"""RGB helpers; OpenCV uint8 HSV uses H 0–179 and S/V 0–255."""

import cv2
import numpy as np


def rgb_to_hsv(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)


def rgb_to_gray(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)


def rgb_to_bgr(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def bgr_to_rgb(bgr):
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def hsv_mask(hsv, lower, upper):
    low, high = np.array(lower, np.uint8), np.array(upper, np.uint8)
    if lower[0] <= upper[0]:
        return cv2.inRange(hsv, low, high).astype(bool)
    return (
        cv2.inRange(hsv, low, np.array((179, upper[1], upper[2]), np.uint8))
        | cv2.inRange(hsv, np.array((0, lower[1], lower[2]), np.uint8), high)
    ).astype(bool)
