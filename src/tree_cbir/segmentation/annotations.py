"""Annotation loading, schema validation, and deterministic polygon rasterization."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cv2
import numpy as np

from tree_cbir.config import IMAGE_HEIGHT, IMAGE_WIDTH
from tree_cbir.models import BinaryMask

StripRow = tuple[int, int, int]
Strip = tuple[StripRow, ...]
QualityStatus = Literal["ACCEPTED", "CORRECTED", "UNUSABLE"]


@dataclass(frozen=True)
class TrunkAnnotation:
    """Validated trunk strip-polygon annotation for one standardized image."""

    filename: str
    source_group: str
    quality_status: QualityStatus
    coordinate_width: int
    coordinate_height: int
    strips: tuple[Strip, ...]
    traits: tuple[str, ...] = ()
    notes: str = ""
    original_source: str = ""


def validate_strips(
    strips: Sequence[Sequence[Sequence[int]]],
    *,
    coord_width: int,
    coord_height: int,
) -> tuple[Strip, ...]:
    """Validate strip-polygon bounds and row ordering, returning canonical tuples."""
    if coord_width <= 0 or coord_height <= 0:
        raise ValueError("coordinate dimensions must be positive")
    if not strips:
        raise ValueError("annotation must contain at least one strip")
    normalized: list[Strip] = []
    for strip_index, rows in enumerate(strips):
        if len(rows) < 2:
            raise ValueError(f"strip {strip_index} must have at least 2 rows")
        parsed_rows: list[StripRow] = []
        prev_y = -1
        for row in rows:
            if len(row) != 3:
                raise ValueError(f"strip row must have 3 elements [y, left, right], got {row!r}")
            y, left, right = int(row[0]), int(row[1]), int(row[2])
            if not (0 <= y < coord_height):
                raise ValueError(f"y coordinate {y} out of bounds [0, {coord_height})")
            if not (0 <= left < right <= coord_width):
                raise ValueError(f"invalid horizontal bounds ({left}, {right}) for w={coord_width}")
            if y < prev_y:
                raise ValueError(f"non-monotonic y ordering in strip {strip_index}: {y} < {prev_y}")
            prev_y = y
            parsed_rows.append((y, left, right))
        normalized.append(tuple(parsed_rows))
    return tuple(normalized)


def rasterize_strips(
    strips: Sequence[Sequence[Sequence[int]]],
    *,
    coord_width: int,
    coord_height: int,
    target_height: int = IMAGE_HEIGHT,
    target_width: int = IMAGE_WIDTH,
) -> BinaryMask:
    """Rasterize validated [y, left, right] strip polygons into an H×W bool mask."""
    if target_height <= 0 or target_width <= 0:
        raise ValueError("target dimensions must be positive")
    validated = validate_strips(strips, coord_width=coord_width, coord_height=coord_height)
    scale_x = target_width / coord_width
    scale_y = target_height / coord_height
    canvas = np.zeros((target_height, target_width), dtype=np.uint8)
    for strip in validated:
        polygon = [(left * scale_x, y * scale_y) for y, left, _ in strip]
        polygon.extend((right * scale_x, y * scale_y) for y, _, right in reversed(strip))
        points = np.rint(np.asarray(polygon, dtype=np.float64)).astype(np.int32)
        points[:, 0] = np.clip(points[:, 0], 0, target_width - 1)
        points[:, 1] = np.clip(points[:, 1], 0, target_height - 1)
        cv2.fillPoly(canvas, [points], 1)
    return canvas.astype(bool)


def rasterize_annotation(
    annotation: TrunkAnnotation,
    *,
    target_height: int = IMAGE_HEIGHT,
    target_width: int = IMAGE_WIDTH,
) -> BinaryMask:
    """Rasterize a TrunkAnnotation into the canonical boolean mask."""
    return rasterize_strips(
        annotation.strips,
        coord_width=annotation.coordinate_width,
        coord_height=annotation.coordinate_height,
        target_height=target_height,
        target_width=target_width,
    )


def load_legacy_strip_file(
    path: Path,
    *,
    source_group: str,
    coord_width: int,
    coord_height: int,
    multi_strip: bool,
) -> dict[str, TrunkAnnotation]:
    """Load legacy P03.2-AUTO or P03.2-V2 strip annotations without modifying originals."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows_map = payload["rows"]
    records: dict[str, TrunkAnnotation] = {}
    for filename, raw in rows_map.items():
        strips_raw = raw if multi_strip else [raw]
        strips = validate_strips(strips_raw, coord_width=coord_width, coord_height=coord_height)
        records[filename] = TrunkAnnotation(
            filename=filename,
            source_group=source_group,
            quality_status="ACCEPTED",
            coordinate_width=coord_width,
            coordinate_height=coord_height,
            strips=strips,
            original_source=str(path),
        )
    return records


def load_canonical_annotation_file(
    path: Path,
    *,
    source_group: str,
    quality_status: QualityStatus,
) -> dict[str, TrunkAnnotation]:
    """Load canonical 768×1024 curated annotations (corrected or newly annotated)."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    coord_w = int(payload.get("coordinate_width", IMAGE_WIDTH))
    coord_h = int(payload.get("coordinate_height", IMAGE_HEIGHT))
    records: dict[str, TrunkAnnotation] = {}
    for filename, entry in payload["rows"].items():
        strips = validate_strips(entry["strips"], coord_width=coord_w, coord_height=coord_h)
        records[filename] = TrunkAnnotation(
            filename=filename,
            source_group=source_group,
            quality_status=quality_status,
            coordinate_width=coord_w,
            coordinate_height=coord_h,
            strips=strips,
            traits=tuple(entry.get("traits", ())),
            notes=str(entry.get("reason", "")),
            original_source=str(path),
        )
    return records
