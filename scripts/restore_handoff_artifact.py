"""Verify and restore a named handoff ZIP without overwriting differing files."""

import argparse
import csv
import hashlib
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def restore(archive: Path, bundle_id: str, manifest: Path, destination: Path) -> int:
    with manifest.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    bundles = [row for row in rows if row["artifact_id"] == bundle_id and not row["bundle_id"]]
    if len(bundles) != 1:
        raise ValueError(f"expected one archive for {bundle_id}")
    bundle = bundles[0]
    if archive.stat().st_size != int(bundle["size_bytes"]) or digest(archive) != bundle["sha256"]:
        raise ValueError("archive size or SHA-256 differs from the manifest")
    members = [row for row in rows if row["bundle_id"] == bundle_id]
    by_name = {row["restore_destination"]: row for row in members}
    if not members or len(by_name) != len(members):
        raise ValueError("archive members must have unique restore paths")
    destination = destination.resolve()
    missing: list[tuple[str, Path]] = []
    with zipfile.ZipFile(archive) as bundle_zip:
        archive_names = bundle_zip.namelist()
        if len(archive_names) != len(by_name) or set(archive_names) != by_name.keys():
            raise ValueError("archive membership differs from the manifest")
        for name, row in by_name.items():
            relative = PurePosixPath(name)
            target = destination / relative
            if (
                relative.is_absolute()
                or ".." in relative.parts
                or ":" in name
                or "\\" in name
                or name != relative.as_posix()
                or not target.resolve().is_relative_to(destination)
            ):
                raise ValueError(f"unsafe restore destination: {name}")
            with bundle_zip.open(name) as stream:
                member_hash = hashlib.file_digest(stream, "sha256").hexdigest()
            if member_hash != row["sha256"] or bundle_zip.getinfo(name).file_size != int(
                row["size_bytes"]
            ):
                raise ValueError(f"member checksum or size differs: {name}")
            if target.exists():
                if not target.is_file() or digest(target) != member_hash:
                    raise FileExistsError(f"existing file differs: {name}")
            else:
                missing.append((name, target))

        for name, target in missing:
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle_zip.open(name) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output)
    return len(missing)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_id")
    parser.add_argument("archive", type=Path)
    parser.add_argument(
        "--manifest", type=Path, default=ROOT / "docs/team_preparation/artifact_manifest.csv"
    )
    parser.add_argument("--destination", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        count = restore(args.archive, args.bundle_id, args.manifest, args.destination)
    except (KeyError, OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"Restore failed: {error}", file=sys.stderr)
        return 1
    print(f"PASS: verified {args.bundle_id}; restored {count} new files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
