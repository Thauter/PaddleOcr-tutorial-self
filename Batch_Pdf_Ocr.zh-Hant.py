import os
from paddleocr import PaddleOCRVL

# ==============================================================================
# --- 1. 設定區 (請在此處修改您的設定) ---
# ==============================================================================

# --- 輸入 / 輸出路徑 ---
PDF_INPUT_DIR = "pdfs/"      # 您 PDF 檔案存放的資料夾
OUTPUT_BASE_DIR = "output_pdfs/"  # 所有處理結果的基底資料夾

# --- 功能開關 ---
SAVE_JSON = True         # True = 儲存整合的 JSON
SAVE_MARKDOWN = True     # True = 儲存整合的 Markdown

# --- Block Text 儲存模式 ---
# 'none'     = 不儲存
# 'separate' = 每個區塊儲存為獨立的 .txt 檔案
# 'single'   = 所有區塊儲存至一個 .txt 檔案 (將存放於每一頁的資料夾內)
BLOCK_TEXT_SAVE_MODE = 'single'

# ==============================================================================
# --- 2. 初始化 PaddleOCR Pipeline ---
# ==============================================================================
print("--- 正在初始化 PaddleOCR Pipeline... ---")
pipeline = PaddleOCRVL(
    use_doc_orientation_classify=True,
    use_doc_unwarping=True,
    use_layout_detection=True,
    vl_rec_backend="vllm-server",
    vl_rec_server_url="http://localhost:8111/v1"
)
print("--- Pipeline 初始化完成 ---")

# ==============================================================================
# --- 3. 批次處理所有 PDF 檔案 ---
# ==============================================================================
# 確保輸入資料夾存在
if not os.path.exists(PDF_INPUT_DIR):
    print(f"!!! 錯誤: 輸入資料夾 '{PDF_INPUT_DIR}' 不存在。請建立並放入 PDF 檔案。")
    exit()

for filename in os.listdir(PDF_INPUT_DIR):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(PDF_INPUT_DIR, filename)
        pdf_basename = os.path.splitext(filename)[0]
        
        print(f"\n{'='*20} 正在處理 PDF: {filename} {'='*20}")
        
        # predict 方法可直接處理 PDF，並回傳一個包含每一頁結果的 list
        result_list = pipeline.predict(pdf_path)
        
        print(f"--- PDF '{filename}' 總共有 {len(result_list)} 頁 ---")

        # --- 逐頁處理並儲存結果 ---
        for res in result_list:
            page_num = res['page_index'] + 1
            print(f"\n  --- 正在處理第 {page_num} 頁 ---")

            # 為每一頁建立獨立的輸出資料夾
            page_output_dir = os.path.join(OUTPUT_BASE_DIR, pdf_basename, f"page_{page_num}")
            os.makedirs(page_output_dir, exist_ok=True)

            # 根據開關儲存 JSON
            if SAVE_JSON:
                res.save_to_json(save_path=page_output_dir)
                print(f"    [✓] 已儲存 JSON")

            # 根據開關儲存 Markdown
            if SAVE_MARKDOWN:
                res.save_to_markdown(save_path=page_output_dir)
                print(f"    [✓] 已儲存 Markdown")

            # 根據模式儲存 Block Texts
            parsing_res = res['parsing_res_list']
            if BLOCK_TEXT_SAVE_MODE == 'single':
                single_txt_path = os.path.join(page_output_dir, f"{pdf_basename}_page_{page_num}_all_blocks.txt")
                with open(single_txt_path, "w", encoding="utf-8") as f:
                    for i, block in enumerate(parsing_res):
                        f.write(f"--- 區塊 {i+1}: {block.label} ---\n")
                        f.write(f"位置: {block.bbox}\n")
                        f.write("-" * 20 + "\n")
                        f.write(block.content)
                        f.write("\n\n")
                print(f"    [✓] 已將所有 Block 合併儲存至單一 .txt 檔案")
            
            elif BLOCK_TEXT_SAVE_MODE == 'separate':
                blocks_data_dir = os.path.join(page_output_dir, "blocks_data")
                os.makedirs(blocks_data_dir, exist_ok=True)
                for i, block in enumerate(parsing_res):
                    block_filename = f"{pdf_basename}_p{page_num}_b{i:02d}_{block.label}.txt"
                    block_save_path = os.path.join(blocks_data_dir, block_filename)
                    with open(block_save_path, "w", encoding="utf-8") as f:
                        f.write(f"標籤: {block.label}\n")
                        f.write(f"位置: {block.bbox}\n")
                        f.write("-" * 20 + "\n")
                        f.write(block.content)
                print(f"    [✓] 已將每個 Block 分別儲存")

print(f"\n{'='*20} 所有 PDF 處理完成 {'='*20}")

