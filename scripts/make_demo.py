from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from genai_app.image_synth import load_font, render_scene
from genai_app.llm_client import LLMSettings
from genai_app.prompt_pipeline import generate_storyboard


def main() -> None:
    demo_dir = ROOT / "demo"
    demo_dir.mkdir(parents=True, exist_ok=True)
    storyboard = generate_storyboard(
        "A climate-resilient night market that uses community AI to reduce food waste",
        "cinematic concept art",
        4,
        LLMSettings(provider="offline"),
    )
    images = [render_scene(scene, width=640, height=420) for scene in storyboard.scenes]
    canvas = Image.new("RGB", (1320, 1040), "#f5f7fb")
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(22, bold=True)
    body_font = load_font(15)
    draw.text((32, 22), "Storyboard Agent Studio - demo output", fill="#111827", font=title_font)
    draw.text((32, 56), storyboard.logline, fill="#374151", font=body_font)

    positions = [(32, 92), (680, 92), (32, 540), (680, 540)]
    for image, position in zip(images, positions, strict=False):
        canvas.paste(image, position)

    output = demo_dir / "314833002_HW7.png"
    canvas.save(output)
    print(output)


if __name__ == "__main__":
    main()
