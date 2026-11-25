"""Detect the lower crown or a woody lateral attachment near the observed bole."""

import cv2
import numpy as np


def trim_at_crown(rgb: np.ndarray, mask: np.ndarray, branches: bool) -> np.ndarray:
    h, w = mask.shape
    lab = cv2.cvtColor(
        cv2.resize(rgb, (192, 256), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2LAB
    ).astype(float)
    small = cv2.resize(mask.astype(np.uint8), (192, 256), interpolation=cv2.INTER_NEAREST)
    ys = np.flatnonzero(small.any(axis=1))
    if len(ys) < 24:
        return mask
    run = 0
    for y in ys[::-1]:
        if y > ys[-1] - 12:
            continue
        xs = np.flatnonzero(small[y])
        x = int(np.median(xs))
        radius = max(3, min(24, (xs[-1] - xs[0] + 1) // 2))
        outer = np.r_[
            max(0, x - 3 * radius) : max(0, x - radius - 2),
            min(192, x + radius + 3) : min(192, x + 3 * radius + 1),
        ]
        if len(outer) < 4:
            continue
        flank = lab[y, outer]
        foliage = (np.linalg.norm(flank[:, 1:] - 128, axis=1) > 29) & (
            (flank[:, 1] < 121) | (flank[:, 1] > 139) | (flank[:, 2] > 158)
        )
        near = np.linalg.norm(flank - np.median(lab[y, xs], axis=0), axis=1) < 29
        attached = branches and near.mean() > 0.24 and np.std(flank[:, 0]) > 24
        run = run + 1 if foliage.mean() > 0.52 or attached else 0
        if run >= 5:
            result = mask.copy()
            result[: round((y + 3) * h / 256)] = False
            return result
    return mask
