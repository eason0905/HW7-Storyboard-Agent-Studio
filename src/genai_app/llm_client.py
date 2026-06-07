from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any

import requests


class LLMError(RuntimeError):
    """Raised when an LLM backend cannot produce a usable response."""


@dataclass(frozen=True)
class LLMSettings:
    provider: str = "offline"
    model: str = "llama3.1:8b"
    base_url: str = "http://localhost:11434/v1"
    api_key: str | None = None
    timeout: float = 45.0
    temperature: float = 0.7


def build_settings(
    provider: str,
    model: str,
    base_url: str | None = None,
    api_key: str | None = None,
    timeout: float = 45.0,
    temperature: float = 0.7,
) -> LLMSettings:
    provider = provider.lower().strip()
    if provider == "ollama":
        return LLMSettings(
            provider=provider,
            model=model or "llama3.1:8b",
            base_url=(base_url or "http://localhost:11434/v1").rstrip("/"),
            api_key=api_key or "ollama",
            timeout=timeout,
            temperature=temperature,
        )
    if provider == "openrouter":
        return LLMSettings(
            provider=provider,
            model=model or "openai/gpt-4o-mini",
            base_url=(base_url or "https://openrouter.ai/api/v1").rstrip("/"),
            api_key=api_key or os.getenv("OPENROUTER_API_KEY"),
            timeout=timeout,
            temperature=temperature,
        )
    return LLMSettings(provider="offline", model="offline")


def generate_chat_completion(
    settings: LLMSettings,
    system_prompt: str,
    user_prompt: str,
) -> str:
    if settings.provider == "offline":
        raise LLMError("offline provider selected")
    if settings.provider == "openrouter" and not settings.api_key:
        raise LLMError("OPENROUTER_API_KEY is missing")

    headers: dict[str, str] = {"Content-Type": "application/json"}
    if settings.api_key:
        headers["Authorization"] = f"Bearer {settings.api_key}"
    if settings.provider == "openrouter":
        headers["HTTP-Referer"] = "http://localhost:8501"
        headers["X-Title"] = "Storyboard Agent Studio"

    payload: dict[str, Any] = {
        "model": settings.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": settings.temperature,
    }

    try:
        response = requests.post(
            f"{settings.base_url}/chat/completions",
            json=payload,
            headers=headers,
            timeout=settings.timeout,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc

    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("LLM response did not match the OpenAI chat schema") from exc
