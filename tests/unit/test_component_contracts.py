from dataclasses import replace

import numpy as np
import pytest

from tree_cbir.component_contracts import (
    ComponentResult,
    Measurement,
    MeasurementQuality,
    assemble_feature_groups,
    run_component,
    validate_bbox,
    validate_image,
    validate_point,
)
from tree_cbir.config import FEATURE_DIMENSION, FEATURE_GROUP_SLICES, FEATURE_IDS, FeatureGroup
from tree_cbir.models import (
    AlgorithmVersion,
    ComponentState,
    SegmentationResult,
    SegmentationStatus,
)


def _component(segmentation, *, values=None, valid=None):
    positions = FEATURE_GROUP_SLICES[segmentation.group]
    return ComponentResult(
        segmentation,
        FEATURE_IDS[positions],
        np.arange(positions.start, positions.stop, dtype=np.float64) if values is None else values,
        np.ones(positions.stop - positions.start, dtype=bool) if valid is None else valid,
    )


def test_canonical_image(synthetic_tree_factory):
    rgb = synthetic_tree_factory().rgb
    validate_image(rgb)
    for wrong in (rgb.swapaxes(0, 1), rgb[:, :, 0], rgb.astype(np.int16)):
        with pytest.raises(ValueError, match="canonical RGB uint8"):
            validate_image(wrong)


def test_mask_dtype_and_shape(synthetic_tree_factory):
    canopy = synthetic_tree_factory().canopy
    mask = canopy.result.masks["canopy"]
    with pytest.raises(ValueError, match="bool"):
        SegmentationResult({"canopy": mask.astype(np.uint8)})
    with pytest.raises(ValueError, match="canonical bool mask"):
        replace(canopy, result=SegmentationResult({"canopy": mask.T}))


def test_point_bbox_and_indexing(synthetic_tree_factory):
    scene = synthetic_tree_factory()
    x, y, w, h = scene.trunk.geometry.bbox.value
    validate_bbox((x, y, w, h))
    validate_bbox((767, 1023, 1, 1))
    validate_point(scene.trunk.geometry.base.value)
    validate_point((5.5, 1023))
    mask = scene.trunk.result.masks["trunk"]
    assert mask[y : y + h, x : x + w].all() and mask.sum() == w * h
    assert not mask[y + h, x] and not mask[y, x + w]
    with pytest.raises(ValueError, match="bbox"):
        validate_bbox((767, 1023, 2, 1))
    with pytest.raises(ValueError, match="bbox"):
        validate_bbox((767, 1023, 0, 1))
    with pytest.raises(ValueError, match="point"):
        validate_point((1023, 767))


def test_geometry_and_status_do_not_infer_reliability(synthetic_tree_factory):
    measured = MeasurementQuality.MEASURED
    with pytest.raises(ValueError, match="quality"):
        Measurement(None, measured)
    with pytest.raises(ValueError, match="confidence"):
        ComponentState(SegmentationStatus.UNAVAILABLE, float("nan"))
    with pytest.raises(ValueError, match="version"):
        ComponentState(SegmentationStatus.RELIABLE)
    uncertain = synthetic_tree_factory(trunk_case="uncertain_base")
    assert uncertain.trunk.geometry.base.value is not None
    assert uncertain.trunk.geometry.base.quality == MeasurementQuality.UNRELIABLE
    assert uncertain.trunk.geometry.width.quality == measured
    assert uncertain.root.geometry.roi_quality == MeasurementQuality.ESTIMATED
    assert uncertain.root.state.status == SegmentationStatus.UNCERTAIN


@pytest.mark.parametrize("trunk_case", ["missing", "unreliable_width"])
def test_missing_or_unreliable_trunk_keeps_downstream_independent(
    synthetic_tree_factory, trunk_case
):
    scene = synthetic_tree_factory(trunk_case=trunk_case)
    root_valid = np.array([False, False, True, False, False, False])
    groups = [_component(scene.canopy), _component(scene.root, valid=root_valid)]
    if scene.trunk is not None:
        groups.append(_component(scene.trunk))
    result = assemble_feature_groups(groups)
    assert result.valid[9:17].all()
    assert not result.valid[22] and result.values[22] == 0
    assert result.diagnostics["root"]["x22_reason"] == "trunk_width_unavailable_or_unreliable"
    if trunk_case == "missing":
        assert result.components[FeatureGroup.TRUNK].status == SegmentationStatus.UNAVAILABLE


def test_empty_foliage_distinguishes_absence_from_unknown(synthetic_tree_factory):
    confirmed = synthetic_tree_factory(foliage_case="leafless").canopy
    unknown = synthetic_tree_factory(foliage_case="unknown").canopy
    values = np.zeros(8)
    present = _component(confirmed, values=values, valid=np.array([True] + [False] * 7))
    missing = _component(unknown, values=values, valid=np.zeros(8, dtype=bool))
    observed = assemble_feature_groups([present])
    indeterminate = assemble_feature_groups([missing])
    assert not confirmed.result.masks["canopy"].any() and not unknown.result.masks["canopy"].any()
    assert observed.components[FeatureGroup.CANOPY].status == SegmentationStatus.CONFIRMED_ABSENT
    assert indeterminate.components[FeatureGroup.CANOPY].status == SegmentationStatus.UNCERTAIN
    assert observed.values[9] == indeterminate.values[9] == 0
    assert observed.valid[9] and not indeterminate.valid[9]


