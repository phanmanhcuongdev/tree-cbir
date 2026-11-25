"""Research variants combining the frozen hybrid with a ground-anchored proposal."""

import cv2
import numpy as np

from .trunk import TrunkSegmentation
from .trunk_ground import ground_proposal


def refine(rgb: np.ndarray, prior: TrunkSegmentation, version: int) -> TrunkSegmentation:
    h, w = rgb.shape[:2]
    if prior.diagnostics["status"] == "RELIABLE_DETECTION" and version < 5:
        return prior
    proposal = ground_proposal(rgb, version)
    box = proposal.region
    if version >= 5:
        from .trunk_profile import bole_profile
        from .trunk_termination import trim_at_crown

        if (
            prior.base
            and prior.bbox
            and prior.bbox[3] < 0.16 * h
            and abs(prior.base[0] - w / 2) < 0.12 * w
        ):
            mask = prior.mask
        elif prior.base and prior.base[1] >= 0.83 * h and abs(prior.base[0] - w / 2) < 0.13 * w:
            mask = prior.mask
        else:
            mask, _ = bole_profile(rgb, 4)
        if version >= 7:
            from .trunk_corridor import open_background, recover_corridor

            sky = open_background(rgb, mask)
            trimmed = trim_at_crown(rgb, mask, branches=sky)
            if trimmed.sum() > 0.28 * mask.sum() or (sky and version < 9):
                mask = trimmed
            if prior.diagnostics.get("backend") == "bands_grabcut" and np.any(mask & prior.mask):
                mask = recover_corridor(rgb, mask, prior.diagnostics.get("axis", ()), version >= 8)
            if version >= 9 and prior.bbox and prior.diagnostics.get("axis"):
                if mask.sum() < 0.66 * prior.mask.sum() and not sky:
                    mask = prior.mask.copy()
                if prior.bbox[3] > 0.25 * h and np.array_equal(trimmed, prior.mask):
                    mask = prior.mask.copy()
                    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
                    for yy, left_edge, r in prior.diagnostics["axis"]:
                        pix = lab[yy, left_edge:r]
                        if pix.size:
                            mask[yy, left_edge:r] |= (
                                np.linalg.norm(pix - np.median(pix, axis=0), axis=1) < 26
                            ) & (pix[:, 1] > 112)
            if version == 8:
                profile, _ = bole_profile(rgb, 4)
                if profile.any() and mask.any():
                    shared = np.count_nonzero(profile & mask)
                    if shared > 0.57 * profile.sum() and profile.sum() < 0.75 * mask.sum():
                        ymin = np.where(profile)[0].min()
                        mask[:ymin] = False
        else:
            mask = trim_at_crown(rgb, mask, branches=version >= 6)
        if version == 10:
            from .trunk_components import lower_component

            alternative, strength = lower_component(rgb)
            if (
                prior.bbox
                and prior.bbox[3] > 0.4 * h
                and mask.sum() < 0.82 * prior.mask.sum()
                and not np.any(trimmed != prior.mask)
            ):
                mask = mask | prior.mask
            if prior.mask.any() and not np.any(trimmed):
                mask = prior.mask.copy()
            if strength > 0.58 and alternative.any():
                common = np.count_nonzero(alternative & mask)
                y0 = np.where(alternative)[0].min()
                anchor = np.where(alternative)[0].max()
                if common < 0.16 * alternative.sum() or (
                    prior.base and prior.base[1] < anchor - 0.13 * h
                ):
                    mask = alternative
                elif (
                    common > 0.53 * alternative.sum()
                    and alternative.sum() < 0.78 * mask.sum()
                    and y0 > 0.55 * h
                ):
                    mask = mask.copy()
                    mask[:y0] = False
            if (
                open_background(rgb, prior.mask)
                and prior.mask.any()
                and trimmed.sum() < 0.27 * prior.mask.sum()
            ):
                mask = prior.mask.copy()
        if np.array_equal(mask, prior.mask):
            return prior
    elif version < 3:
        if prior.base and prior.base[1] >= 0.84 * h and abs(prior.base[0] - w / 2) < 0.13 * w:
            return prior
        mask = proposal.mask
    else:
        from .trunk_profile import bole_profile

        if (
            prior.base
            and prior.bbox
            and prior.bbox[3] < 0.15 * h
            and abs(prior.base[0] - w / 2) < 0.12 * w
        ):
            return prior
        mask, support = bole_profile(rgb, version)
        if (
            version == 3
            and prior.base
            and prior.base[1] >= 0.84 * h
            and abs(prior.base[0] - w / 2) < 0.13 * w
        ):
            return prior
        if (
            version >= 4
            and prior.bbox
            and prior.bbox[3] > 0.42 * h
            and mask.sum() < 0.6 * prior.mask.sum()
        ):
            return prior
    if not mask.any():
        return prior
    x, y, width, height = cv2.boundingRect(mask.astype(np.uint8))
    base_y = y + height - 1
    base = (int(np.median(np.where(mask[base_y])[0])), base_y)
    upper = (int(np.median(np.where(mask[y])[0])), y)
    diag = dict(
        status="UNCERTAIN_DETECTION",
        backend="ground",
        selected_roi=box,
        reason="independent boundary confirmation unavailable",
        expected_height_confidence=0.0,
        ground_support=proposal.support,
        strong_green_fraction=proposal.foliage,
    )
    confidence = min(0.49, proposal.support)
    if version >= 9:
        overlap = (mask & proposal.mask).sum() / max(1, (mask | proposal.mask).sum())
        agreement = (mask & prior.mask).sum() / max(1, (mask | prior.mask).sum())
        diag.update(ground_agreement=float(overlap), prior_agreement=float(agreement))
        if overlap > 0.58 and agreement > 0.55 and proposal.support > 0.5 and base_y < h - 2:
            diag.update(status="RELIABLE_DETECTION", reason=None)
            confidence = float((overlap + agreement) / 2)
    return TrunkSegmentation(mask, (x, y, width, height), base, upper, 0.6 * h, confidence, diag)
