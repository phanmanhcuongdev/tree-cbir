"""Stable cross-phase constants and feature-group slices."""

from enum import StrEnum
from pathlib import Path
from types import MappingProxyType

IMAGE_WIDTH = 768
IMAGE_HEIGHT = 1024
FEATURE_DIMENSION = 38
TRUNK = slice(0, 9)
CANOPY = slice(9, 17)
BRANCH = slice(17, 20)
ROOT = slice(20, 26)
CONTEXT = slice(26, 38)
FEATURE_IDS = tuple(f"X{i}" for i in range(FEATURE_DIMENSION))
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class FeatureGroup(StrEnum):
    TRUNK = "trunk"
    CANOPY = "canopy"
    BRANCH = "branch"
    ROOT = "root"
    CONTEXT = "context"


FEATURE_GROUP_SLICES = MappingProxyType(
    dict(zip(FeatureGroup, (TRUNK, CANOPY, BRANCH, ROOT, CONTEXT), strict=True))
)
