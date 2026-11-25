"""Verify the accepted P02 corpus against its versioned manifest without rewriting images."""

import argparse
import csv
import hashlib
import sys
from pathlib import Path, PurePosixPath

from PIL import Image

from tree_cbir.config import IMAGE_HEIGHT, IMAGE_WIDTH

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_IMAGES = 507


def verify_files(
    directory: Path, rows: list[dict[str, str]], name_key: str, hash_key: str, *, standardized: bool
) -> list[str]:
    expected_names: set[str] = set()
    errors: list[str] = []
    for row in rows:
        name = row[name_key]
        relative = PurePosixPath(name)
        if (
            not name
            or relative.is_absolute()
            or ".." in relative.parts
            or ":" in name
            or "\\" in name
            or name != relative.as_posix()
        ):
            errors.append(f"invalid manifest path: {name!r}")
            continue
        if name in expected_names:
            errors.append(f"duplicate manifest path: {name}")
            continue
        expected_names.add(name)
        path = directory / relative
        if not path.resolve().is_relative_to(directory.resolve()) or not path.is_file():
            errors.append(f"missing or out-of-directory file: {name}")
            continue
        with path.open("rb") as stream:
            actual_hash = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual_hash != row[hash_key]:
            errors.append(f"SHA-256 mismatch: {name}")
        if standardized:
            try:
                with Image.open(path) as image:
                    image.load()
                    if (image.format, image.mode, image.size) != (
                        "JPEG",
                        "RGB",
                        (IMAGE_WIDTH, IMAGE_HEIGHT),
                    ):
                        errors.append(
                            f"expected decoded JPEG RGB {IMAGE_WIDTH}×{IMAGE_HEIGHT}: {name}"
                        )
            except OSError:
                errors.append(f"cannot decode: {name}")

    actual_names = {
        path.relative_to(directory).as_posix()
        for path in directory.rglob("*")
        if path.is_file() and path.name != ".gitkeep"
    }
    errors.extend(f"unexpected file: {name}" for name in sorted(actual_names - expected_names))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "outputs/preprocessing/standardization/standardization_manifest.csv",
    )
    parser.add_argument("--standardized", type=Path, default=ROOT / "data/standardized")
    parser.add_argument("--source", type=Path, help="also verify original images in this directory")
    args = parser.parse_args()
    try:
        with args.manifest.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        if len(rows) != EXPECTED_IMAGES or any(
            row.get("validation_status") != "PASS" for row in rows
        ):
            raise ValueError(f"expected {EXPECTED_IMAGES} accepted rows in the P02 manifest")
        if len({row["output_sha256"] for row in rows}) != EXPECTED_IMAGES:
            raise ValueError("standardized manifest contains repeated or missing output checksums")
        checks = [(args.standardized, "standardized_path", "output_sha256", True)]
        if args.source is not None:
            checks.append((args.source, "source_path", "source_sha256", False))
        for directory, name_key, hash_key, standardized in checks:
            errors = verify_files(directory, rows, name_key, hash_key, standardized=standardized)
            if errors:
                print("\n".join(errors), file=sys.stderr)
                return 1
            label = "standardized JPEG RGB images" if standardized else "original images"
            print(f"PASS: {EXPECTED_IMAGES} {label} match the manifest")
    except (KeyError, OSError, ValueError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
