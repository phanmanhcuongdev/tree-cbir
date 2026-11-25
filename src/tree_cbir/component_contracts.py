"""Boundaries for independent components on the standardized image grid."""

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from math import isfinite
from numbers import Integral

import numpy as np
from numpy.typing import NDArray

from .config import (
    FEATURE_DIMENSION,
    FEATURE_GROUP_SLICES,
    FEATURE_IDS,
    IMAGE_HEIGHT,
    IMAGE_WIDTH,
    FeatureGroup,
)
from .models import (
    AlgorithmVersion,
    BinaryMask,
    ComponentState,
    FeatureExtractionResult,
    RGBImage,
    SegmentationResult,
    SegmentationStatus,
)

type Point = tuple[float, float]
type BoundingBox = tuple[int, int, int, int]

_MASK_KEYS = {
    FeatureGroup.TRUNK: {"trunk"},
    FeatureGroup.CANOPY: {"canopy", "canopy_roi"},
    FeatureGroup.BRANCH: {"branch"},
    FeatureGroup.ROOT: {"root", "root_roi"},
    FeatureGroup.CONTEXT: {"ground", "background", "lower_roi"},
}
_NO_OBSERVATION = (SegmentationStatus.UNAVAILABLE, SegmentationStatus.FAILED)
_KNOWN_OBSERVATION = (SegmentationStatus.RELIABLE, SegmentationStatus.CONFIRMED_ABSENT)


def validate_image(rgb: RGBImage) -> None:
    if not (
        isinstance(rgb, np.ndarray)
        and rgb.shape == (IMAGE_HEIGHT, IMAGE_WIDTH, 3)
        and rgb.dtype == np.uint8
    ):
        raise ValueError("expected canonical RGB uint8 image (1024, 768, 3)")


def validate_mask(mask: BinaryMask) -> None:
    if not (
        isinstance(mask, np.ndarray)
        and mask.shape == (IMAGE_HEIGHT, IMAGE_WIDTH)
        and mask.dtype == np.bool_
    ):
        raise ValueError("expected canonical bool mask (1024, 768)")


def validate_point(point: Point) -> None:
    x, y = point
    if not (0 <= x <= IMAGE_WIDTH - 1 and 0 <= y <= IMAGE_HEIGHT - 1):
        raise ValueError("point (x, y) must be on the canonical image grid")


def validate_bbox(box: BoundingBox) -> None:
    x, y, width, height = box
    if not (
        all(isinstance(value, Integral) and not isinstance(value, bool) for value in box)
        and 0 <= x < x + width <= IMAGE_WIDTH
        and 0 <= y < y + height <= IMAGE_HEIGHT
    ):
        raise ValueError("bbox (x, y, width, height) must be a nonempty in-bounds rectangle")


class MeasurementQuality(StrEnum):
    MEASURED = "measured"
    ESTIMATED = "estimated"
    UNRELIABLE = "unreliable"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class Measurement[T]:
    value: T | None = None
    quality: MeasurementQuality = MeasurementQuality.UNAVAILABLE

    def __post_init__(self) -> None:
        if not isinstance(self.quality, MeasurementQuality):
            raise ValueError("quality must be a MeasurementQuality")
        if (self.value is None) != (self.quality == MeasurementQuality.UNAVAILABLE):
            raise ValueError("measurement value is absent exactly when quality is unavailable")


@dataclass(frozen=True)
class TrunkGeometry:
    bbox: Measurement[BoundingBox] = Measurement()
    base: Measurement[Point] = Measurement()
    upper: Measurement[Point] = Measurement()
    width: Measurement[float] = Measurement()
    observed_height: Measurement[float] = Measurement()
    expected_height: Measurement[float] = Measurement()
    centerline: Measurement[tuple[Point, ...]] = Measurement()
    bark_color: Measurement[tuple[float, float, float]] = Measurement()

    def __post_init__(self) -> None:
        if self.bbox.value is not None:
            validate_bbox(self.bbox.value)
        for point in (self.base.value, self.upper.value, *(self.centerline.value or ())):
            if point is not None:
                validate_point(point)
        for measure, upper in ((self.width, IMAGE_WIDTH - 1), (self.observed_height, IMAGE_HEIGHT)):
            if measure.value is not None and not 0 <= measure.value <= upper:
                raise ValueError("trunk width or observed height is outside the image grid")
        height = self.expected_height.value
        if height is not None and not (isfinite(height) and height > 0):
            raise ValueError("expected trunk height must be positive and finite")
        if self.bark_color.value is not None and not np.isfinite(self.bark_color.value).all():
            raise ValueError("bark color measurements must be finite")


