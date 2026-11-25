"""Row-wise foreground profiles anchored in the lower image."""

import cv2
import numpy as np


def bole_profile(rgb: np.ndarray, mode: int) -> tuple[np.ndarray, float]:
    small = cv2.resize(rgb, (192, 256), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).astype(np.float32)
    smooth = cv2.GaussianBlur(lab, (3, 5), 0)
    edge = np.linalg.norm(np.gradient(smooth, axis=1), axis=2)
    # Compare row centres with both flanks, using several scales simultaneously.
    radii = np.arange(2, 32)[:, None]
    centers = np.arange(54, 139)[None, :]
    left = centers - radii
    right = centers + radii
    mid = smooth[:, centers[0], :][:, None, :, :]

    def distance(a, b):
        return np.linalg.norm(a - b, axis=-1)

    dl = distance(mid, smooth[:, left - 2])
    dr = distance(mid, smooth[:, right + 2])
    interior = distance(mid, smooth[:, left + 1]) + distance(mid, smooth[:, right - 1])
    woody = np.clip((mid[..., 1] - 109) / 16, 0, 1)
    support = (
        np.minimum(np.minimum(dl, dr), 65) / 55
        + np.minimum(np.minimum(edge[:, left], edge[:, right]), 25) / 20
        - np.minimum(interior, 100) / 120
    ) * woody
    support -= 0.45 * (abs(centers - 96) / 40) ** 2
    # Estimate a ground contact from persistence above and loss of support below.
    flat = support.reshape(256, -1)
    up = cv2.blur(flat, (1, 16), anchor=(0, 15))
    down = cv2.blur(flat, (1, 7), anchor=(0, 0))
    scores = (up - 0.45 * down).reshape(support.shape)
    scores -= ((np.arange(256)[:, None, None] - 234) / 62) ** 2
    scores[:155] = -10
    by, ri, ci = np.unravel_index(scores.argmax(), scores.shape)
    base_score = float(scores[by, ri, ci])
    mask = np.zeros((256, 192), bool)
    color = np.median(smooth[max(0, by - 10) : by + 1, centers[0, ci]], axis=0)
    misses = 0
    for y in range(int(by), max(0, by - 202), -1):
        likelihood = (
            support[y] - 0.19 * abs(radii - radii[ri]) - 0.29 * abs(centers - centers[0, ci])
        )
        if mode >= 4:
            likelihood -= np.minimum(distance(mid[y], color), 100) / 70
        r, c = np.unravel_index(likelihood.argmax(), likelihood.shape)
        if likelihood[r, c] < 0.07:
            misses += 1
            if misses >= 5:
                break
            continue
        misses = 0
        ri, ci = r, c
        x = int(centers[0, c])
        left_edge = int(left[r, c])
        end = int(right[r, c])
        if mode >= 4:
            color = 0.94 * color + 0.06 * smooth[y, x]
        pixels = lab[y, left_edge : end + 1]
        mask[y, left_edge : end + 1] = distance(pixels, smooth[y, x]) <= max(
            32, np.quantile(distance(pixels, smooth[y, x]), 0.75)
        )
    return cv2.resize(
        mask.astype(np.uint8), rgb.shape[1::-1], interpolation=cv2.INTER_NEAREST
    ) > 0, base_score
