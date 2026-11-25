"""Superpixel label assignment, oracle mask construction, and image-aware weighting."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from numpy.typing import NDArray

from tree_cbir.models import BinaryMask

from .superpixels import SuperpixelMap, boundary_mask

LABEL_NON_TRUNK = 0
LABEL_TRUNK = 1
LABEL_AMBIGUOUS = -1


@dataclass(frozen=True)
class LabelPolicy:
    """Overlap thresholds for mapping region overlap to supervised labels."""

    positive_threshold: float = 0.80
    negative_threshold: float = 0.20
    oracle_threshold: float = 0.50

    def __post_init__(self) -> None:
        if not (0.0 <= self.negative_threshold < self.positive_threshold <= 1.0):
            raise ValueError("require 0 <= negative_threshold < positive_threshold <= 1")
        if not (0.0 < self.oracle_threshold <= 1.0):
            raise ValueError("oracle_threshold must lie in (0, 1]")


@dataclass(frozen=True)
class MaskMetrics:
    """Pixel-level segmentation agreement metrics against a reference mask."""

    iou: float
    dice: float
    precision: float
    recall: float


@dataclass(frozen=True)
class SuperpixelLabels:
    """Supervised labels, oracle masks, and superpixel quality metrics for one image."""

    region_ids: NDArray[np.int32]
    overlaps: NDArray[np.float64]
    labels: NDArray[np.int8]
    n_positive: int
    n_negative: int
    n_ambiguous: int
    oracle_mask: BinaryMask
    strict_positive_mask: BinaryMask
    oracle_metrics: MaskMetrics
    strict_positive_metrics: MaskMetrics
    boundary_recall: float
    undersegmentation_error: float
    image_uniform_weights: NDArray[np.float64]


def compute_mask_metrics(prediction: BinaryMask, reference: BinaryMask) -> MaskMetrics:
    """Compute IoU, Dice, precision, and recall between boolean masks."""
    if prediction.shape != reference.shape or prediction.dtype != np.bool_:
        raise ValueError("prediction and reference must be boolean masks of matching shape")
    pred_area = int(prediction.sum())
    ref_area = int(reference.sum())
    intersection = int(np.count_nonzero(prediction & reference))
    union = pred_area + ref_area - intersection
    return MaskMetrics(
        iou=float(intersection / union) if union > 0 else 1.0,
        dice=float(2 * intersection / (pred_area + ref_area))
        if (pred_area + ref_area) > 0
        else 1.0,
        precision=float(intersection / pred_area) if pred_area > 0 else 0.0,
        recall=float(intersection / ref_area) if ref_area > 0 else 0.0,
    )


def compute_boundary_metrics(
    superpixels: SuperpixelMap,
    reference: BinaryMask,
    *,
    tolerance_px: int = 2,
) -> tuple[float, float]:
    """Compute superpixel Boundary Recall (BR) and Undersegmentation Error (UE)."""
    ref_u8 = reference.astype(np.uint8)
    eroded = cv2.erode(ref_u8, np.ones((3, 3), dtype=np.uint8)) > 0
    ref_border = reference & ~eroded
    if not ref_border.any():
        return 0.0, 0.0
    sp_border = boundary_mask(superpixels.labels)
    k = 2 * tolerance_px + 1
    dilated_sp = cv2.dilate(sp_border.astype(np.uint8), np.ones((k, k), dtype=np.uint8)) > 0
    n_ref_border = int(np.count_nonzero(ref_border))
    boundary_recall = float(np.count_nonzero(ref_border & dilated_sp) / n_ref_border)

    flat_labels = superpixels.labels.ravel()
    areas = superpixels.region_areas
    hits = np.bincount(
        flat_labels,
        weights=reference.ravel().astype(np.float64),
        minlength=superpixels.n_regions,
    )
    overlapping = hits > 0
    leak_sum = float(np.minimum(hits[overlapping], areas[overlapping] - hits[overlapping]).sum())
    ref_area = max(1, int(reference.sum()))
    ue = leak_sum / float(ref_area)
    return boundary_recall, ue


def label_superpixels(
    superpixels: SuperpixelMap,
    reference: BinaryMask,
    policy: LabelPolicy = LabelPolicy(),
) -> SuperpixelLabels:
    """Assign TRUNK / NON_TRUNK / AMBIGUOUS labels and compute oracle metrics."""
    if reference.ndim != 2 or reference.dtype != np.bool_:
        raise ValueError("reference must be a 2D bool mask")
    if superpixels.labels.shape != reference.shape:
        raise ValueError("superpixels and reference mask shapes must match")

    flat_labels = superpixels.labels.ravel()
    areas = superpixels.region_areas.astype(np.float64)
    hits = np.bincount(
        flat_labels,
        weights=reference.ravel().astype(np.float64),
        minlength=superpixels.n_regions,
    )
    overlaps = np.clip(hits / areas, 0.0, 1.0)

    labels = np.full(superpixels.n_regions, LABEL_AMBIGUOUS, dtype=np.int8)
    labels[overlaps >= policy.positive_threshold] = LABEL_TRUNK
    labels[overlaps <= policy.negative_threshold] = LABEL_NON_TRUNK

    oracle_selected = overlaps >= policy.oracle_threshold
    strict_selected = labels == LABEL_TRUNK
    oracle_mask = oracle_selected[superpixels.labels]
    strict_mask = strict_selected[superpixels.labels]

    oracle_metrics = compute_mask_metrics(oracle_mask, reference)
    strict_metrics = compute_mask_metrics(strict_mask, reference)
    br, ue = compute_boundary_metrics(superpixels, reference)

    usable = labels != LABEL_AMBIGUOUS
    n_usable = int(np.count_nonzero(usable))
    weights = np.zeros(superpixels.n_regions, dtype=np.float64)
    if n_usable > 0:
        weights[usable] = 1.0 / float(n_usable)

    return SuperpixelLabels(
        region_ids=superpixels.region_ids,
        overlaps=overlaps,
        labels=labels,
        n_positive=int(np.count_nonzero(labels == LABEL_TRUNK)),
        n_negative=int(np.count_nonzero(labels == LABEL_NON_TRUNK)),
        n_ambiguous=int(np.count_nonzero(labels == LABEL_AMBIGUOUS)),
        oracle_mask=oracle_mask,
        strict_positive_mask=strict_mask,
        oracle_metrics=oracle_metrics,
        strict_positive_metrics=strict_metrics,
        boundary_recall=br,
        undersegmentation_error=ue,
        image_uniform_weights=weights,
    )