@dataclass(frozen=True)
class CanopyGeometry:
    roi_quality: MeasurementQuality = MeasurementQuality.UNAVAILABLE
    bbox: Measurement[BoundingBox] = Measurement()

    def __post_init__(self) -> None:
        if self.bbox.value is not None:
            validate_bbox(self.bbox.value)


@dataclass(frozen=True)
class BranchGeometry:
    skeleton: Measurement[BinaryMask] = Measurement()

    def __post_init__(self) -> None:
        if self.skeleton.value is not None:
            validate_mask(self.skeleton.value)


@dataclass(frozen=True)
class RootGeometry:
    roi_quality: MeasurementQuality = MeasurementQuality.UNAVAILABLE
    bbox: Measurement[BoundingBox] = Measurement()
    skeleton: Measurement[BinaryMask] = Measurement()

    def __post_init__(self) -> None:
        if self.bbox.value is not None:
            validate_bbox(self.bbox.value)
        if self.skeleton.value is not None:
            validate_mask(self.skeleton.value)


_GEOMETRY_TYPES = {
    FeatureGroup.TRUNK: TrunkGeometry,
    FeatureGroup.CANOPY: CanopyGeometry,
    FeatureGroup.BRANCH: BranchGeometry,
    FeatureGroup.ROOT: RootGeometry,
    FeatureGroup.CONTEXT: type(None),
}


def _validate_subset(mask: BinaryMask | None, roi: BinaryMask | None) -> None:
    if mask is not None and roi is not None and np.any(mask & ~roi):
        raise ValueError("component mask must be contained in its ROI")


@dataclass(frozen=True)
class ComponentSegmentation[T]:
    group: FeatureGroup
    state: ComponentState
    result: SegmentationResult = field(default_factory=lambda: SegmentationResult({}))
    geometry: T | None = None

    def __post_init__(self) -> None:
        masks = self.result.masks
        if self.geometry is not None and not isinstance(self.geometry, _GEOMETRY_TYPES[self.group]):
            raise ValueError(f"unexpected geometry type for {self.group}")
        if masks.keys() - _MASK_KEYS[self.group]:
            raise ValueError(f"unexpected mask key for {self.group}")
        for mask in masks.values():
            validate_mask(mask)
        if self.state.status in _NO_OBSERVATION and (masks or self.geometry is not None):
            raise ValueError("unavailable or failed segmentation cannot provide masks or geometry")
        if self.state.status == SegmentationStatus.CONFIRMED_ABSENT:
            observed = masks.get(self.group.value)
            if observed is None or observed.any():
                raise ValueError("confirmed absence requires an explicit empty component mask")
        if self.state.status == SegmentationStatus.RELIABLE:
            observed_keys = (
                ("ground", "background")
                if self.group == FeatureGroup.CONTEXT
                else (self.group.value,)
            )
            if not any(key in masks and masks[key].any() for key in observed_keys):
                raise ValueError("reliable detection requires a nonempty component mask")
        if self.group in (FeatureGroup.CANOPY, FeatureGroup.ROOT):
            _validate_subset(masks.get(self.group.value), masks.get(f"{self.group.value}_roi"))
        _validate_subset(masks.get("ground"), masks.get("lower_roi"))
        if (
            "ground" in masks
            and "background" in masks
            and np.any(masks["ground"] & masks["background"])
        ):
            raise ValueError("ground and background masks must be disjoint")


@dataclass(frozen=True)
class ComponentResult[T]:
    segmentation: ComponentSegmentation[T]
    feature_ids: tuple[str, ...]
    values: NDArray[np.float64]
    valid: NDArray[np.bool_]
    diagnostics: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        expected = FEATURE_IDS[FEATURE_GROUP_SLICES[self.segmentation.group]]
        if self.feature_ids != expected:
            raise ValueError("feature IDs must match the component's canonical ordered slice")
        if self.values.shape != (len(expected),) or self.valid.shape != (len(expected),):
            raise ValueError("values and validity must match component feature dimensions")
        if self.values.dtype != np.float64 or self.valid.dtype != np.bool_:
            raise ValueError("component values must be float64 and validity bool")
        if not np.isfinite(self.values[self.valid]).all():
            raise ValueError("valid feature values must be finite")
        if self.segmentation.state.status in _NO_OBSERVATION and self.valid.any():
            raise ValueError("a failed or unavailable component cannot provide valid features")


