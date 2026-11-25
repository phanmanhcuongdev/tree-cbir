"""Measurement provenance for consumers of the trunk segmenter."""

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .trunk import TrunkSegmentation

Quality = Literal["measured", "estimated", "unreliable", "unavailable"]


@dataclass(frozen=True)
class TrunkMeasurements:
    centerline: tuple[tuple[int, int], ...]
    median_width: float | None
    multiple_stem_evidence: bool | None
    expected_region: tuple[int, int, int, int] | None
    quality: dict[str, Quality]


def measurements(result: TrunkSegmentation) -> TrunkMeasurements:
    """Report mask measurements, keeping endpoint and stem uncertainty explicit."""
    mask = result.mask
    rows = np.flatnonzero(mask.any(axis=1))
    reliable = result.diagnostics["status"] == "RELIABLE_DETECTION"
    quality: dict[str, Quality] = {}
    centers = []
    widths = []
    split_rows = 0
    for y in rows[:: max(1, len(rows) // 64)]:
        xs = np.flatnonzero(mask[y])
        centers.append((round(float(np.median(xs))), int(y)))
        widths.append(len(xs))
        segments = np.split(xs, np.flatnonzero(np.diff(xs) > max(2, mask.shape[1] // 100)) + 1)
        split_rows += sum(len(run) >= max(3, len(xs) * 0.2) for run in segments) >= 2
    for key, present in [
        ("base", result.base),
        ("upper", result.upper),
        ("width", widths),
        ("centerline", centers),
        ("color", widths),
    ]:
        quality[key] = (
            "measured" if present and reliable else "unreliable" if present else "unavailable"
        )
    # A clipped endpoint provides no evidence of actual termination.
    if result.base and result.base[1] >= mask.shape[0] - 2:
        quality["base"] = "unreliable"
    if result.upper and result.upper[1] <= 1:
        quality["upper"] = "unreliable"
    region = result.diagnostics.get("coarse_region") or result.diagnostics.get("selected_roi")
    quality["expected_region"] = (
        "unreliable" if region and not reliable else "estimated" if region else "unavailable"
    )
    quality["expected_height"] = "estimated"
    quality["multiple_stem_evidence"] = "unreliable" if centers else "unavailable"
    return TrunkMeasurements(
        tuple(centers),
        float(np.median(widths)) if widths else None,
        split_rows >= max(3, len(centers) * 0.2) if centers else None,
        region,
        quality,
    )
