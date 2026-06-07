# Homework Description

## 作業主題

本次期末作業是「Deep Generative Models」課程的 Agent-Driven Integration Project。目標是完成一個可互動的生成式 AI App，並用 AI Agent 輔助完成從發想、架構設計、任務拆解、程式碼生成、除錯到文件撰寫的完整流程。

## 核心要求

- 專題需具備完整可執行的互動介面，可使用 Gradio、Streamlit 或前端框架。
- 技術內容至少需包含 Large Language Models 或 Diffusion / Flow Matching Models 其中一項。
- LLM 應用可包含 Prompt Engineering、RAG、API 呼叫、本機開源模型推論或 OpenAI-compatible API。
- Diffusion / Flow Matching 應用可包含影像、音訊或 3D 生成，以及 ControlNet、LoRA、客製化 pipeline 或推論加速。
- 作業過程需明確呈現 Agentic Workflow，並記錄關鍵 prompt、工具組合與除錯過程。

## 本專題選題

專題名稱：Storyboard Agent Studio

本專題是一個以 LLM 為核心的生成式 AI 分鏡工具。使用者輸入一段主題或故事概念後，系統會透過 LLM 或本機 fallback pipeline 產生故事標題、logline、多段場景敘事、影像生成 prompt、negative prompt、鏡頭語言與色彩配置。App 會將每個場景渲染成可視覺化的 storyboard preview，並可匯出 JSON 與 PNG 結果。

## 技術對應

- Large Language Models：支援 Ollama 與 OpenRouter 等 OpenAI-compatible Chat Completion API，用於生成結構化 storyboard JSON。
- Prompt Engineering：以 system prompt 限定輸出 schema，要求模型產出可解析的 title、logline、scenes、image_prompt、negative_prompt、camera 與 palette。
- Interactive App：使用 Streamlit 建立本機互動介面。
- Agent Workflow：使用 Codex CLI 進行需求整理、架構規劃、程式碼生成、測試與文件生成。

## 繳交項目

- Source code：本資料夾中的 `src/`、`tests/`、`requirements.txt`。
- README：`README.md`。
- Workflow Log：`workflow_log.md`。
- Demonstration material：`demo/314833002_HW7.png`。
- GitHub link txt：`314833002_HW7.txt`，內容為公開 GitHub repo URL。
