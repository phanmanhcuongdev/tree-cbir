"""Deterministic contract fixtures. This module has no production callers."""

from collections.abc import Callable
from dataclasses import dataclass, replace

import numpy as np
import pytest

from tree_cbir.component_contracts import (
    BranchGeometry,
    CanopyGeometry,
    ComponentSegmentation,
    Measurement,
    MeasurementQuality,
    RootGeometry,
    TrunkGeometry,
)
from tree_cbir.config import IMAGE_HEIGHT, IMAGE_WIDTH, FeatureGroup
from tree_cbir.models import (
    AlgorithmVersion,
    BinaryMask,
    ComponentState,
    RGBImage,
    SegmentationResult,
    SegmentationStatus,
)

SYNTHETIC_VERSION = AlgorithmVersion("synthetic-contract-fixture", "1", "test-only")


@dataclass(frozen=True)
class SyntheticTree:
    rgb: RGBImage
    trunk: ComponentSegmentation[TrunkGeometry] | None
    canopy: ComponentSegmentation[CanopyGeometry]
    branch: ComponentSegmentation[BranchGeometry]
    root: ComponentSegmentation[RootGeometry]
    context: ComponentSegmentation[None]
    tree_mask: BinaryMask


def _empty_mask() -> BinaryMask:
    return np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH), dtype=bool)


def _scene(
    *,
    trunk_case: str = "complete",
    foliage_case: str = "leafy",
    incomplete_tree: bool = False,
) -> SyntheticTree:
    measured = MeasurementQuality.MEASURED
    unreliable = MeasurementQuality.UNRELIABLE
    reliable = ComponentState(SegmentationStatus.RELIABLE, 0.8, SYNTHETIC_VERSION)

    trunk_mask = _empty_mask()
    trunk_mask[450:820, 372:396] = True
    trunk_geometry = TrunkGeometry(
        bbox=Measurement((372, 450, 24, 370), measured),
        base=Measurement((384, 819), measured),
        upper=Measurement((384, 450), measured),
        width=Measurement(23.0, measured),
        observed_height=Measurement(370.0, measured),
        expected_height=Measurement(400.0, MeasurementQuality.ESTIMATED),
        centerline=Measurement(((384, 450), (384, 819)), measured),
    )
    trunk_state = reliable
    match trunk_case:
        case "uncertain_base":
            trunk_geometry = replace(trunk_geometry, base=Measurement((384, 819), unreliable))
            trunk_state = replace(reliable, status=SegmentationStatus.PARTIAL)
        case "unreliable_width":
            trunk_geometry = replace(trunk_geometry, width=Measurement(23.0, unreliable))
            trunk_state = replace(reliable, status=SegmentationStatus.PARTIAL)
        case "complete" | "missing":
            pass
        case _:
            raise ValueError(f"unknown trunk fixture {trunk_case}")
    trunk = (
        None
        if trunk_case == "missing"
        else ComponentSegmentation(
            FeatureGroup.TRUNK,
            trunk_state,
            SegmentationResult({"trunk": trunk_mask}),
            trunk_geometry,
        )
    )

    canopy_roi = _empty_mask()
    canopy_roi[100:600, 180:590] = True
    foliage = _empty_mask()
    canopy_bbox = Measurement()
    match foliage_case:
        case "leafy":
            foliage[160:430, 220:550] = True
            canopy_bbox = Measurement((220, 160, 330, 270), measured)
            canopy_state = reliable
        case "leafless":
            canopy_state = replace(reliable, status=SegmentationStatus.CONFIRMED_ABSENT)
        case "unknown":
            canopy_state = replace(reliable, status=SegmentationStatus.UNCERTAIN)
        case _:
            raise ValueError(f"unknown foliage fixture {foliage_case}")
    canopy = ComponentSegmentation(
        FeatureGroup.CANOPY,
        canopy_state,
        SegmentationResult({"canopy_roi": canopy_roi, "canopy": foliage}),
        CanopyGeometry(measured, canopy_bbox),
    )

    branch_skeleton = _empty_mask()
    branch_skeleton[425:470, 384] = True
    branch_skeleton[440, 350:420] = True
    branch = ComponentSegmentation(
        FeatureGroup.BRANCH,
        reliable,
        SegmentationResult({"branch": branch_skeleton.copy()}),
        BranchGeometry(Measurement(branch_skeleton, measured)),
    )

    root_roi = _empty_mask()
    root_roi[800:905, 280:490] = True
    roots = _empty_mask()
    roots[818:823, 325:440] = True
    root_skeleton = _empty_mask()
    root_skeleton[820, 325:440] = True
    root_is_uncertain = trunk_case != "complete"
    root_state = (
        replace(reliable, status=SegmentationStatus.UNCERTAIN) if root_is_uncertain else reliable
    )
    root_quality = unreliable if root_is_uncertain else measured
    root = ComponentSegmentation(
        FeatureGroup.ROOT,
        root_state,
        SegmentationResult({"root_roi": root_roi, "root": roots}),
        RootGeometry(
            MeasurementQuality.ESTIMATED if root_is_uncertain else measured,
            Measurement((325, 818, 115, 5), root_quality),
            Measurement(root_skeleton, root_quality),
        ),
    )

    rgb = np.empty((IMAGE_HEIGHT, IMAGE_WIDTH, 3), dtype=np.uint8)
    rgb[:] = (140, 190, 220)
    rgb[805:] = (110, 90, 65)
    rgb[foliage] = (35, 130, 55)
    rgb[trunk_mask | branch_skeleton | roots] = (90, 55, 30)
    tree_mask = trunk_mask | foliage | branch_skeleton | roots
    known_mask = foliage | branch_skeleton | roots
    if trunk is not None and not incomplete_tree:
        known_mask |= trunk_mask
    lower_roi = _empty_mask()
    lower_roi[805:] = True
    ground = lower_roi & ~known_mask
    background = ~(lower_roi | known_mask)
    context = ComponentSegmentation(
        FeatureGroup.CONTEXT,
        reliable,
        SegmentationResult(
            {"lower_roi": lower_roi, "ground": ground, "background": background},
            {"contamination_risk": incomplete_tree or trunk is None},
        ),
    )
    return SyntheticTree(rgb, trunk, canopy, branch, root, context, tree_mask)


@pytest.fixture
def synthetic_tree_factory() -> Callable[..., SyntheticTree]:
    """Provide fresh arrays with configurable observation and upstream failures."""
    return _scene
