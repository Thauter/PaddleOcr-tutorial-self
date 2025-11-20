[English](README.md) | [繁體中文](README.zh-Hant.md) | [粵語](README.yue.md)

> **前言**：本專案的誕生，源於我當初閱讀官方文件時遇到了不少困難。我花費了許多時間研究與試驗，才摸索出這些用法。為了讓後來的朋友們不必走這麼多冤枉路，我將心得整理成這些簡單的腳本以及這份筆記，如果剛好被人看到，希望能幫助到大家！

這份教學將以一個比較輕鬆、類似手寫筆記的方式，帶你了解每個檔案的用途

## <img src="./preview/Preview_allres_log.png" width="25%"><img src="./preview/Previewjsonoutput.png" width="25%"><img src="./preview/previewlog.png" width="25%"><img src="./preview/Previewmd_output.png" width="25%">

---

## ⚙️ 事前準備 (Setup)

在你開始執行任何腳本之前，要先完成兩件事：啟動後端的 AI 模型伺服器，以及設定好你的 Python 環境。

### 第 1 步：啟動 vLLM 推理伺服器 (使用 Docker)

我們的腳本需要一個強大的後端來做實際的圖文辨識，這個後端是透過 vLLM 加速的。最簡單的方法是使用 Docker 來啟動它。

