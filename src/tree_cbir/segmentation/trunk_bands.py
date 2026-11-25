"""Link horizontally contrasting trunk bands with a smooth scale-space path."""

import cv2
import numpy as np

from .trunk_localization import Slice


def band_path(lab: np.ndarray) -> tuple[Slice, ...]:
    height, width = lab.shape[:2]
    scale = min(1.0, 256 / height)
    h, w = round(height * scale), round(width * scale)
    if min(h, w) < 20:
        return ()
    small = cv2.resize(lab, (w, h), interpolation=cv2.INTER_AREA)
    smoothed = cv2.blur(small, (1, 5))
    sums = np.pad(smoothed.cumsum(axis=1), ((0, 0), (1, 0), (0, 0)))
    widths = np.arange(2, max(3, w // 9))[:, None]
    centers = np.arange(w)[None, :]
    left, right = centers - widths, centers + widths
    margin = np.maximum(2, widths // 2)
    outer_left, outer_right = np.maximum(0, left - margin), np.minimum(w, right + margin)
    in_bounds = (left >= margin) & (right <= w - margin)
    left, right = np.clip(left, 0, w), np.clip(right, 0, w)
    body = (sums[:, right] - sums[:, left]) / (2 * widths[..., None])
    flank_left = (sums[:, left] - sums[:, outer_left]) / margin[..., None]
    flank_right = (sums[:, outer_right] - sums[:, right]) / margin[..., None]
    dl, dr = body - flank_left, body - flank_right
    contrast = np.minimum(np.linalg.norm(dl, axis=-1), np.linalg.norm(dr, axis=-1))
    shared = np.sum(dl * dr, axis=-1) >= 0
    edge = np.linalg.norm(np.diff(smoothed, axis=1, prepend=smoothed[:, :1]), axis=-1)
    edge = cv2.dilate(edge, np.ones((1, 3), np.uint8))
    boundary = np.minimum(edge[:, np.minimum(w - 1, left)], edge[:, np.minimum(w - 1, right)])
    central = np.abs(2 * centers / w - 1)
    green = np.clip((115 - body[..., 1]) / 25, 0, 1)
    evidence = (
        (0.60 * np.clip((contrast - 9) / 29, 0, 1) + 0.40 * np.clip((boundary - 4) / 21, 0, 1))
        * np.where(shared, 1, 0.55)
        * (1 - 0.65 * green)
    )
    reward = evidence - 0.38 - 0.31 * central
    reward[:, ~in_bounds] = -10
    # Ascent can start at any row. A lower starting band receives a soft prior.
    scores = np.zeros(left.shape)
    predecessors = np.zeros((h, *left.shape), np.int8)
    height_index, x_index = np.indices(left.shape)
    moves = (
        (0, 0),
        (0, 1),
        (0, -1),
        (1, 0),
        (-1, 0),
        (1, 1),
        (1, -1),
        (-1, 1),
        (-1, -1),
        (0, 2),
        (0, -2),
    )
    best = (0.0, 0, 0, 0)
    for y in range(h - 1, h // 5, -1):
        start = np.where(evidence[y] >= 0.42, 8 * (y / h) ** 3, -1.0)
        options = [start]
        for di, dx in moves:
            ni, nx = height_index + di, x_index + dx
            previous = scores[np.clip(ni, 0, len(widths) - 1), np.clip(nx, 0, w - 1)]
            valid = (ni >= 0) & (ni < len(widths)) & (nx >= 0) & (nx < w) & (previous > 0)
            options.append(np.where(valid, previous - 0.045 * (abs(di) + abs(dx)), -1))
        options = np.array(options)
        predecessors[y] = options.argmax(axis=0)
        scores = np.maximum(0, options.max(axis=0) + reward[y])
        i, x = np.unravel_index(scores.argmax(), scores.shape)
        if scores[i, x] > best[0]:
            best = (float(scores[i, x]), y, i, x)
    _, y, i, x = best
    trace = []
    for row in range(y, h):
        trace.append((row, int(left[i, x]), int(right[i, x]), evidence[row, i, x] >= 0.26))
        code = predecessors[row, i, x]
        if code == 0:
            break
        di, dx = moves[code - 1]
        i, x = i + di, x + dx
    # Stop at long unsupported regions. Keep the longest observed segment.
    groups: list[list[tuple[int, int, int]]] = [[]]
    misses = 0
    for y, left_x, right_x, seen in trace:
        if seen:
            if misses > 3:
                groups.append([])
            groups[-1].append((y, left_x, right_x))
            misses = 0
        else:
            misses += 1
    observed = max(groups, key=len)
    if len(observed) < max(7, h * 0.055):
        return ()
    result = []
    for y, left_x, right_x in observed:
        for full_y in range(round(y * height / h), round((y + 1) * height / h)):
            result.append((full_y, round(left_x * width / w), round(right_x * width / w)))
    return tuple(result)
