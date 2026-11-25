"""Competing lower-bole hypotheses from local, bilateral colour contrast."""

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class GroundProposal:
    mask: np.ndarray
    region: tuple[int, int, int, int]
    support: float
    foliage: float


def ground_proposal(rgb: np.ndarray, version: int) -> GroundProposal:
    height, width = rgb.shape[:2]
    small = cv2.resize(rgb, (192, 256), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).astype(np.float32)
    y, x = np.indices((256, 192))
    green = np.clip((125 - lab[:, :, 1]) / 12, 0, 1)
    chroma = np.linalg.norm(lab[:, :, 1:] - 128, axis=2)
    bark = 1 - np.clip((chroma - 21) / 42, 0, 1)
    best = -np.inf
    for radius in [2, 4, 7, 12, 20, 29]:
        smooth = cv2.blur(lab, (2 * radius + 1, 5))
        left = np.roll(smooth, 2 * radius + 1, axis=1)
        right = np.roll(smooth, -2 * radius - 1, axis=1)
        contrast = np.minimum(
            np.linalg.norm(smooth - left, axis=2), np.linalg.norm(smooth - right, axis=2)
        )
        signal = np.minimum(contrast / 48, 1.5) * (1 - 0.7 * green) * (0.4 + 0.6 * bark)
        for length in (12, 24, 48, 84):
            above = cv2.blur(signal, (3, length), anchor=(1, length - 1))
            below = cv2.blur(signal, (3, 9), anchor=(1, 0))
            score = above - 0.43 * below
            score *= np.exp(-(((x - 96) / 39) ** 2) - ((y - 230) / 54) ** 2)
            score[(y < 145) | (y > 252) | (abs(x - 96) > 48)] = -1
            by, cx = np.unravel_index(score.argmax(), score.shape)
            if score[by, cx] > best:
                best = score[by, cx]
                selection = int(cx), int(by), radius, length
    cx, by, radius, length = selection
    labels = np.zeros((256, 192), np.uint8)
    top = max(0, by - length)
    labels[top : by + 1, cx - radius : cx + radius + 1] = cv2.GC_PR_FGD
    if version >= 2 and best > 0.02:
        pad = max(4, radius)
        labels[
            max(0, top - length // 2) : min(256, by + 5), cx - radius - pad : cx + radius + pad + 1
        ] = cv2.GC_PR_BGD
        labels[top : by + 1, cx - radius : cx + radius + 1] = cv2.GC_PR_FGD
        labels[top + length // 3 : by - 1, cx : cx + 1] = cv2.GC_FGD
        cv2.setRNGSeed(2026)
        cv2.grabCut(small, labels, None, None, None, 2, cv2.GC_INIT_WITH_MASK)
    observed = ((labels % 2) == 1) & (green < 0.85) & (best > 0.02)
    rect = (
        round((cx - radius) * width / 192),
        round(top * height / 256),
        round((2 * radius + 1) * width / 192),
        round((length + 1) * height / 256),
    )
    mask = (
        cv2.resize(observed.astype(np.uint8), (width, height), interpolation=cv2.INTER_NEAREST) > 0
    )
    return GroundProposal(
        mask, rect, float(best), float(green[observed].mean()) if observed.any() else 0.0
    )
