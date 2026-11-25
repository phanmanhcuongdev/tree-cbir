"""Canonical non-destructive RGB preprocessing for dataset and query images."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

from .config import IMAGE_HEIGHT, IMAGE_WIDTH
from .models import ImageMetadata, PreprocessedImage

ImageInput = str | Path | bytes | Image.Image


class PreprocessingError(ValueError):
    pass


def _open(source: ImageInput) -> Image.Image:
    try:
        if isinstance(source, Image.Image):
            return source.copy()
        if isinstance(source, bytes):
            if not source:
                raise PreprocessingError("image bytes are empty")
            return Image.open(BytesIO(source))
        return Image.open(Path(source))
    except (FileNotFoundError, OSError, UnidentifiedImageError) as error:
        raise PreprocessingError(f"cannot decode image: {error}") from error


def preprocess_image(source: ImageInput, image_id: str = "query") -> PreprocessedImage:
    """EXIF-correct, black alpha-composite, center-crop 3:4, resize RGB uint8.
    Center cropping assumes a centered tree; tree-aware cropping is outside P02.
    """
    image = ImageOps.exif_transpose(_open(source))
    if image.mode == "RGBA":
        base = Image.new("RGBA", image.size, (0, 0, 0, 255))
        base.alpha_composite(image)
        image = base.convert("RGB")
    else:
        image = image.convert("RGB")
    width, height = image.size
    ratio = width / height
    target = IMAGE_WIDTH / IMAGE_HEIGHT
    if not np.isclose(ratio, target):
        if ratio > target:
            crop = round(height * target)
            left = (width - crop) // 2
            image = image.crop((left, 0, left + crop, height))
        else:
            crop = round(width / target)
            top = (height - crop) // 2
            image = image.crop((0, top, width, top + crop))
    if image.size != (IMAGE_WIDTH, IMAGE_HEIGHT):
        image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)
    return PreprocessedImage(
        ImageMetadata(image_id, Path(str(image_id))),
        np.ascontiguousarray(np.asarray(image, dtype=np.uint8)),
    )
