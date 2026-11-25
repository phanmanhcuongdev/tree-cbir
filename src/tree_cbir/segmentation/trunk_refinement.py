"""Constrained P03.2 pixel mask refinement for ranked trunk candidates."""

import cv2
import numpy as np

from tree_cbir.utils.color import rgb_to_gray

from .trunk_candidates import Candidate


def refine_mask(rgb: np.ndarray, candidates: list[Candidate]) -> tuple[np.ndarray, dict]:
    height, width = rgb.shape[:2]
    empty = np.zeros((height, width), bool)
    if not candidates:
        return empty, {"status": "UNCERTAIN_DETECTION", "reason": "no candidates", "components": 0}
    selected = candidates[0]
    x, y, w, h = selected.x, selected.y, selected.width, selected.height
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    roi = hsv[y : y + h, x : x + w]
    gray = rgb_to_gray(rgb)[y : y + h, x : x + w]
    color = (roi[:, :, 1] < 180) & (roi[:, :, 2] < 230)
    edges = cv2.Canny(gray, 50, 150) > 0
    preliminary = cv2.morphologyEx(
        (
            color & (edges | cv2.dilate(edges.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0)
        ).astype(np.uint8)
        * 255,
        cv2.MORPH_CLOSE,
        np.ones((3, 3), np.uint8),
    )
    n, labels, stats, _ = cv2.connectedComponentsWithStats(preliminary)
    keep = [i for i in range(1, n) if stats[i, 4] >= max(12, h * 0.15)]
    refined = np.zeros_like(empty)
    refined[y : y + h, x : x + w] = np.isin(labels, keep)
    count = len(keep)
    coverage = float(refined[y : y + h, x : x + w].any(axis=1).mean())
    confidence = float(np.clip(0.45 * coverage + 0.25 * selected.score, 0, 1))
    status = (
        "RELIABLE_DETECTION"
        if count and confidence >= 0.55 and coverage >= 0.45
        else "PARTIAL_DETECTION"
        if count
        else "UNCERTAIN_DETECTION"
    )
    return refined, {
        "status": status,
        "components": count,
        "selected_roi": (x, y, w, h),
        "candidate_score": selected.score,
        "confidence": confidence,
        "coverage": coverage,
        "reason": None if count else "weak pixel evidence",
    }
