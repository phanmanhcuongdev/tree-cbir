"""Emit a sanitized environment snapshot."""

import json
import platform
import shutil
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
report = {
    "python": sys.version,
    "executable": sys.executable,
    "platform": platform.platform(),
    "architecture": platform.machine(),
    "git": shutil.which("git"),
    "docker": shutil.which("docker"),
}
(root / "outputs/environment/environment.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(json.dumps(report, indent=2))