def test_group_contract_rejects_invalid_ids_shapes_and_values(synthetic_tree_factory):
    branch = _component(synthetic_tree_factory().branch)
    for ids in (("X18", "X17", "X19"), ("X17", "X17", "X19"), ("X17", "X18")):
        with pytest.raises(ValueError, match="canonical ordered slice"):
            replace(branch, feature_ids=ids)
    with pytest.raises(ValueError, match="dimensions"):
        replace(branch, values=np.zeros(4))
    with pytest.raises(ValueError, match="dimensions"):
        replace(branch, valid=np.zeros(2, dtype=bool))
    with pytest.raises(ValueError, match="float64 and validity bool"):
        replace(branch, valid=np.zeros(3, dtype=np.uint8))
    with pytest.raises(ValueError, match="finite"):
        replace(branch, values=np.array([np.inf, 0.0, 0.0]))
    with pytest.raises(ValueError, match="duplicate"):
        assemble_feature_groups([branch, branch])


def test_all_groups_assemble_to_canonical_positions(synthetic_tree_factory):
    scene = synthetic_tree_factory()
    components = [scene.context, scene.root, scene.canopy, scene.branch, scene.trunk]
    result = assemble_feature_groups(_component(segmentation) for segmentation in components)
    np.testing.assert_array_equal(result.values, np.arange(FEATURE_DIMENSION))
    assert result.values.dtype == np.float64 and result.valid.dtype == np.bool_
    assert result.valid.shape == (FEATURE_DIMENSION,) and result.valid.all()
    assert result.values[0] == 0 and result.valid[0]
    assert result.components[FeatureGroup.ROOT].version == scene.root.state.version
    assert result.components[FeatureGroup.ROOT].confidence == scene.root.state.confidence
    assert set(result.diagnostics) == set(FeatureGroup)
    assert {"branch", "root", "ground", "background"} <= result.masks.keys()


def test_failure_isolation_and_finite_database_payload(synthetic_tree_factory):
    scene = synthetic_tree_factory()
    version = scene.canopy.state.version

    def failed(_rgb):
        raise RuntimeError("private runtime details")

    canopy = run_component(FeatureGroup.CANOPY, scene.rgb, version, failed)
    branch = _component(
        scene.branch, values=np.array([np.nan, 0.0, np.inf]), valid=np.array([False, True, False])
    )
    result = assemble_feature_groups([canopy, branch])
    assert result.components[FeatureGroup.CANOPY].status == SegmentationStatus.FAILED
    assert result.components[FeatureGroup.CANOPY].version == version
    assert result.diagnostics["canopy"]["reason"] == "RuntimeError"
    assert not result.valid[9:17].any() and result.valid[18]
    assert not result.valid[17] and not result.valid[19] and np.isfinite(result.values).all()
    assert result.values[17] == result.values[18] == result.values[19] == 0


def test_runner_rejects_result_from_wrong_group_or_version(synthetic_tree_factory):
    scene = synthetic_tree_factory()
    version = scene.branch.state.version

    def operation(_rgb):
        return _component(scene.branch)

    with pytest.raises(ValueError, match="unexpected group or algorithm version"):
        run_component(FeatureGroup.CANOPY, scene.rgb, version, operation)
    with pytest.raises(ValueError, match="unexpected group or algorithm version"):
        run_component(
            FeatureGroup.BRANCH, scene.rgb, AlgorithmVersion("other", "1", "1"), operation
        )


def test_context_rejects_known_tree_pixels_without_losing_other_groups(synthetic_tree_factory):
    scene = synthetic_tree_factory()
    masks = dict(scene.context.result.masks)
    masks["background"] = masks["background"] | scene.root.result.masks["root"]
    contaminated = replace(scene.context, result=SegmentationResult(masks))
    result = assemble_feature_groups([_component(scene.root), _component(contaminated)])
    assert result.valid[20] and not result.valid[26:].any()
    assert "background" not in result.masks
    assert result.diagnostics["context"]["reason"] == "context_overlaps_component_mask"
    assert result.components[FeatureGroup.CONTEXT].status == SegmentationStatus.FAILED


def test_context_reports_when_upstream_masks_are_unknown(synthetic_tree_factory):
    scene = synthetic_tree_factory(trunk_case="missing", incomplete_tree=True)
    result = assemble_feature_groups([_component(scene.branch), _component(scene.context)])
    assert result.diagnostics["context"]["contamination_risk"] is True
    assert "trunk" in result.diagnostics["context"]["unresolved_components"]


def test_synthetic_scenes_are_repeatable_and_independent(synthetic_tree_factory):
    first = synthetic_tree_factory()
    second = synthetic_tree_factory()
    np.testing.assert_array_equal(first.rgb, second.rgb)
    np.testing.assert_array_equal(first.tree_mask, second.tree_mask)
    assert first.trunk.geometry == second.trunk.geometry
    complete = first.context.result.masks
    assert not np.any(complete["ground"] & complete["background"])
    assert not np.any((complete["ground"] | complete["background"]) & first.tree_mask)
    assert first.branch.geometry.skeleton.value.any() and first.root.geometry.skeleton.value.any()
    first.rgb[0, 0] = (0, 0, 0)
    first.trunk.result.masks["trunk"][:] = False
    assert second.rgb[0, 0].any() and second.trunk.result.masks["trunk"].any()
