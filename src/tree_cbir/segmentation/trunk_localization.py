"""Locate persistent paired trunk boundaries and track their observed pixels."""

from dataclasses import dataclass

import cv2
import numpy as np

from .trunk_candidates import Candidate

# Slices use half-open x coordinates.
Slice = tuple[int, int, int]


@dataclass(frozen=True)
class Localization:
    axis: tuple[Slice, ...]
    base: tuple[int, int]
    region: tuple[int, int, int, int]
    ambiguous: bool


def _bands(lab: np.ndarray, y: int, left: int, right: int):
    """Find color transitions along a locally averaged horizontal slice."""
    radius = max(1, round(lab.shape[0] / 220))
    row = lab[max(0, y - radius) : y + radius + 1].mean(axis=0)
    delta = np.linalg.norm(np.diff(row, axis=0), axis=1)
    edges = np.flatnonzero(delta[left : right - 1] >= 9) + left + 1
    return row, edges


def _fit(row, left, right, reference=None):
    if left < 2 or right + 2 > len(row) or right - left < 3:
        return None
    pixels = row[left:right]
    color = np.median(pixels, axis=0)
    spread = np.linalg.norm(pixels - color, axis=1)
    contrast = min(
        np.linalg.norm(color - row[left - 2 : left].mean(axis=0)),
        np.linalg.norm(color - row[right : right + 2].mean(axis=0)),
    )
    if contrast < 12 or np.mean(spread <= 24) < 0.78:
        return None
    if reference is not None and np.linalg.norm(color - reference) > 23:
        return None
    return color, float(min(contrast, 65) - spread.mean())


