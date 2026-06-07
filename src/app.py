from __future__ import annotations

from pathlib import Path

import streamlit as st

from genai_app.exporter import build_zip, save_run
from genai_app.image_synth import render_scene
from genai_app.llm_client import build_settings
from genai_app.prompt_pipeline import generate_storyboard


OUTPUT_DIR = Path("outputs/latest")


st.set_page_config(page_title="Storyboard Agent Studio", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
    div[data-testid="stSidebar"] { border-right: 1px solid #dde3ea; }
    h1, h2, h3 { letter-spacing: 0; }
    .stButton > button { border-radius: 6px; }
    </style>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Model")
    provider = st.selectbox("Provider", ["offline", "ollama", "openrouter"], index=0)
    default_model = {
        "offline": "offline",
        "ollama": "llama3.1:8b",
        "openrouter": "openai/gpt-4o-mini",
    }[provider]
    model = st.text_input("Model", value=default_model)
    base_url = ""
    api_key = ""
    if provider == "ollama":
        base_url = st.text_input("Base URL", value="http://localhost:11434/v1")
    elif provider == "openrouter":
        base_url = st.text_input("Base URL", value="https://openrouter.ai/api/v1")
        api_key = st.text_input("API key", type="password")
    temperature = st.slider("Temperature", 0.0, 1.4, 0.7, 0.1)

st.title("Storyboard Agent Studio")

left, right = st.columns([0.92, 1.08], gap="large")

with left:
    with st.form("storyboard_form"):
        topic = st.text_area(
            "Premise",
            value="A climate-resilient night market that uses community AI to reduce food waste",
            height=118,
        )
        visual_style = st.selectbox(
            "Visual style",
            [
                "cinematic concept art",
                "editorial science illustration",
                "isometric product visualization",
                "documentary photography moodboard",
                "high-contrast cyberpunk poster",
            ],
        )
        scene_count = st.slider("Scenes", 1, 6, 4)
        submitted = st.form_submit_button("Generate storyboard", type="primary")

    if submitted:
        settings = build_settings(provider, model, base_url, api_key, temperature=temperature)
        with st.spinner("Generating"):
            storyboard = generate_storyboard(topic, visual_style, scene_count, settings)
            images = [render_scene(scene) for scene in storyboard.scenes]
            paths = save_run(storyboard, images, OUTPUT_DIR)
            st.session_state["storyboard"] = storyboard
            st.session_state["images"] = images
            st.session_state["paths"] = paths

with right:
    storyboard = st.session_state.get("storyboard")
    images = st.session_state.get("images", [])
    paths = st.session_state.get("paths", [])

    if storyboard is None:
        preview_settings = build_settings("offline", "offline")
        storyboard = generate_storyboard(
            "A climate-resilient night market that uses community AI to reduce food waste",
            "cinematic concept art",
            4,
            preview_settings,
        )
        images = [render_scene(scene) for scene in storyboard.scenes]

    st.subheader(storyboard.title)
    st.caption(f"{storyboard.logline} Backend: {storyboard.backend}.")
    if storyboard.warning:
        st.warning(storyboard.warning)

    if paths:
        st.download_button(
            "Download run",
            data=build_zip(paths),
            file_name="storyboard_agent_run.zip",
            mime="application/zip",
        )

for scene, image in zip(storyboard.scenes, images, strict=False):
    columns = st.columns([0.58, 0.42], gap="medium")
    with columns[0]:
        st.image(image, use_column_width=True)
    with columns[1]:
        st.markdown(f"### {scene.index}. {scene.title}")
        st.write(scene.narration)
        st.markdown("**Image prompt**")
        st.code(scene.image_prompt, language="text")
        st.markdown("**Negative prompt**")
        st.code(scene.negative_prompt, language="text")
        st.markdown(f"**Camera:** {scene.camera}")
