"""Save P03.1 evidence for six deterministic standardized images."""

from pathlib import Path

import cv2
from PIL import Image

from tree_cbir.preprocessing import preprocess_image
from tree_cbir.segmentation.trunk_candidates import generate_candidates

root = Path(__file__).resolve().parents[1]
output = root / "outputs/trunk/p03_1"
output.mkdir(parents=True, exist_ok=True)
files = sorted((root / "data/standardized").glob("*.jpg"))[:6]
for path in files:
    rgb = preprocess_image(path, path.name).rgb
    candidates, diagnostics = generate_candidates(rgb)
    overlay = rgb.copy()
    for item in candidates:
        cv2.rectangle(
            overlay, (item.x, item.y), (item.x + item.width, item.y + item.height), (255, 0, 0), 2
        )
    Image.fromarray(diagnostics["bark_evidence"] * 255).save(output / f"{path.stem}_bark.png")
    Image.fromarray(diagnostics["edge_evidence"] * 255).save(output / f"{path.stem}_edges.png")
    Image.fromarray(overlay).save(output / f"{path.stem}_candidates.jpg")
    (output / f"{path.stem}_scores.txt").write_text(
        "\n".join(map(str, candidates)), encoding="utf-8"
    )