def track_boundaries(lab: np.ndarray, seed: Slice) -> tuple[Slice, ...]:
    """Walk both directions and leave short breaks unfilled."""
    y, left, right = seed
    row, _ = _bands(lab, y, 0, lab.shape[1])
    initial = _fit(row, left, right)
    if initial is None:
        return ()
    result = [seed]
    for direction in (-1, 1):
        old_left, old_right = left, right
        reference = initial[0]
        misses = 0
        for yy in range(y + direction, lab.shape[0] if direction > 0 else -1, direction):
            radius = min(8, max(2, (old_right - old_left) // 9))
            row, edges = _bands(
                lab,
                yy,
                max(0, old_left - radius - 1),
                min(lab.shape[1], old_right + radius + 1),
            )
            best = None
            best_score = -np.inf
            for ll in edges[abs(edges - old_left) <= radius]:
                for rr in edges[abs(edges - old_right) <= radius]:
                    if not 0.55 * (right - left) <= rr - ll <= 1.9 * (right - left):
                        continue
                    fit = _fit(row, ll, rr, reference)
                    if fit is None or np.linalg.norm(fit[0] - initial[0]) > 32:
                        continue
                    score = fit[1] - 2 * (abs(ll - old_left) + abs(rr - old_right))
                    if score > best_score:
                        best, best_score = (int(ll), int(rr), fit[0]), score
            if best is None:
                misses += 1
                if misses > max(1, lab.shape[0] // 300):
                    break
                continue
            misses = 0
            old_left, old_right, color = best
            reference = 0.8 * reference + 0.2 * color
            result.append((yy, old_left, old_right))
    return tuple(sorted(result))


def localize_trunk(lab: np.ndarray, *, base_first: bool = False) -> Localization | None:
    """Search for long, locally contrasting bands at reduced resolution."""
    height, width = lab.shape[:2]
    scale = min(1.0, 144 / max(height, width))
    small = cv2.resize(
        lab,
        (max(1, round(width * scale)), max(1, round(height * scale))),
        interpolation=cv2.INTER_AREA,
    )
    h, w = small.shape[:2]
    paths = []
    for y in range(h // 4, h, max(3, h // 24)):
        row, edges = _bands(small, y, int(w * 0.12), int(w * 0.88))
        seeds = []
        for left in edges:
            for right in edges[(edges - left >= 3) & (edges - left <= max(4, w // 3))]:
                fit = _fit(row, left, right)
                if fit is not None:
                    centrality = 1 - abs((left + right) / w - 1)
                    # Strongly green interiors commonly belong to foliage or grass.
                    green_penalty = max(0, 115 - float(fit[0][1]))
                    seeds.append((fit[1] + 16 * centrality - green_penalty, int(left), int(right)))
        for _, left, right in sorted(seeds, reverse=True)[:5]:
            path = track_boundaries(small, (y, left, right))
            if len(path) >= max(6, h * (0.06 if base_first else 0.12)):
                widths = np.array([right - left for _, left, right in path])
                if len(path) / np.median(widths) < 1.5:
                    continue
                centers = [(left + right) / 2 for _, left, right in path]
                base_y, base_left, base_right = path[-1]
                # A transition from the band into the surrounding surface supports a base.
                below = small[base_y + 2 : base_y + 6, base_left:base_right]
                end = np.median(small[base_y, base_left:base_right], axis=0)
                transition = (
                    min(1.0, float(np.linalg.norm(np.median(below, axis=(0, 1)) - end)) / 40)
                    if below.size
                    else 0.0
                )
                center_weight = 1 - 0.65 * abs(2 * np.median(centers) / w - 1)
                score = center_weight * (len(path) + 0.15 * base_y * transition)
                if base_first:
                    score = center_weight**2 * (
                        min(len(path), h * 0.32)
                        + h * 0.55 * (base_y / h) ** 3
                        + h * 0.13 * transition
                    )
                paths.append((score, path))
    if not paths:
        return None
    score, best = max(paths)
    best_rows = {y: (left + right) / 2 for y, left, right in best}
    ambiguous = False
    for other_score, other in paths:
        shared = [
            abs(best_rows[y] - (left + right) / 2) for y, left, right in other if y in best_rows
        ]
        if other_score >= 0.85 * score and (not shared or np.median(shared) > 0.12 * w):
            ambiguous = True
            break
    axis = tuple(
        (round((y + 0.5) * height / h - 0.5), round(left * width / w), round(right * width / w))
        for y, left, right in best
    )
    base_y, left, right = axis[-1]
    min_x = min(left for _, left, _ in axis)
    max_x = max(right for _, _, right in axis)
    return Localization(
        axis,
        ((left + right) // 2, base_y),
        (min_x, axis[0][0], max_x - min_x, base_y - axis[0][0] + 1),
        ambiguous,
    )


def select_seed(lab: np.ndarray, location: Localization, candidates: list[Candidate]):
    """Require a candidate to intersect the traced axis and reach toward its base."""
    ranked = []
    base_y = location.base[1]
    height = location.region[3]
    for candidate in candidates:
        matching = [
            (y, left, right)
            for y, left, right in location.axis
            if candidate.y <= y < candidate.y + candidate.height
            and candidate.x <= (left + right) / 2 < candidate.x + candidate.width
        ]
        if len(matching) < max(2, len(location.axis) * 0.15):
            continue
        gap = max(0, base_y - candidate.y - candidate.height)
        if gap > 0.65 * height:
            continue
        ranked.append(
            (
                candidate.score + len(matching) / len(location.axis) - gap / height,
                candidate,
                matching,
            )
        )
    for _, candidate, matching in sorted(ranked, key=lambda item: -item[0]):
        trials = []
        step = max(1, len(matching) // 6)
        for y, left, right in matching[::step]:
            radius = max(3, min(12, (right - left) // 3))
            row, edges = _bands(
                lab, y, max(0, left - radius - 1), min(lab.shape[1], right + radius + 1)
            )
            fits = []
            for ll in edges[abs(edges - left) <= radius]:
                for rr in edges[abs(edges - right) <= radius]:
                    fit = _fit(row, ll, rr)
                    if fit is not None:
                        fits.append((fit[1] - abs(ll - left) - abs(rr - right), int(ll), int(rr)))
            if fits:
                _, ll, rr = max(fits)
                seed = (y, ll, rr)
                trace = track_boundaries(lab, seed)
                trials.append((len(trace), seed, trace))
        if trials:
            _, seed, trace = max(trials)
            return candidate, seed, trace
    return None
