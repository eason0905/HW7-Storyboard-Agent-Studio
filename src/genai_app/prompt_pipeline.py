from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re
from typing import Any

from .llm_client import LLMError, LLMSettings, generate_chat_completion


SYSTEM_PROMPT = """You are a senior creative technologist.
Return strict JSON only. No markdown fences. Design a coherent short storyboard
for a generative AI demo app. Every scene must include title, narration,
image_prompt, negative_prompt, camera, and palette."""


@dataclass
class ScenePlan:
    index: int
    title: str
    narration: str
    image_prompt: str
    negative_prompt: str
    camera: str
    palette: list[str]


@dataclass
class StoryboardPlan:
    title: str
    logline: str
    visual_style: str
    scenes: list[ScenePlan]
    backend: str
    warning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "logline": self.logline,
            "visual_style": self.visual_style,
            "backend": self.backend,
            "warning": self.warning,
            "scenes": [asdict(scene) for scene in self.scenes],
        }


def clamp_scene_count(scene_count: int) -> int:
    return max(1, min(int(scene_count), 6))


def generate_storyboard(
    topic: str,
    visual_style: str,
    scene_count: int,
    settings: LLMSettings | None = None,
) -> StoryboardPlan:
    scene_count = clamp_scene_count(scene_count)
    topic = normalize_topic(topic)
    visual_style = visual_style.strip() or "cinematic concept art"
    settings = settings or LLMSettings(provider="offline")

    if settings.provider == "offline":
        return fallback_storyboard(topic, visual_style, scene_count, "offline fallback")

    user_prompt = build_user_prompt(topic, visual_style, scene_count)
    try:
        raw = generate_chat_completion(settings, SYSTEM_PROMPT, user_prompt)
        return parse_storyboard(raw, topic, visual_style, scene_count, settings.provider)
    except (LLMError, ValueError, json.JSONDecodeError) as exc:
        plan = fallback_storyboard(topic, visual_style, scene_count, settings.provider)
        plan.warning = f"LLM backend unavailable or invalid JSON; used fallback. Details: {exc}"
        return plan


def build_user_prompt(topic: str, visual_style: str, scene_count: int) -> str:
    return json.dumps(
        {
            "task": "Create a storyboard for an interactive generative AI app demo.",
            "topic": topic,
            "visual_style": visual_style,
            "scene_count": scene_count,
            "schema": {
                "title": "string",
                "logline": "string",
                "scenes": [
                    {
                        "title": "string",
                        "narration": "string",
                        "image_prompt": "string",
                        "negative_prompt": "string",
                        "camera": "string",
                        "palette": ["#RRGGBB", "#RRGGBB", "#RRGGBB"],
                    }
                ],
            },
        },
        ensure_ascii=False,
    )


def parse_storyboard(
    raw: str,
    topic: str,
    visual_style: str,
    scene_count: int,
    backend: str,
) -> StoryboardPlan:
    data = json.loads(extract_json_object(raw))
    scenes_data = data.get("scenes")
    if not isinstance(scenes_data, list) or not scenes_data:
        raise ValueError("storyboard JSON is missing scenes")

    scenes: list[ScenePlan] = []
    for index, item in enumerate(scenes_data[:scene_count], start=1):
        if not isinstance(item, dict):
            continue
        scenes.append(
            ScenePlan(
                index=index,
                title=str(item.get("title") or f"Scene {index}"),
                narration=str(item.get("narration") or item.get("description") or ""),
                image_prompt=str(item.get("image_prompt") or item.get("prompt") or topic),
                negative_prompt=str(item.get("negative_prompt") or "low quality, blurry"),
                camera=str(item.get("camera") or "medium shot"),
                palette=clean_palette(item.get("palette")),
            )
        )

    if len(scenes) < scene_count:
        fallback = fallback_storyboard(topic, visual_style, scene_count, backend)
        scenes.extend(fallback.scenes[len(scenes) : scene_count])

    return StoryboardPlan(
        title=str(data.get("title") or f"{topic.title()} Storyboard"),
        logline=str(data.get("logline") or f"A generated visual sequence about {topic}."),
        visual_style=visual_style,
        scenes=scenes,
        backend=backend,
    )


def extract_json_object(raw: str) -> str:
    text = raw.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON object found")
    return text[start : end + 1]


def clean_palette(value: Any) -> list[str]:
    if not isinstance(value, list):
        return ["#1f6feb", "#f2cc60", "#2da44e"]
    colors = [str(color) for color in value if re.fullmatch(r"#[0-9a-fA-F]{6}", str(color))]
    return colors[:5] or ["#1f6feb", "#f2cc60", "#2da44e"]


def normalize_topic(topic: str) -> str:
    topic = " ".join(topic.strip().split())
    return topic or "a climate-resilient city powered by community AI"


def fallback_storyboard(
    topic: str,
    visual_style: str,
    scene_count: int,
    backend: str,
) -> StoryboardPlan:
    scene_count = clamp_scene_count(scene_count)
    keywords = keyword_bank(topic)
    palettes = [
        ["#184e77", "#52b788", "#f9c74f", "#f94144"],
        ["#3a0ca3", "#4cc9f0", "#ffbe0b", "#fb5607"],
        ["#0b132b", "#5bc0be", "#f7fff7", "#ff6b6b"],
        ["#2f3e46", "#cad2c5", "#84a98c", "#ffb703"],
        ["#001219", "#0a9396", "#ee9b00", "#ca6702"],
        ["#2b2d42", "#8d99ae", "#edf2f4", "#ef233c"],
    ]
    beats = [
        ("Signal", "The system reads the user's intent and extracts the creative direction."),
        ("Expansion", "The agent expands the idea into concrete narrative and visual constraints."),
        ("Synthesis", "The generation layer converts prompts into a visible scene preview."),
        ("Review", "The user compares outputs and refines the next prompt iteration."),
        ("Delivery", "The final storyboard is exported with reproducible metadata."),
        ("Reflection", "The workflow log captures agent prompts, bottlenecks, and fixes."),
    ]

    scenes: list[ScenePlan] = []
    for index in range(scene_count):
        beat_title, beat_text = beats[index]
        digest = hashlib.sha256(f"{topic}-{visual_style}-{index}".encode()).hexdigest()
        focus = keywords[index % len(keywords)]
        accent = keywords[(index + 1) % len(keywords)]
        scenes.append(
            ScenePlan(
                index=index + 1,
                title=f"{beat_title}: {focus.title()}",
                narration=f"{beat_text} The scene connects {focus} with {accent}.",
                image_prompt=(
                    f"{topic}, {focus}, {accent}, {visual_style}, cinematic lighting, "
                    f"layered composition, high detail, seed motif {digest[:8]}"
                ),
                negative_prompt="blurry, distorted text, low contrast, duplicated objects",
                camera=["wide establishing shot", "overhead interface view", "close-up detail"][index % 3],
                palette=palettes[index % len(palettes)],
            )
        )

    return StoryboardPlan(
        title=f"{topic.title()} Storyboard Agent",
        logline=f"An agent-assisted generative storyboard about {topic}.",
        visual_style=visual_style,
        scenes=scenes,
        backend=backend,
    )


def keyword_bank(topic: str) -> list[str]:
    words = [
        word.lower()
        for word in re.findall(r"[A-Za-z0-9]+", topic)
        if len(word) > 2 and word.lower() not in {"the", "and", "with", "for"}
    ]
    defaults = ["intent", "agent", "prompt", "latent", "render", "export"]
    unique = list(dict.fromkeys(words + defaults))
    return unique[:8]
