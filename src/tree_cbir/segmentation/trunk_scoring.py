"""Finite [0,1] heuristic scores for P03.1 trunk proposals."""

import numpy as np


def clamp(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def weighted_score(
    scores: tuple[float, float, float, float, float], weights: tuple[float, ...]
) -> float:
    if (
        len(weights) != 5
        or any(weight < 0 for weight in weights)
        or not np.isclose(sum(weights), 1)
    ):
        raise ValueError("five nonnegative weights must sum to 1")
    return clamp(float(np.dot(scores, weights)))
