"""Deterministic SLIC superpixel generation and boundary visualization."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter

import numpy as np
from numpy.typing import NDArray
from skimage.segmentation import slic

from tree_cbir.models import RGBImage


@dataclass(frozen=True)
class SlicConfig:
    """Configuration for deterministic SLIC superpixel oversegmentation."""

    name: str
    n_segments: int
    compactness: float = 15.0
    sigma: float = 1.0
    min_size_factor: float = 0.5
    max_size_factor: float = 3.0

    def __post_init__(self) -> None:
        if self.n_segments <= 0:
            raise ValueError("n_segments must be positive")
        if self.compactness <= 0:
            raise ValueError("compactness must be positive")
        if self.sigma < 0:
            raise ValueError("sigma must be non-negative")


@dataclass(frozen=True)
class SuperpixelMap:
    """Contiguous 0..n_regions-1 SLIC superpixel partition for an RGB image."""

    labels: NDArray[np.int32]
    n_regions: int
    region_ids: NDArray[np.int32]
    region_areas: NDArray[np.int64]
    duration_seconds: float
    config: SlicConfig

    def __post_init__(self) -> None:
        if self.labels.ndim != 2 or not np.issubdtype(self.labels.dtype, np.integer):
            raise ValueError("labels must be a 2D integer array")
        if self.n_regions <= 0:
            raise ValueError("n_regions must be positive")
        if self.region_ids.shape != (self.n_regions,) or self.region_areas.shape != (
            self.n_regions,
        ):
            raise ValueError("region_ids and region_areas must have length n_regions")
        if not np.array_equal(self.region_ids, np.arange(self.n_regions, dtype=np.int32)):
            raise ValueError("region_ids must be contiguous 0..n_regions-1")
        if np.any(self.region_areas <= 0):
            raise ValueError("every superpixel region must have positive pixel area")


def generate_superpixels(rgb: RGBImage, config: SlicConfig) -> SuperpixelMap:
    """Generate deterministic SLIC superpixels on a non-empty RGB uint8 image."""
    if rgb.ndim != 3 or rgb.shape[2] != 3 or rgb.dtype != np.uint8 or not rgb.size:
        raise ValueError("expected a nonempty RGB uint8 image")
    started = perf_counter()
    raw = slic(
        np.ascontiguousarray(rgb),
        n_segments=config.n_segments,
        compactness=config.compactness,
        sigma=config.sigma,
        min_size_factor=config.min_size_factor,
        max_size_factor=config.max_size_factor,
        start_label=0,
        convert2lab=True,
        enforce_connectivity=True,
        channel_axis=-1,
    )
    duration = perf_counter() - started
    labels = raw.astype(np.int32, copy=False)
    unique = np.unique(labels)
    if unique[0] != 0 or unique.size != int(unique[-1]) + 1:
        _, inverse = np.unique(labels, return_inverse=True)
        labels = inverse.reshape(labels.shape).astype(np.int32)
        n_regions = int(unique.size)
    else:
        n_regions = int(unique.size)
    region_ids = np.arange(n_regions, dtype=np.int32)
    region_areas = np.bincount(labels.ravel(), minlength=n_regions).astype(np.int64)
    return SuperpixelMap(
        labels=labels,
        n_regions=n_regions,
        region_ids=region_ids,
        region_areas=region_areas,
        duration_seconds=duration,
        config=config,
    )


def boundary_mask(labels: NDArray[np.int32]) -> NDArray[np.bool_]:
    """Return a boolean mask of superpixel boundary pixels (4-neighborhood)."""
    if labels.ndim != 2 or not labels.size:
        raise ValueError("labels must be a nonempty 2D array")
    edges = np.zeros(labels.shape, dtype=bool)
    if labels.shape[0] > 1:
        diff_v = labels[:-1, :] != labels[1:, :]
        edges[:-1, :] |= diff_v
        edges[1:, :] |= diff_v
    if labels.shape[1] > 1:
        diff_h = labels[:, :-1] != labels[:, 1:]
        edges[:, :-1] |= diff_h
        edges[:, 1:] |= diff_h
    return edges


def draw_superpixel_boundaries(
    rgb: RGBImage,
    labels: NDArray[np.int32],
    *,
    color: tuple[int, int, int] = (255, 220, 0),
) -> RGBImage:
    """Render superpixel boundaries onto an RGB copy without mutating the input."""
    output = rgb.copy()
    edges = boundary_mask(labels)
    output[edges] = color
    return output
