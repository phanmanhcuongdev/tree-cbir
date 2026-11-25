"""Data contracts. RGB arrays are H×W×3 uint8; OpenCV calls explicitly convert RGB↔BGR."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from math import isfinite
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .config import FEATURE_DIMENSION, FeatureGroup

RGBImage = NDArray[np.uint8]
BinaryMask = NDArray[np.bool_]


class SegmentationStatus(StrEnum):
    RELIABLE = "RELIABLE_DETECTION"
    PARTIAL = "PARTIAL_DETECTION"
    UNCERTAIN = "UNCERTAIN_DETECTION"
    CONFIRMED_ABSENT = "CONFIRMED_ABSENT"
    UNAVAILABLE = "UNAVAILABLE"
    FAILED = "FAILED"


@dataclass(frozen=True)
class AlgorithmVersion:
    algorithm: str
    revision: str
    config_version: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.algorithm, self.revision, self.config_version)):
            raise ValueError("algorithm, revision and config version must be nonempty")


@dataclass(frozen=True)
class ComponentState:
    status: SegmentationStatus
    confidence: float | None = None
    version: AlgorithmVersion | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, SegmentationStatus):
            raise ValueError("status must be a SegmentationStatus")
        if self.confidence is not None and not (
            isfinite(self.confidence) and 0 <= self.confidence <= 1
        ):
            raise ValueError("confidence must be finite and in [0, 1]")
        if self.status != SegmentationStatus.UNAVAILABLE and self.version is None:
            raise ValueError("a component that ran requires an algorithm and configuration version")
        if self.status in (SegmentationStatus.UNAVAILABLE, SegmentationStatus.FAILED):
            if self.confidence is not None:
                raise ValueError("an unavailable or failed component has no confidence")


@dataclass(frozen=True)
class ImageMetadata:
    image_id: str
    path: Path
    width: int = 768
    height: int = 1024


@dataclass(frozen=True)
class PreprocessedImage:
    metadata: ImageMetadata
    rgb: RGBImage

    def __post_init__(self) -> None:
        if self.rgb.ndim != 3 or self.rgb.shape[2] != 3 or self.rgb.dtype != np.uint8:
            raise ValueError("rgb must be an H×W×3 uint8 RGB array")


@dataclass(frozen=True)
class SegmentationResult:
    masks: Mapping[str, BinaryMask]
    diagnostics: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name, mask in self.masks.items():
            if mask.ndim != 2 or mask.dtype != np.bool_:
                raise ValueError(f"mask {name!r} must be a 2D bool array")


@dataclass(frozen=True)
class FeatureExtractionResult:
    values: NDArray[np.float64]
    valid: NDArray[np.bool_]
    masks: Mapping[str, BinaryMask] = field(default_factory=dict)
    diagnostics: Mapping[str, Any] = field(default_factory=dict)
    components: Mapping[FeatureGroup, ComponentState] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.values.shape != (FEATURE_DIMENSION,) or self.valid.shape != (FEATURE_DIMENSION,):
            raise ValueError("values and valid must each have dimension 38")
        if self.values.dtype.kind not in "fc" or self.valid.dtype != np.bool_:
            raise ValueError("values must be numeric and valid must be bool")
        if not np.isfinite(self.values[self.valid]).all():
            raise ValueError("valid feature values must be finite")
        SegmentationResult(self.masks)


@dataclass(frozen=True)
class RetrievalResult:
    image_id: str
    distance: float
    rank: int
