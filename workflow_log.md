# Agent Collaboration Log

本文件記錄這次 HW7 專題使用 Agent 輔助開發的過程。  
專題名稱是 **Storyboard Agent Studio**，目標是做一個可以把故事概念轉成分鏡草圖與影像 prompt 的互動式生成 AI App。

## 1. 發想與題目選定

一開始我先把作業要求提供給 Codex，請它整理這次作業必須包含的內容。作業重點包含：

- 需要是一個可操作的生成式 AI App
- 至少要整合 LLM 或 Diffusion / Flow Matching 其中一種技術
- 需要有互動介面
- 需要有 README、workflow log、source code 和展示素材

我給 Agent 的初始 prompt 大意如下：

```text
請根據 HW7 期末作業要求，幫我設計一個可以在本機執行的生成式 AI 專題。
專題需要有互動介面、README、workflow log、requirements.txt、demo 截圖，
並且至少使用 LLM 或 diffusion 其中一種生成式 AI 技術。
```

Agent 一開始提出幾種方向，例如：

- 用 LLM 做 RAG 問答工具
- 用 LLM 產生故事與影像 prompt
- 做一個文字到 storyboard 的生成工具

最後我選擇 storyboard 方向，原因是它可以清楚呈現 LLM 的 prompt engineering，也可以做出比較容易展示的視覺結果。

## 2. 系統設計與任務拆解

選定題目後，我請 Agent 進一步把系統拆成可實作的部分。  
當時給的 prompt 大意如下：

```text
我想做 Storyboard Agent Studio。
使用者輸入一段故事概念，LLM 要產生分鏡標題、旁白、image prompt、
negative prompt、camera note 和 palette。
請幫我拆解系統架構，並規劃 Streamlit App 的檔案結構。
```

Agent 建議的架構如下：

```text
Streamlit UI
    -> prompt pipeline
    -> LLM client
    -> storyboard JSON parser
    -> preview image renderer
    -> export JSON / PNG
```

我採用這個架構，並把程式拆成幾個檔案：

- `src/app.py`：Streamlit 互動介面
- `src/genai_app/llm_client.py`：負責呼叫 Ollama 或 OpenRouter
- `src/genai_app/prompt_pipeline.py`：負責 prompt、JSON parsing 和 fallback
- `src/genai_app/image_synth.py`：負責把場景資訊轉成預覽圖
- `src/genai_app/exporter.py`：負責輸出 JSON 和圖片壓縮檔

## 3. LLM Prompt 設計

這個專題最重要的地方是讓 LLM 不只是聊天，而是產生可被程式解析的結構化資料。  
我請 Agent 幫我設計 system prompt，要求模型只能回傳 JSON。

關鍵 prompt 概念如下：

```text
You are a senior creative technologist.
Return strict JSON only.
Design a coherent short storyboard.
Every scene must include title, narration, image_prompt,
negative_prompt, camera, and palette.
```

使用者輸入的故事主題會被整理成 JSON 任務，例如：

```json
{
  "task": "Create a storyboard for an interactive generative AI app demo.",
  "topic": "A climate-resilient night market that uses community AI to reduce food waste",
  "visual_style": "cinematic concept art",
  "scene_count": 4
}
```

LLM 理想上會回傳：

```json
{
  "title": "Climate Night Market Storyboard",
  "logline": "A short generated visual sequence...",
  "scenes": [
    {
      "title": "Signal",
      "narration": "The system reads the user's intent...",
      "image_prompt": "cinematic concept art...",
      "negative_prompt": "blurry, low quality...",
      "camera": "wide establishing shot",
      "palette": ["#184e77", "#52b788", "#f9c74f"]
    }
  ]
}
```

## 4. 實作過程

實作時我讓 Agent 先產生核心程式，再逐步測試與修正。

使用過的主要工具：

- Codex CLI：協助產生程式、整理作業需求與修改文件
- Streamlit：建立互動式 App
- Pillow / NumPy：產生 storyboard preview image
- Pytest：測試 prompt pipeline 與 image renderer
- Git / GitHub：版本控制與提交作業 repo
- Playwright：擷取 App 實際運行畫面作為展示素材

我給 Agent 的 implementation prompt 大意如下：

```text
請建立一個 Streamlit app。
側邊欄可以選 offline / Ollama / OpenRouter。
主畫面可以輸入 premise、visual style、scene count。
按下 generate 後顯示 storyboard title、logline、scene image、
image prompt、negative prompt 和 camera note。
同時提供下載 JSON 和 PNG 的功能。
```

完成初版後，我請 Agent 補上測試：

```text
請幫我補 pytest，至少確認 offline storyboard 會產生指定 scene count，
JSON fence 可以被正確解析，image renderer 會產生 RGB image。
```

最後測試結果：

```text
3 passed
```

## 5. 遇到的問題與修正

### 問題一：不能假設每台電腦都有 LLM API key

如果只依賴 OpenRouter 或本機 Ollama，展示時可能會因為沒有 API key 或模型沒有啟動而失敗。  
因此 Agent 建議加入 `offline` 模式。

解法：

- offline mode 會用 deterministic fallback 產生 storyboard
- fallback 的資料格式和 LLM 回傳格式相同
- UI 不需要分別處理兩種資料來源

### 問題二：LLM 回傳 JSON 可能不乾淨

有些模型會把 JSON 包在 Markdown code fence 裡，或多加說明文字。  
因此 Agent 幫我加入 JSON extraction：

- 如果有 ```json code fence，就先取出 fence 內文字
- 找出第一個 `{` 和最後一個 `}`
- 再交給 `json.loads()` 解析

這樣可以提高不同模型輸出時的穩定性。

### 問題三：原本展示圖不夠像 App 截圖

一開始 demo 圖只是把幾張生成結果拼在一起，沒有明確展示使用者輸入、模型設定和 App 介面。  
後來我改用 Playwright 擷取實際 Streamlit 頁面，讓展示素材能更清楚證明系統真的可以運行。

修改後的展示圖：

```text
demo/314833002_HW7.png
```

## 6. 最終功能

目前 App 可以做到：

- 使用者輸入故事或專題概念
- 選擇 storyboard 視覺風格
- 選擇場景數量
- 切換 offline、Ollama 或 OpenRouter
- 產生 title、logline、scene narration
- 產生 image prompt、negative prompt、camera note
- 顯示每個場景的 preview image
- 匯出 `storyboard.json` 和圖片

## 7. 最終檔案

本次作業 repo 中主要檔案：

- `README.md`：專題介紹、架構與執行方式
- `workflow_log.md`：本文件，記錄 Agent 輔助流程
- `requirements.txt`：Python 套件需求
- `src/app.py`：Streamlit App
- `src/genai_app/`：LLM client、prompt pipeline、image renderer 等核心程式
- `tests/`：pytest 測試
- `demo/314833002_HW7.png`：App 實際運行截圖
- `314833002_HW7.txt`：GitHub repo 連結

## 8. 我的整理

這次使用 Agent 的方式不是只叫它「幫我完成作業」，而是把它當成一個可以協助規劃、拆任務、寫程式和除錯的工具。  
我負責決定題目方向、確認作業要求、選擇技術架構和檢查最後輸出；Agent 則協助快速建立程式骨架、補測試、修文件和產生展示素材。

整體來說，這個專題符合本次作業要求中的 LLM 應用、互動式 App、Agent workflow 紀錄與展示素材。
