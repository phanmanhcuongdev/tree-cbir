"""Competing woody components in the lower part of a centred tree."""

import cv2
import numpy as np


def lower_component(rgb: np.ndarray) -> tuple[np.ndarray, float]:
    small = cv2.resize(rgb, (192, 256), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).astype(np.float32)
    best = 0.0
    winner = np.zeros((256, 192), bool)
    for level in (56, 92, 134, 180):
        wood = (
            (lab[:, :, 0] < level)
            & (lab[:, :, 1] >= 118)
            & (lab[:, :, 1] < 149)
            & (lab[:, :, 2] < 160)
        )
        wood[:160] = False
        wood = cv2.morphologyEx(wood.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3, 2), np.uint8))
        # Break lateral connections to neighbouring shrubs and horizontal ground.
        wood = cv2.morphologyEx(wood, cv2.MORPH_OPEN, np.ones((7, 1), np.uint8))
        count, labels, stats, _ = cv2.connectedComponentsWithStats(wood)
        for i in range(1, count):
            x, y, w, h, area = stats[i]
            if area < 36 or not 4 <= w <= 75 or h < 12 or y + h < 211:
                continue
            m = labels == i
            ys, xs = np.where(m)
            principal = np.median(xs[ys >= np.quantile(ys, 0.6)])
            central = np.exp(-(((principal - 96) / 17) ** 2))
            fill = area / (w * h)
            score = (
                central
                * min(1, fill * 1.6)
                * min(1, h / 23)
                * min(1, w / 7)
                * np.exp(-(((y + h - 239) / 26) ** 2))
            )
            if score > best:
                winner = m
                best = score
    return cv2.resize(
        winner.astype(np.uint8), rgb.shape[1::-1], interpolation=cv2.INTER_NEAREST
    ) > 0, float(best)
