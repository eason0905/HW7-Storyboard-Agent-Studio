# Storyboard Agent Studio

這是我這次 HW7 做的生成式 AI 小專題。  
一開始的想法是做一個可以把「故事概念」轉成分鏡草圖的工具：使用者輸入一段主題，系統會產生幾個場景、每個場景的旁白、影像生成 prompt、negative prompt、鏡頭描述和配色，最後用 Streamlit 做成可以操作的介面。

這個專題主要對應作業要求中的 LLM 應用。程式支援 Ollama 和 OpenRouter 這類 OpenAI-compatible API；如果當下沒有模型或 API key，也可以用 offline mode 先跑完整流程，方便展示和測試。

## 功能

- 輸入一段故事主題或專題概念
- 選擇視覺風格和場景數量
- 使用 LLM 產生結構化 storyboard
- 顯示每個場景的圖片預覽、prompt、negative prompt 和 camera note
- 可以下載產生的 JSON 和 PNG 圖片
- 沒有模型服務時可以用 offline fallback 測試整個 App

## 系統架構

主要程式放在 `src/` 裡面：

- `src/app.py`：Streamlit 介面，負責輸入、模型設定、結果顯示和下載
- `src/genai_app/llm_client.py`：呼叫 Ollama / OpenRouter 的 OpenAI-compatible chat API
- `src/genai_app/prompt_pipeline.py`：整理 prompt、解析 LLM 回傳的 JSON、處理 fallback
- `src/genai_app/image_synth.py`：把每個場景的 prompt 和 palette 轉成一張預覽圖
- `src/genai_app/exporter.py`：輸出 storyboard JSON 和圖片壓縮檔

整體流程大概是：

```text
使用者輸入主題
    -> prompt pipeline 整理成 LLM 任務
    -> LLM 產生 storyboard JSON
    -> 程式解析並補齊場景資料
    -> 產生每個場景的圖片預覽
    -> Streamlit 顯示結果並提供下載
```

## 安裝與執行

先安裝套件：

```bash
python -m pip install -r requirements.txt
```

啟動 App：

```bash
python -m streamlit run src/app.py
```

啟動後瀏覽器打開 Streamlit 顯示的網址，通常會是：

```text
http://localhost:8501
```

## 模型設定

介面左側可以切換三種模式：

- `offline`：不用外部模型，直接用本機 fallback 產生結果
- `ollama`：使用本機 Ollama，例如 `llama3.1:8b`
- `openrouter`：使用 OpenRouter API，需要填 API key

如果要用 Ollama，可以先執行：

```bash
ollama pull llama3.1:8b
ollama serve
```

然後在 App 裡選 `ollama`，base URL 保持：

```text
http://localhost:11434/v1
```

## 測試

我有放幾個簡單測試，主要確認 storyboard pipeline 和圖片產生器可以正常跑：

```bash
python -m pytest
```

目前測試通過：

```text
3 passed
```

## 輸出檔案

App 產生的最新結果會放在：

```text
outputs/latest/
```

裡面會包含：

- `storyboard.json`
- `scene_01.png`
- `scene_02.png`
- 其他場景圖片

這次作業用的展示圖放在：

```text
demo/314833002_HW7.png
```

## 作業相關文件

- `homework desciption.md`：我整理的作業需求和本專題對應方式
- `workflow_log.md`：Agent 協作紀錄
- `314833002_HW7.txt`：GitHub repo 連結
- `requirements.txt`：執行環境套件

## 備註

這個專題的重點不是訓練一個大型模型，而是把 LLM API、prompt engineering、資料格式控制、介面封裝和輸出流程串成一個可以實際操作的小 App。offline mode 是為了避免展示時因為沒有 GPU、沒有 API key 或模型服務沒開而整個不能跑。
