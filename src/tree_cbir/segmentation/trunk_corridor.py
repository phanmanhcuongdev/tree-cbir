"""Recover weakly textured interior using a spatially bounded foreground model."""

import cv2
import numpy as np


def recover_corridor(rgb: np.ndarray, mask: np.ndarray, axis: tuple, wide: bool) -> np.ndarray:
    if len(axis) < 5 or not mask.any():
        return mask
    h, w = mask.shape
    small = cv2.resize(rgb, (192, 256), interpolation=cv2.INTER_AREA)
    labels = np.zeros((256, 192), np.uint8)
    prior = cv2.resize(mask.astype(np.uint8), (192, 256), interpolation=cv2.INTER_AREA) > 0
    labels[prior] = cv2.GC_PR_FGD
    trace = np.asarray(axis)
    for y in np.flatnonzero(prior.any(axis=1)):
        left, right = np.round(
            [np.interp(y * h / 256, trace[:, 0], trace[:, k]) * 192 / w for k in (1, 2)]
        ).astype(int)
        radius = max(2, (right - left) // 2)
        mid = (left + right) // 2
        pad = max(3, radius * (2 if wide else 1))
        labels[y, max(0, left - pad) : right + pad + 1] = cv2.GC_PR_BGD
        labels[y, max(0, left) : right + 1] = cv2.GC_PR_FGD
        if 0 <= mid < 192 and prior[y, mid] and y % 3 == 0:
            labels[y, mid] = cv2.GC_FGD
    if (labels == cv2.GC_FGD).sum() < 5:
        return mask
    cv2.setRNGSeed(2026)
    cv2.grabCut(small, labels, None, None, None, 3, cv2.GC_INIT_WITH_MASK)
    candidate = (
        cv2.resize((labels % 2).astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST) > 0
    )
    return candidate if candidate.sum() > 0.55 * mask.sum() else mask


def open_background(rgb: np.ndarray, mask: np.ndarray) -> bool:
    """Estimate whether upper attachment evidence can be separated from distant scene."""
    small = cv2.resize(rgb, (192, 256), interpolation=cv2.INTER_AREA)
    ys, xs = np.where(mask)
    if not len(xs):
        return False
    cx = round(float(np.median(xs)) * 192 / mask.shape[1])
    top = round(float(ys.min()) * 256 / mask.shape[0])
    bottom = round(float(ys.max()) * 256 / mask.shape[0])
    flank = small[top : (top + bottom) // 2 + 1, max(0, cx - 40) : max(1, cx - 16)]
    if not flank.size:
        return False
    return float(np.mean(flank.min(axis=2) > 145)) > 0.5
