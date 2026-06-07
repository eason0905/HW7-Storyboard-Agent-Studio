from __future__ import annotations

import io
import json
from pathlib import Path
import zipfile

from PIL import Image

from .prompt_pipeline import StoryboardPlan


def save_run(storyboard: StoryboardPlan, images: list[Image.Image], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "storyboard.json"
    json_path.write_text(
        json.dumps(storyboard.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    paths = [json_path]
    for scene, image in zip(storyboard.scenes, images, strict=False):
        image_path = output_dir / f"scene_{scene.index:02d}.png"
        image.save(image_path)
        paths.append(image_path)
    return paths


def build_zip(paths: list[Path]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, arcname=path.name)
    return buffer.getvalue()
