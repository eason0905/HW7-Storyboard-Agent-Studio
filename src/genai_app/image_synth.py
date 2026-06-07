from __future__ import annotations

import hashlib
import math
from pathlib import Path
import textwrap
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .prompt_pipeline import ScenePlan


def render_scene(scene: ScenePlan, width: int = 768, height: int = 512) -> Image.Image:
    seed = stable_seed(
        f"{scene.index}|{scene.title}|{scene.image_prompt}|{','.join(scene.palette)}"
    )
    rng = np.random.default_rng(seed)
    palette = [hex_to_rgb(color) for color in scene.palette]
    while len(palette) < 4:
        palette.append(random_color(rng))

    base = gradient_background(width, height, palette, rng)
    image = Image.fromarray(base, mode="RGB").filter(ImageFilter.GaussianBlur(radius=0.6))
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for layer in range(18):
        color = palette[layer % len(palette)]
        alpha = int(rng.integers(54, 150))
        shape_color = (*color, alpha)
        x1 = int(rng.integers(-width // 8, width))
        y1 = int(rng.integers(-height // 8, height))
        w = int(rng.integers(width // 9, width // 3))
        h = int(rng.integers(height // 9, height // 2))
        x2 = x1 + w
        y2 = y1 + h
        if layer % 3 == 0:
            draw.ellipse((x1, y1, x2, y2), fill=shape_color)
        elif layer % 3 == 1:
            draw.rounded_rectangle((x1, y1, x2, y2), radius=8, fill=shape_color)
        else:
            points = [
                (x1, y1),
                (x2, int((y1 + y2) / 2)),
                (int((x1 + x2) / 2), y2),
            ]
            draw.polygon(points, fill=shape_color)

    for _ in range(26):
        color = (*palette[int(rng.integers(0, len(palette)))], int(rng.integers(80, 180)))
        x = int(rng.integers(0, width))
        y = int(rng.integers(0, height))
        length = int(rng.integers(width // 8, width // 2))
        angle = float(rng.uniform(0, math.pi * 2))
        draw.line(
            (x, y, x + int(math.cos(angle) * length), y + int(math.sin(angle) * length)),
            fill=color,
            width=int(rng.integers(1, 5)),
        )

    image = Image.alpha_composite(image.convert("RGBA"), overlay)
    image = image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=3))
    add_caption(image, scene)
    return image.convert("RGB")


def save_scene_images(scenes: Iterable[ScenePlan], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for scene in scenes:
        path = output_dir / f"scene_{scene.index:02d}.png"
        render_scene(scene).save(path)
        paths.append(path)
    return paths


def gradient_background(
    width: int,
    height: int,
    palette: list[tuple[int, int, int]],
    rng: np.random.Generator,
) -> np.ndarray:
    x = np.linspace(0, 1, width, dtype=np.float32)
    y = np.linspace(0, 1, height, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    c1 = np.array(palette[0], dtype=np.float32)
    c2 = np.array(palette[1], dtype=np.float32)
    c3 = np.array(palette[2], dtype=np.float32)
    radial = np.sqrt((xx - 0.5) ** 2 + (yy - 0.4) ** 2)
    blend = np.clip((xx * 0.7 + yy * 0.3), 0, 1)
    base = c1 * (1 - blend[..., None]) + c2 * blend[..., None]
    base = base * (1 - radial[..., None] * 0.55) + c3 * (radial[..., None] * 0.35)
    noise = rng.normal(0, 9, size=(height, width, 3))
    return np.clip(base + noise, 0, 255).astype(np.uint8)


def add_caption(image: Image.Image, scene: ScenePlan) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    width, height = image.size
    title_font = load_font(16, bold=True)
    body_font = load_font(14)
    title = f"{scene.index}. {scene.title}"
    body = scene.narration
    lines = [title] + textwrap.wrap(body, width=82)[:2]
    panel_height = 92
    draw.rectangle((0, height - panel_height, width, height), fill=(0, 0, 0, 166))
    y = height - panel_height + 12
    for line_index, line in enumerate(lines):
        fill = (255, 255, 255, 245) if line_index == 0 else (232, 238, 245, 224)
        font = title_font if line_index == 0 else body_font
        draw.text((18, y), line, fill=fill, font=font)
        y += 24 if line_index == 0 else 21


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"] if bold else ["DejaVuSans.ttf"]
    search_paths = [
        Path("/usr/share/fonts/truetype/dejavu") / name
        for name in names
    ] + [Path("/home/pohua0905/anaconda3/lib/python3.11/site-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf")]
    for path in search_paths:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16) % (2**32)


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.strip().lstrip("#")
    return tuple(int(color[index : index + 2], 16) for index in (0, 2, 4))


def random_color(rng: np.random.Generator) -> tuple[int, int, int]:
    return tuple(int(value) for value in rng.integers(40, 230, size=3))
