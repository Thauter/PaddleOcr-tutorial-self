[粵語](README.md) | [繁體中文](README.zh-Hant.md) | [English](README.en.md)

> **前言**：呢個項目嘅誕生，源於我當初睇官方文檔時遇到唔少困難。我花咗好多時間研究同試驗，先至摸索出呢啲用法。為咗等後來嘅朋友唔使行咁多冤枉路，我就將心得整理成呢啲簡單嘅腳本同埋呢份筆記，如果咁啱俾人睇到，希望可以幫到大家！

呢份教學會用一個比較輕鬆、似手寫筆記嘅方式，帶你了解每個檔案嘅用途

---

## ⚙️ 事前準備 (Setup)

喺你開始運行任何腳本之前，要先搞掂兩樣嘢：啟動後端嘅 AI 模型伺服器，同埋設定好你嘅 Python 環境。

### 第 1 步：啟動 vLLM 推理伺服器 (用 Docker)

我哋嘅腳本需要一個強大嘅後端嚟做實際嘅圖文辨識，呢個後端係透過 vLLM 加速嘅。最簡單嘅方法係用 Docker 嚟啟動佢。

**前提**：你需要裝咗 [Docker](https://www.docker.com/) 同埋有 NVIDIA 顯示卡（同埋對應嘅驅動程式）。

打開你嘅 Terminal，然後貼上以下指令：

```bash
docker run ^
    -it ^
    --rm ^
    --gpus all ^
    --network host ^
    ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddleocr-genai-vllm-server:latest ^
    paddleocr genai_server --model_name PaddleOCR-VL-0.9B --host 0.0.0.0 --port 8111 --backend vllm
```

**特別注意**：

- 我哋喺上面嘅指令用咗 `--port 8111`，因為項目入面所有 Python 腳本都係設定去連接呢個 port。
- 如果你想用其他 port，記得要將上面嘅 `--port` **同埋**所有 `.py` 檔案入面嘅 `vl_rec_server_url` 一齊改。
- 執行完呢個指令之後，唔好閂咗個 Terminal，等佢喺背景繼續運行。

### 第 2 步：準備 Python 環境 (用 uv)

呢份教學用咗 `uv` Python 套件管理工具。

1.  **建立虛擬環境**:
    我指定用 Python 3.10。喺項目根目錄執行：

    ```bash
    uv venv --python 3.10
    ```

    `uv` 會幫你創建一個叫 `.venv` 嘅資料夾，入面就係乾淨嘅 Python 環境。

2.  **安裝所有套件**:
    跟住，用 `sync` 指令，`uv` 會根據 `pyproject.toml` 同 `uv.lock` 檔案，自動幫你裝哂所有需要嘅套件。
    ```bash
    uv sync
    ```

搞掂哂呢兩步，你就可以開始玩各種腳本啦！

---

## 項目結構概覽

```
.
├── images/             # 所有你要辨識嘅圖片放喺呢度
│   └── 2501.10973.png  # 範例圖片
├── pdfs/               # 所有你要辨識嘅 PDF 檔案放喺呢度
│   └── sample.pdf      # 範例 PDF
├── output_data/        # 腳本產生嘅輸出會放喺類似咁嘅資料夾
├── pyproject.toml      # 項目嘅設定檔
├── baseOcr_output.py   # 【基本】單張圖片辨識，結果印喺畫面
├── All_file_Ocr.py     # 【進階】批次處理資料夾入面所有圖片
├── All_res_Ocr.py      # 【最強】單張圖片詳細處理，輸出選項超多
├── Batch_PDF_Processor.py # 【PDF】用命令行批次處理 PDF
└── Batch_Pdf_Ocr.py    # 【PDF最強】用 Python 批次處理 PDF，逐頁分析
```

---

## 腳本功能詳解

我哋逐個腳本嚟睇下佢哋係做咩嘅啦！

### 👶 `baseOcr_output.py` - 新手體驗版

呢個係最基本嘅腳本

- **功能**：佢會讀取一張指定嘅圖片 (`images/2501.10973.png`)，用 OCR 引擎辨識完之後，直接將結果**印喺你嘅 Terminal (命令行畫面) 上面**。
- **適合場景**：
  - 想快速測試個環境有冇裝好。
  - 睇下 OCR 對某張圖嘅基本辨識效果。
- **點樣用**：直接執行 `uv run python baseOcr_output.py` 就搞掂。

---

### 🗂️ `All_file_Ocr.py` - 圖片批次處理

當你有成個資料夾嘅圖片要處理，就用呢個啦。

- **功能**：佢會走入 `images/` 資料夾，將入面**所有嘅圖片** (png, jpg, jpeg) 逐張攞嚟做 OCR。辨識完嘅結果會儲存成 **JSON** 同 **Markdown** 兩種格式，放喺 `output2/` 資料夾入面。
- **適合場景**：
  - 你有幾十甚至幾百張圖要一次過轉成文字。
  - 唔需要太複雜嘅設定，淨係想快快脆脆攞到結果。
- **點樣用**：`uv run python All_file_Ocr.py`，然後就可以去 `output2/` 睇下成果。

---

### 🔬 `All_res_Ocr.py` - 圖片精細分析

呢個係處理單張圖片功能有最多嘅控制權嘅腳本

- **功能**：同 `baseOcr_output.py` 一樣，佢都係處理單一張圖。但係！佢提供咗好多**開關**畀你校：
  - `SAVE_JSON`：可以揀儲存定唔儲存 JSON 檔案。
  - `SAVE_MARKDOWN`：可以揀儲存定唔儲存 Markdown 檔案。
  - `BLOCK_TEXT_SAVE_MODE`：呢個最特別，你可以揀點樣儲存文字區塊 (block)：
    - `'none'`：唔儲存。
    - `'separate'`：每個文字區塊（例如一個標題、一段內文）存成一個獨立嘅 `.txt` 檔案。
    - `'single'`：將成張圖所有文字區塊，順序放入**一個** `.txt` 檔案。
- **適合場景**：
  - 想深入分析一張圖嘅版面結構。
  - 淨係想要純文字，或者淨係想要 JSON。
  - 做實驗，睇下唔同設定嘅輸出效果。
- **點樣用**：執行前，先打開個檔案，修改上面嗰啲開關，然後 `uv run python All_res_Ocr.py`。

---

### 📜 `Batch_PDF_Processor.py` - PDF 命令行處理器

呢個腳本係專為鍾意用命令行嘅朋友而設，用嚟處理 PDF。

- **功能**：佢會掃描 `pdfs/` 資料夾入面所有嘅 PDF。之後，佢會模仿我哋喺 Terminal 手動打指令嘅方式，為每個 PDF 執行 `paddleocr doc_parser` 呢個 command。每個 PDF 嘅處理結果會放喺 `output_cli/` 入面一個同名嘅子資料夾。
- **適合場景**：
  - 習慣用 command-line tool。
  - 想將 OCR 功能整合到你現有嘅 Shell script 或自動化流程入面。
- **點樣用**：將啲 PDF 放入 `pdfs/`，然後行 `uv run python Batch_PDF_Processor.py`。

---

### 👑 `Batch_Pdf_Ocr.py` - PDF 處理

呢個係處理 PDF 嘅腳本。

- **功能**：同上一個腳本一樣，佢都係處理 `pdfs/` 入面嘅所有 PDF。但佢唔係用命令行，而係直接用 Python library，咁樣可以做到更加精細嘅控制。佢會：
  1.  逐個 PDF 檔案讀取。
  2.  再**逐頁**進行分析。
  3.  為每一頁，你可以好似 `All_res_Ocr.py` 咁，自由選擇要唔要儲存 **JSON**、**Markdown**，同埋點樣儲存**文字區塊** (`BLOCK_TEXT_SAVE_MODE`)。
  4.  結果會好有條理咁存放喺 `output_pdfs/`，每個 PDF 一個資料夾，入面再每頁一個子資料夾。
- **適合場景**：
  - 需要對 PDF 嘅每一頁做詳細分析。
  - 想攞到最完整、最有彈性嘅輸出結果。
- **點樣用**：打開個檔案改好設定，將 PDF 放入 `pdfs/`，然後 `uv run python Batch_Pdf_Ocr.py`。

---

## 總結

希望呢份手寫筆記風嘅教學幫到你啦！

