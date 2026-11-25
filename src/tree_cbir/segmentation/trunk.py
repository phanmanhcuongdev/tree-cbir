"""Heuristic multi-scale trunk proposals; confidence is not calibrated."""

from dataclasses import dataclass

import cv2
import numpy as np

from .trunk_bands import band_path
from .trunk_candidates import generate_candidates
from .trunk_localization import localize_trunk, select_seed


@dataclass(frozen=True)
class TrunkSegmentation:
    mask: np.ndarray
    bbox: tuple[int, int, int, int] | None
    base: tuple[int, int] | None
    upper: tuple[int, int] | None
    expected_height: float
    confidence: float
    diagnostics: dict


DEFAULT_TRUNK_METHOD = "hybrid"


def segment_trunk(rgb: np.ndarray, *, method: str = DEFAULT_TRUNK_METHOD) -> TrunkSegmentation:
    """Localize a probable trunk, then trace both boundaries from a compatible seed."""
    mask = np.zeros(rgb.shape[:2], dtype=bool)
    height = rgb.shape[0]
    diagnostics = {"status": "UNCERTAIN_DETECTION", "expected_height_confidence": 0.0}
    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8 or not rgb.size:
        raise ValueError("expected a nonempty RGB uint8 image")
    if method == "v2":
        from .trunk_v2 import refine

        return refine(rgb, segment_trunk(rgb, method="hybrid"), 10)
    if method not in {"baseline", "base_priority", "bands", "hybrid", "hybrid_structural"}:
        raise ValueError(f"unknown trunk segmentation method: {method}")
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    if method in {"bands", "hybrid", "hybrid_structural"}:
        if method == "bands":
            return _segment_bands(rgb, lab)
        paired = segment_trunk(rgb, method="base_priority")
        roi = paired.diagnostics.get("coarse_region")
        if (
            paired.bbox is not None
            and paired.base is not None
            and roi
            and paired.base[1] > 0.59 * height
            and paired.diagnostics.get("base_agreement", 0) > 0.75
            and paired.diagnostics.get("axis_agreement", 0) > 0.55
        ):
            if method == "hybrid_structural":
                return _trim_foliage(paired, lab)
            return paired
        return _segment_bands(rgb, lab, grabcut=True, structural=method == "hybrid_structural")
    location = localize_trunk(lab, base_first=method == "base_priority")
    if location is None:
        diagnostics["reason"] = "no persistent paired boundaries"
        return TrunkSegmentation(mask, None, None, None, height * 0.6, 0.0, diagnostics)

    diagnostics.update(
        probable_base=location.base,
        coarse_region=location.region,
        ambiguous=location.ambiguous,
        axis=location.axis,
    )
    candidates, _ = generate_candidates(rgb, top_k=100)
    selected = select_seed(lab, location, candidates)
    if selected is None:
        diagnostics["reason"] = "no candidate with a supported boundary pair on the coarse axis"
        return TrunkSegmentation(mask, None, None, None, height * 0.6, 0.0, diagnostics)
    candidate, seed, trace = selected
    diagnostics.update(
        selected_roi=(candidate.x, candidate.y, candidate.width, candidate.height),
        candidate_score=candidate.score,
        seed=seed,
    )
    if len(trace) < max(4, height * 0.035):
        diagnostics["reason"] = "full-resolution boundary trace too short"
        return TrunkSegmentation(mask, None, None, None, height * 0.6, 0.0, diagnostics)

    boundary_support = []
    for y, left, right in trace:
        pixels = lab[y, left:right]
        center = np.median(pixels, axis=0)
        mask[y, left:right] = np.linalg.norm(pixels - center, axis=1) <= 24
        boundary_support.append(
            min(
                np.linalg.norm(center - lab[y, left - 2 : left].mean(axis=0)),
                np.linalg.norm(center - lab[y, right : right + 2].mean(axis=0)),
            )
            >= 12
        )
    band_pixels = sum(right - left for _, left, right in trace)
    leakage_risk = 1 - int(mask.sum()) / band_pixels
    green_fraction = float(np.mean(lab[mask, 1] < 110)) if mask.any() else 0.0
    trace_by_y = {y: (left, right) for y, left, right in trace}
    agreement = sum(
        y in trace_by_y
        and abs(sum(trace_by_y[y]) / 2 - (left + right) / 2) <= max(5, (right - left) * 0.4)
        for y, left, right in location.axis
    ) / len(location.axis)
    base_y, left, right = trace[-1]
    top_y, top_left, top_right = trace[0]
    base = ((left + right) // 2, base_y)
    base_agreement = max(
        0.0,
        1
        - float(np.linalg.norm(np.subtract(base, location.base)))
        / max(1, location.region[3] * 0.35),
    )
    paired = float(np.mean(boundary_support))
    confidence = (
        (0.4 * agreement + 0.3 * paired + 0.3 * base_agreement)
        * (1 - leakage_risk)
        * (1 - green_fraction)
    )
    reasons = []
    if location.ambiguous:
        reasons.append("competing coarse axes")
    if agreement < 0.7 or paired < 0.7 or base_agreement < 0.65 or leakage_risk > 0.12:
        reasons.append("insufficient axis, base, or boundary agreement")
    if green_fraction > 0.35:
        reasons.append("substantial green interior; possible vegetation leakage")
    # A boundary trace ending at the image border cannot establish a visible base.
    if base_y >= height - 2:
        reasons.append("base at image boundary")
    if reasons:
        confidence = min(confidence, 0.49)
    else:
        diagnostics["status"] = "RELIABLE_DETECTION"
    diagnostics.update(
        reason="; ".join(reasons) or None,
        axis_agreement=agreement,
        base_agreement=base_agreement,
        paired_boundary_support=paired,
        interior_color_rejection=leakage_risk,
        strong_green_fraction=green_fraction,
        pixels_outside_candidate=int(mask.sum())
        - int(
            mask[
                candidate.y : candidate.y + candidate.height,
                candidate.x : candidate.x + candidate.width,
            ].sum()
        ),
    )
    box = cv2.boundingRect(mask.astype(np.uint8)) if mask.any() else None
    return TrunkSegmentation(
        mask, box, base, ((top_left + top_right) // 2, top_y), height * 0.6, confidence, diagnostics
    )


def _segment_bands(
    rgb: np.ndarray, lab: np.ndarray, *, grabcut: bool = False, structural: bool = False
) -> TrunkSegmentation:
    mask = np.zeros(rgb.shape[:2], bool)
    height = rgb.shape[0]
    axis = band_path(lab)
    diag = {
        "axis": axis,
        "status": "UNCERTAIN_DETECTION",
        "backend": "bands",
        "expected_height_confidence": 0.0,
    }
    if not axis:
        diag["reason"] = "no persistent contrasting band"
        return TrunkSegmentation(mask, None, None, None, 0.6 * height, 0.0, diag)
    candidates, _ = generate_candidates(rgb, top_k=100)
    supported = []
    for candidate in candidates:
        overlap = [
            (y, left, right)
            for y, left, right in axis
            if candidate.y <= y < candidate.y + candidate.height
            and candidate.x <= (left + right) / 2 < candidate.x + candidate.width
        ]
        if len(overlap) >= max(3, len(axis) * 0.15):
            supported.append(
                (len(overlap) / len(axis) + 0.35 * candidate.score, candidate, overlap)
            )
    if not supported:
        diag["reason"] = "no sliding-window proposal supports the traced band"
        return TrunkSegmentation(mask, None, None, None, 0.6 * height, 0.0, diag)
    _, candidate, overlap = max(supported, key=lambda item: item[0])
    if structural:
        axis = _trim_branching_axis(axis, lab)
        diag["axis"] = axis
    boundary = []
    for y, left, right in axis:
        pixels = lab[y, left:right]
        center = np.median(pixels, axis=0)
        spread = np.linalg.norm(pixels - center, axis=1)
        mask[y, left:right] = spread <= max(26, min(44, 2.5 * np.median(spread)))
        boundary.append(
            min(
                np.linalg.norm(center - lab[y, max(0, left - 5) : left].mean(axis=0)),
                np.linalg.norm(center - lab[y, right : right + 5].mean(axis=0)),
            )
            >= 16
        )
    paired = float(np.mean(boundary))
    occupancy = int(mask.sum()) / sum(right - left for _, left, right in axis)
    if grabcut:
        mask = _grabcut_corridor(rgb, lab, axis, mask)
        diag["backend"] = "bands_grabcut"
    green = float(np.mean(lab[mask, 1] < 110))
    confidence = (0.65 * paired + 0.35 * occupancy) * (1 - green)
    base_y, left, right = axis[-1]
    top_y, top_left, top_right = axis[0]
    base = ((left + right) // 2, base_y)
    if (
        not grabcut
        and paired >= 0.72
        and occupancy >= 0.78
        and green < 0.15
        and base_y < height - 2
    ):
        diag["status"] = "RELIABLE_DETECTION"
        diag["reason"] = None
    else:
        confidence = min(0.49, confidence)
        diag["reason"] = "weak flank contrast, visible base, or foreground consistency"
    diag.update(
        seed=overlap[len(overlap) // 2],
        selected_roi=(candidate.x, candidate.y, candidate.width, candidate.height),
        candidate_score=candidate.score,
        paired_boundary_support=paired,
        interior_color_rejection=1 - occupancy,
        strong_green_fraction=green,
    )
    return TrunkSegmentation(
        mask,
        cv2.boundingRect(mask.astype(np.uint8)),
        base,
        ((top_left + top_right) // 2, top_y),
        0.6 * height,
        confidence,
        diag,
    )


def _grabcut_corridor(rgb, lab, axis, observed):
    """Use observed color cores as seeds and treat corridor shoulders as unknown."""
    labels = np.full(observed.shape, cv2.GC_BGD, np.uint8)
    for y, left, right in axis:
        width = right - left
        pad = max(3, round(width * 0.42))
        labels[y, max(0, left - pad) : right + pad] = cv2.GC_PR_BGD
        labels[y, left:right] = cv2.GC_PR_FGD
        center = (left + right) // 2
        core = max(1, width // 6)
        indexes = np.arange(center - core, center + core + 1)
        strong = observed[y, indexes] & (lab[y, indexes, 1] >= 112)
        if y % 5 == 0:
            labels[y, indexes[strong]] = cv2.GC_FGD
    if np.count_nonzero(labels == cv2.GC_FGD) < 20:
        return observed
    x, y, width, height = cv2.boundingRect((labels != cv2.GC_BGD).astype(np.uint8))
    x0, y0 = max(0, x - 4), max(0, y - 4)
    box = np.s_[y0 : y + height + 4, x0 : x + width + 4]
    sub = labels[box].copy()
    cv2.setRNGSeed(12345)
    cv2.grabCut(np.ascontiguousarray(rgb[box]), sub, None, None, None, 2, cv2.GC_INIT_WITH_MASK)
    result = np.zeros_like(observed)
    result[box] = (sub == cv2.GC_FGD) | (sub == cv2.GC_PR_FGD)
    count, components = cv2.connectedComponents(result.astype(np.uint8), connectivity=8)
    support = np.bincount(components[observed & result], minlength=count)
    areas = np.bincount(components[result], minlength=count)
    return result & ((support >= np.maximum(8, areas * 0.30))[components])


def _trim_branching_axis(axis, lab):
    """Stop ascent at persistent narrow or zigzagging continuation above the bole."""
    chunk = max(10, lab.shape[0] // 26)
    lower = axis[len(axis) // 2 :]
    baseline_width = float(np.median([right - left for _, left, right in lower]))
    last = len(axis)
    while last > max(3 * chunk, len(axis) * 0.57):
        segment = axis[last - chunk : last]
        width = float(np.median([right - left for _, left, right in segment]))
        midpoints = np.array([(left + right) / 2 for _, left, right in segment])
        if width < 0.78 * baseline_width or np.ptp(midpoints) > 0.40 * baseline_width:
            break
        last -= chunk
    return axis[last:] if last < len(axis) - 2 * chunk and last > 0.25 * len(axis) else axis


def _trim_foliage(result: TrunkSegmentation, lab: np.ndarray) -> TrunkSegmentation:
    """Remove isolated green pixels at the top of an otherwise supported trunk."""
    from dataclasses import replace

    mask = result.mask.copy()
    if result.bbox is None:
        return result
    _, y, _, height = result.bbox
    top = np.s_[y : y + height // 3]
    mask[top] &= lab[top][..., 1] >= 119
    return replace(result, mask=mask, bbox=cv2.boundingRect(mask.astype(np.uint8)))
