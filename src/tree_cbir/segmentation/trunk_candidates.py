"""Actual multi-scale central/lower sliding-window candidate generation."""

from dataclasses import dataclass

import cv2
import numpy as np

from tree_cbir.utils.color import rgb_to_gray

from .trunk_scoring import clamp, weighted_score


@dataclass(frozen=True)
class CandidateConfig:
    widths: tuple[int, ...] = (32, 64, 112, 176)
    heights: tuple[int, ...] = (180, 300, 460, 640)
    stride: int = 32
    weights: tuple[float, ...] = (0.25, 0.2, 0.15, 0.25, 0.15)


@dataclass(frozen=True)
class Candidate:
    x: int
    y: int
    width: int
    height: int
    color: float
    edge: float
    shape: float
    position: float
    continuity: float
    score: float


def generate_candidates(
    rgb: np.ndarray, config: CandidateConfig = CandidateConfig(), top_k: int = 12
) -> tuple[list[Candidate], dict]:
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        return [], {"reason": "invalid RGB input"}
    height, width = rgb.shape[:2]
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    bark = ((hsv[:, :, 1] < 175) & (hsv[:, :, 2] < 225)).astype(np.uint8)
    edges = (cv2.Canny(rgb_to_gray(rgb), 50, 150) > 0).astype(np.uint8)
    result = []
    for window_width in config.widths:
        for window_height in config.heights:
            for y in range(int(height * 0.18), height - window_height + 1, config.stride):
                for x in range(
                    int(width * 0.12), int(width * 0.88) - window_width + 1, config.stride
                ):
                    color = clamp(float(bark[y : y + window_height, x : x + window_width].mean()))
                    edge = clamp(
                        float(edges[y : y + window_height, x : x + window_width].mean()) * 3
                    )
                    shape = clamp(window_height / window_width / 3.5) * clamp(
                        window_height / (height * 0.45)
                    )
                    position = clamp(
                        (1 - abs((x + window_width / 2) - width / 2) / (width / 2))
                        * min(1, (y + window_height) / height / 0.7)
                    )
                    continuity = clamp(
                        float(
                            np.any(
                                edges[
                                    y : y + window_height,
                                    x + window_width // 3 : x + 2 * window_width // 3,
                                ],
                                axis=1,
                            ).mean()
                        )
                        * 2
                    )
                    scores = (color, edge, shape, position, continuity)
                    result.append(
                        Candidate(
                            x,
                            y,
                            window_width,
                            window_height,
                            *scores,
                            weighted_score(scores, config.weights),
                        )
                    )
    result.sort(key=lambda item: (-item.score, item.y, item.x))
    kept = []
    for item in result:
        if all(_iou(item, other) < 0.45 for other in kept):
            kept.append(item)
        if len(kept) >= top_k:
            break
    return kept, {
        "bark_evidence": bark,
        "edge_evidence": edges,
        "candidate_count": len(result),
        "weights": config.weights,
    }


def _iou(a: Candidate, b: Candidate) -> float:
    x1, y1 = max(a.x, b.x), max(a.y, b.y)
    x2, y2 = min(a.x + a.width, b.x + b.width), min(a.y + a.height, b.y + b.height)
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    return (
        intersection / (a.width * a.height + b.width * b.height - intersection)
        if intersection
        else 0.0
    )
