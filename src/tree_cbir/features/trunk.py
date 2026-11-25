"""Raw X0–X8 measurements from a supplied trunk mask."""

import cv2
import numpy as np

from tree_cbir.utils.color import rgb_to_hsv
from tree_cbir.utils.geometry import horizontal_runs
from tree_cbir.utils.morphology import skeleton


def extract_trunk_features(rgb, mask, expected_height):
    values = np.zeros(9)
    valid = np.zeros(9, dtype=bool)
    ys = np.where(mask.any(axis=1))[0]
    if not len(ys) or expected_height <= 0:
        return values, valid, {"semantic": "uncertain"}
    height = ys[-1] - ys[0] + 1
    values[0] = height / expected_height
    valid[0] = True
    hsv = rgb_to_hsv(rgb)
    pixels = hsv[mask]
    if len(pixels):
        values[1:4] = np.median(pixels, axis=0)
        valid[1:4] = True
    sample = np.linspace(ys[0], ys[-1], min(20, len(ys)), dtype=int)
    centers = []
    widths = []
    runs = []
    for y in sample:
        r = horizontal_runs(mask, y)
        if r:
            left = min(a for a, b in r)
            right = max(b for a, b in r)
            widths.append(right - left)
            centers.append((y, (left + right) / 2))
            runs.append(len(r))
    if widths:
        values[4] = np.median(widths) / mask.shape[1]
        valid[4] = True
    if len(centers) >= 2:
        y, x = np.array(centers).T
        a, b = np.polyfit(y, x, 1)
        res = x - (a * y + b)
        values[5] = abs(np.degrees(np.arctan(a)))
        values[6] = np.sqrt(np.mean(res**2)) / height
        valid[5:7] = True
    if runs:
        values[7] = np.median(runs)
        valid[7] = True
    sk = skeleton(mask)
    lower = sk[int((ys[0] + ys[-1]) / 2) :]
    n = cv2.filter2D(lower.astype(np.uint8), -1, np.ones((3, 3), np.uint8))
    values[8] = int(((n >= 4) & lower).sum() > 0)
    valid[8] = True
    return values, valid, {"semantic": "clearly visible" if values[0] > 0.6 else "partial"}