**前提**：你需要安裝了 [Docker](https://www.docker.com/) 以及擁有 NVIDIA 顯示卡（以及對應的驅動程式）。

打開你的 Terminal，然後貼上以下指令：

docker for Apple silicon cpu

```bash
docker run --rm --name paddleocr-vllm  --ipc=host --shm-size=13g -p 8111:8111 thauter/paddleocr-vl-vllm:cpu
```

docker for gpu #cuda

```bash
docker run -d -p 8111:8111 --gpus all --name paddleocr-vllm-server ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddleocr-genai-vllm-server:latest paddleocr genai_server --model_name PaddleOCR-VL-0.9B --host 0.0.0.0 --port 8111 --backend vllm
```

**特別注意**：

- 我們在上面的指令使用了 `--port 8111`，因為專案裡面所有 Python 腳本都是設定去連接這個 port。
- 如果你想用其他 port，記得要將上面的 `--port` **以及**所有 `.py` 檔案裡面的 `vl_rec_server_url` 一起改。
- 執行完這個指令之後，不要關閉 Terminal，讓它在背景繼續執行。

### 第 2 步：準備 Python 環境 (使用 uv)

這份教學使用了 `uv` Python 套件管理工具。

1.  **建立虛擬環境**:
    我指定使用 Python 3.10。在專案根目錄執行：

    ```bash
    uv venv --python 3.10
    ```

    `uv` 會幫你創建一個叫 `.venv` 的資料夾，裡面就是乾淨的 Python 環境。

2.  **安裝所有套件**:
    接著，使用 `sync` 指令，`uv` 會根據 `pyproject.toml` 和 `uv.lock` 檔案，自動幫你安裝好所有需要的套件。
    ```bash
    uv sync
    ```

完成這兩步，你就可以開始使用各種腳本啦！

---

## 專案結構概覽

```
.
├── images/             # 所有你要辨識的圖片放在這裡
│   └── 2501.10973.png  # 範例圖片
├── pdfs/               # 所有你要辨識的 PDF 檔案放在這裡
│   └── sample.pdf      # 範例 PDF
├── output_data/        # 腳本產生的輸出會放在類似這樣的資料夾
├── pyproject.toml      # 專案的設定檔
├── baseOcr_output.py   # 【基本】單張圖片辨識，結果印在畫面
├── All_file_Ocr.py     # 【進階】批次處理資料夾裡面所有圖片
├── All_res_Ocr.py      # 【最強】單張圖片詳細處理，輸出選項超多
├── Batch_PDF_Processor.py # 【PDF】用命令行批次處理 PDF
└── Batch_Pdf_Ocr.py    # 【PDF最強】用 Python 批次處理 PDF，逐頁分析
```

---

## 腳本功能詳解

我們逐個腳本來看一下它們是做什麼的吧！

### 👶 `baseOcr_output.py` - 新手體驗版

這是最基本的腳本

- **功能**：它會讀取一張指定的圖片 (`images/2501.10973.png`)，用 OCR 引擎辨識完之後，直接將結果**印在你的 Terminal (命令行畫面) 上面**。
- **適合場景**：
  - 想快速測試環境有沒有裝好。
  - 看一下 OCR 對某張圖的基本辨識效果。
- **如何使用**：直接執行 `uv run python baseOcr_output.py` 就搞定。

---

### 🗂️ `All_file_Ocr.py` - 圖片批次處理

當你有整個資料夾的圖片要處理，就用這個啦。

- **功能**：它會進入 `images/` 資料夾，將裡面**所有的圖片** (png, jpg, jpeg) 逐張拿來做 OCR。辨識完的結果會儲存成 **JSON** 和 **Markdown** 兩種格式，放在 `output2/` 資料夾裡面。
- **適合場景**：
  - 你有幾十甚至幾百張圖要一次轉成文字。
  - 不需要太複雜的設定，只是想快速拿到結果。
- **如何使用**：`uv run python All_file_Ocr.py`，然後就可以去 `output2/` 看一下成果。

---

### 🔬 `All_res_Ocr.py` - 圖片精細分析

這是處理單張圖片功能有最多控制權的腳本

- **功能**：同 `baseOcr_output.py` 一樣，它也是處理單一張圖。但是！它提供了很多**開關**給你調整：
  - `SAVE_JSON`：可以選儲存還是不儲存 JSON 檔案。
  - `SAVE_MARKDOWN`：可以選儲存還是不儲存 Markdown 檔案。
  - `BLOCK_TEXT_SAVE_MODE`：這個最特別，你可以選怎樣儲存文字區塊 (block)：
    - `'none'`：不儲存。
    - `'separate'`：每個文字區塊（例如一個標題、一段內文）存成一個獨立的 `.txt` 檔案。
    - `'single'`：將整張圖所有文字區塊，順序放入**一個** `.txt` 檔案。
- **適合場景**：
  - 想深入分析一張圖的版面結構。
  - 只是想要純文字，或者只是想要 JSON。
  - 做實驗，看一下不同設定的輸出效果。
- **如何使用**：執行前，先打開檔案，修改上面那些開關，然後 `uv run python All_res_Ocr.py`。

---

### 📜 `Batch_PDF_Processor.py` - PDF 命令行處理器

這個腳本是專為喜歡用命令行的朋友而設，用來處理 PDF。

- **功能**：它會掃描 `pdfs/` 資料夾裡面所有的 PDF。之後，它會模仿我們在 Terminal 手動打指令的方式，為每個 PDF 執行 `paddleocr doc_parser` 這個 command。每個 PDF 的處理結果會放在 `output_cli/` 裡面一個同名的子資料夾。
- **適合場景**：
  - 習慣用 command-line tool。
  - 想將 OCR 功能整合到你現有的 Shell script 或自動化流程裡面。
- **如何使用**：將 PDF 放入 `pdfs/`，然後執行 `uv run python Batch_PDF_Processor.py`。

---

### 👑 `Batch_Pdf_Ocr.py` - PDF 處理

這是處理 PDF 的腳本。

- **功能**：同上一個腳本一樣，它也是處理 `pdfs/` 裡面的所有 PDF。但它不是用命令行，而是直接用 Python library，這樣可以做到更加精細的控制。它會：
  1.  逐個 PDF 檔案讀取。
  2.  再**逐頁**進行分析。
  3.  為每一頁，你可以像 `All_res_Ocr.py` 那樣，自由選擇要不要儲存 **JSON**、**Markdown**，以及怎樣儲存**文字區塊** (`BLOCK_TEXT_SAVE_MODE`)。
  4.  結果會很有條理地存放在 `output_pdfs/`，每個 PDF 一個資料夾，裡面再每頁一個子資料夾。
- **適合場景**：
  - 需要對 PDF 的每一頁做詳細分析。
  - 想拿到最完整、最有彈性的輸出結果。
- **如何使用**：打開檔案改好設定，將 PDF 放入 `pdfs/`，然後 `uv run python Batch_Pdf_Ocr.py`。

---

## 總結

希望這份手寫筆記風的教學幫到你啦！
