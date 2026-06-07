from __future__ import annotations

from genai_app.llm_client import LLMSettings
from genai_app.prompt_pipeline import generate_storyboard, parse_storyboard


def test_offline_storyboard_has_requested_scene_count() -> None:
    plan = generate_storyboard(
        "AI assisted campus recycling",
        "editorial science illustration",
        3,
        LLMSettings(provider="offline"),
    )

    assert plan.backend == "offline fallback"
    assert len(plan.scenes) == 3
    assert all(scene.image_prompt for scene in plan.scenes)


def test_parse_storyboard_accepts_json_fence() -> None:
    raw = """```json
    {
      "title": "Demo",
      "logline": "A tiny demo.",
      "scenes": [
        {
          "title": "One",
          "narration": "Scene narration.",
          "image_prompt": "clean generated city",
          "negative_prompt": "blur",
          "camera": "wide",
          "palette": ["#112233", "#445566", "#778899"]
        }
      ]
    }
    ```"""

    plan = parse_storyboard(raw, "demo", "cinematic", 1, "ollama")

    assert plan.title == "Demo"
    assert plan.scenes[0].palette == ["#112233", "#445566", "#778899"]
