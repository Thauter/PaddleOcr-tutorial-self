[粵語](README.md) | [繁體中文](README.zh-Hant.md) | [English](README.en.md)

> **前言**：本專案的誕生，源於我最初閱讀官方文件時遇到了不少困難。我花費了大量時間研究與試驗，才摸索出這些使用方法。為了讓後繼的朋友們不必走這麼多彎路，我便將心得整理成這些簡易的腳本與這份筆記，若恰巧有人看到，希望能為大家提供幫助！

這份教學將以一種較為輕鬆、類似手寫筆記的方式，引導您了解每個檔案的用途。

---

## ⚙️ 事前準備 (Setup)

在您開始執行任何腳本之前，需要先完成兩件事：啟動後端的 AI 模型伺服器，並設定好您的 Python 環境。

### 第 1 步：啟動 vLLM 推理伺服器 (使用 Docker)

我們的腳本需要一個強大的後端來進行實際的圖文辨識，此後端透過 vLLM 進行加速。最簡單的方法是使用 Docker 來啟動它。

**前提**：您需要已安裝 [Docker](https://www.docker.com/) 並擁有 NVIDIA 顯示卡（以及對應的驅動程式）。

開啟您的終端機，然後貼上以下指令：

```cmd
docker run ^
    -it ^
    --rm ^
    --gpus all ^
    --network host ^
    ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddleocr-genai-vllm-server:latest ^
    paddleocr genai_server --model_name PaddleOCR-VL-0.9B --host 0.0.0.0 --port 8111 --backend vllm
```

**特別注意**：

- 我們在上述指令中使用了 `--port 8111`，因為專案中所有 Python 腳本都設定為連接此埠號。
- 若您想使用其他埠號，請記得務必將上述的 `--port` **以及**所有 `.py` 檔案中的 `vl_rec_server_url` 一同修改。
- 執行此指令後，請勿關閉該終端機，讓它在背景持續運行。

### 第 2 步：準備 Python 環境 (使用 uv)

本專案使用 `uv` 這個高速的 Python 套件管理工具。

1.  **建立虛擬環境**:
    我們指定使用 Python 3.10。請在專案根目錄執行：

    ```bash
    uv venv --python 3.10
    ```

    `uv` 將會為您建立一個名為 `.venv` 的資料夾，其中包含一個乾淨的 Python 環境。

2.  **安裝所有套件**:
    接著，使用 `sync` 指令，`uv` 將會根據 `pyproject.toml` 與 `uv.lock` 檔案，自動為您安裝所有必要的套件。
    ```bash
    uv sync
    ```

完成這兩步後，您就可以開始使用各種腳本了！

---

## 專案結構概覽

```
.
├── images/             # 所有您要辨識的圖片請置於此處
│   └── 2501.10973.png  # 範例圖片
├── pdfs/               # 所有您要辨識的 PDF 檔案請置於此處
│   └── sample.pdf      # 範例 PDF
├── output_data/        # 腳本產生的輸出將存放於類似此類的資料夾
├── pyproject.toml      # 專案的設定檔
├── baseOcr_output.py   # 【基本】單張圖片辨識，結果顯示於終端機
├── All_file_Ocr.py     # 【進階】批次處理資料夾內所有圖片
├── All_res_Ocr.py      # 【最強】單張圖片詳細處理，提供多樣輸出選項
├── Batch_PDF_Processor.py # 【PDF】使用命令列批次處理 PDF
└── Batch_Pdf_Ocr.py    # 【PDF最強】使用 Python 批次處理 PDF，逐頁分析
```

---

## 腳本功能詳解

讓我們逐一檢視每個腳本的功能！

### 👶 `baseOcr_output.py` - 新手體驗版

這是最基本的腳本。

- **功能**：它會讀取一張指定的圖片 (`images/2501.10973.png`)，使用 OCR 引擎辨識後，直接將結果**顯示在您的終端機（命令列介面）上**。
- **適用情境**：
  - 想快速測試環境是否已正確安裝。
  - 檢視 OCR 對某張圖片的基本辨識效果。
- **如何使用**：直接執行 `uv run python baseOcr_output.py` 即可。

---

### 🗂️ `All_file_Ocr.py` - 圖片批次處理

當您有整個資料夾的圖片需要處理時，請使用此腳本。

- **功能**：它會進入 `images/` 資料夾，將其中**所有的圖片** (png, jpg, jpeg) 逐一進行 OCR。辨識完成的結果將儲存為 **JSON** 和 **Markdown** 兩種格式，並存放於 `output2/` 資料夾中。
- **適用情境**：
  - 當您有數十甚至數百張圖片需要一次性轉換為文字時。
  - 不需要複雜的設定，只想快速獲取結果。
- **如何使用**：執行 `uv run python All_file_Ocr.py`，然後即可至 `output2/` 查看成果。

---

### 🔬 `All_res_Ocr.py` - 圖片精細分析

這是處理單張圖片功能中，提供最多控制選項的腳本。

- **功能**：與 `baseOcr_output.py` 同樣處理單一圖片。但它提供了許多**開關**供您調整：
  - `SAVE_JSON`：可選擇是否儲存 JSON 檔案。
  - `SAVE_MARKDOWN`：可選擇是否儲存 Markdown 檔案。
  - `BLOCK_TEXT_SAVE_MODE`：此為最特別的功能，您可選擇如何儲存文字區塊 (block)：
    - `'none'`：不儲存。
    - `'separate'`：每個文字區塊（如一個標題、一段內文）儲存為一個獨立的 `.txt` 檔案。
    - `'single'`：將整張圖片的所有文字區塊，依序存入**單一** `.txt` 檔案中。
- **適用情境**：
  - 希望深入分析一張圖片的版面結構。
  - 僅需純文字或僅需 JSON 格式的結果。
  - 進行實驗，觀察不同設定下的輸出效果。
- **如何使用**：執行前，請先開啟檔案修改上述開關，然後執行 `uv run python All_res_Ocr.py`。

---

### 📜 `Batch_PDF_Processor.py` - PDF 命令列處理器

此腳本專為偏好使用命令列的朋友設計，用於處理 PDF。

- **功能**：它會掃描 `pdfs/` 資料夾中的所有 PDF。之後，它將模擬我們在終端機手動輸入指令的方式，為每個 PDF 執行 `paddleocr doc_parser` 這個 command。每個 PDF 的處理結果將存放於 `output_cli/` 中一個同名的子資料夾。
- **適用情境**：
  - 習慣使用 command-line tool。
  - 希望將 OCR 功能整合至您現有的 Shell script 或自動化流程中。
- **如何使用**：將 PDF 檔案放入 `pdfs/`，然後執行 `uv run python Batch_PDF_Processor.py`。

---

### 👑 `Batch_Pdf_Ocr.py` - PDF 全能處理

這是處理 PDF 功能最完整的腳本。

- **功能**：與前一個腳本相同，它也處理 `pdfs/` 中的所有 PDF。但它不使用命令列，而是直接使用 Python library，從而能進行更精細的控制。它會：
  1.  逐一讀取 PDF 檔案。
  2.  再**逐頁**進行分析。
  3.  對於每一頁，您可以像 `All_res_Ocr.py` 一樣，自由選擇是否要儲存 **JSON**、**Markdown**，以及如何儲存**文字區塊** (`BLOCK_TEXT_SAVE_MODE`)。
  4.  結果將有條理地存放於 `output_pdfs/`，每個 PDF 一個資料夾，內部再為每頁建立一個子資料夾。
- **適用情境**：
  - 需要對 PDF 的每一頁進行詳細分析。
  - 希望獲得最完整、最具彈性的輸出結果。
- **如何使用**：開啟檔案修改好設定，將 PDF 放入 `pdfs/`，然後執行 `uv run python Batch_Pdf_Ocr.py`。

---

## 總結

希望這份筆記風格的教學對您有幫助！

