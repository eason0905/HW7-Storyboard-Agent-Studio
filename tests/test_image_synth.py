from __future__ import annotations

from genai_app.image_synth import render_scene
from genai_app.prompt_pipeline import ScenePlan


def test_render_scene_returns_rgb_image() -> None:
    scene = ScenePlan(
        index=1,
        title="Test",
        narration="A generated preview scene.",
        image_prompt="solar classroom agent interface",
        negative_prompt="blur",
        camera="wide",
        palette=["#184e77", "#52b788", "#f9c74f"],
    )

    image = render_scene(scene, width=320, height=220)

    assert image.mode == "RGB"
    assert image.size == (320, 220)