def _without_observation[T](
    group: FeatureGroup, state: ComponentState, reason: str
) -> ComponentResult[T]:
    ids = FEATURE_IDS[FEATURE_GROUP_SLICES[group]]
    return ComponentResult(
        ComponentSegmentation(group, state, SegmentationResult({}, {"reason": reason})),
        ids,
        np.zeros(len(ids)),
        np.zeros(len(ids), dtype=bool),
    )


def run_component[T](
    group: FeatureGroup,
    rgb: RGBImage,
    version: AlgorithmVersion,
    operation: Callable[[RGBImage], ComponentResult[T]],
) -> ComponentResult[T]:
    """Run an explicitly supplied operation and isolate errors raised by that operation."""
    validate_image(rgb)
    try:
        result = operation(rgb)
    except Exception as error:
        return _without_observation(
            group, ComponentState(SegmentationStatus.FAILED, version=version), type(error).__name__
        )
    if result.segmentation.group != group or result.segmentation.state.version != version:
        raise ValueError("component returned an unexpected group or algorithm version")
    return result


def assemble_feature_groups(results: Iterable[ComponentResult[object]]) -> FeatureExtractionResult:
    """Assemble canonical slices regardless of execution order. Missing groups stay invalid."""
    by_group = {}
    for result in results:
        group = result.segmentation.group
        if group in by_group:
            raise ValueError(f"duplicate result for {group}")
        by_group[group] = result

    values = np.zeros(FEATURE_DIMENSION)
    valid = np.zeros(FEATURE_DIMENSION, dtype=bool)
    masks = {}
    diagnostics = {}
    components = {}
    for group, positions in FEATURE_GROUP_SLICES.items():
        result = by_group.get(group)
        if result is None:
            components[group] = ComponentState(SegmentationStatus.UNAVAILABLE)
            diagnostics[group] = {"reason": "component_not_supplied"}
            continue
        segmentation = result.segmentation
        components[group] = segmentation.state
        diagnostics[group] = {
            **segmentation.result.diagnostics,
            "features": dict(result.diagnostics),
        }
        masks.update(segmentation.result.masks)
        values[positions] = np.where(result.valid, result.values, 0.0)
        valid[positions] = result.valid

    if valid[22]:
        trunk = by_group.get(FeatureGroup.TRUNK)
        geometry = trunk.segmentation.geometry if trunk is not None else None
        if not (
            isinstance(geometry, TrunkGeometry)
            and geometry.width.quality == MeasurementQuality.MEASURED
            and geometry.width.value is not None
            and geometry.width.value > 0
        ):
            valid[22] = False
            values[22] = 0.0
            diagnostics[FeatureGroup.ROOT]["x22_reason"] = "trunk_width_unavailable_or_unreliable"

    if FeatureGroup.CONTEXT in by_group:
        unresolved = tuple(
            group.value
            for group in FeatureGroup
            if group != FeatureGroup.CONTEXT and components[group].status not in _KNOWN_OBSERVATION
        )
        if unresolved:
            diagnostics[FeatureGroup.CONTEXT]["contamination_risk"] = True
            diagnostics[FeatureGroup.CONTEXT]["unresolved_components"] = unresolved

        context_masks = [masks[key] for key in ("ground", "background") if key in masks]
        known_tree_masks = [masks[group.value] for group in FeatureGroup if group.value in masks]
        if any(np.any(region & tree) for region in context_masks for tree in known_tree_masks):
            state = components[FeatureGroup.CONTEXT]
            components[FeatureGroup.CONTEXT] = ComponentState(
                SegmentationStatus.FAILED, version=state.version
            )
            diagnostics[FeatureGroup.CONTEXT]["contamination_risk"] = True
            diagnostics[FeatureGroup.CONTEXT]["reason"] = "context_overlaps_component_mask"
            for key in _MASK_KEYS[FeatureGroup.CONTEXT]:
                masks.pop(key, None)
            positions = FEATURE_GROUP_SLICES[FeatureGroup.CONTEXT]
            values[positions] = 0.0
            valid[positions] = False

    return FeatureExtractionResult(values, valid, masks, diagnostics, components)
