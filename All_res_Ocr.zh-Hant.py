import os
from paddleocr import PaddleOCRVL

# --- 1. 功能開關 (可在此處選擇) ---
SAVE_JSON = True         # True = 儲存整合的 JSON
SAVE_MARKDOWN = True     # True = 儲存整合的 Markdown

# --- Block Text 儲存模式 ---
# 'none'     = 不儲存
# 'separate' = 每個區塊儲存為獨立的 .txt 檔案
# 'single'   = 所有區塊儲存至一個 .txt 檔案
BLOCK_TEXT_SAVE_MODE = 'single' 

# --- 2. 設定 & 初始化 ---
# 確保輸出目錄存在
if SAVE_JSON or SAVE_MARKDOWN or BLOCK_TEXT_SAVE_MODE == 'single':
    os.makedirs("output_data", exist_ok=True)
if BLOCK_TEXT_SAVE_MODE == 'separate':
    os.makedirs("output_blocks_data", exist_ok=True)


# 自訂設定
pipeline = PaddleOCRVL(
    use_doc_orientation_classify=True,  # 啟用方向分類
    use_doc_unwarping=True,            # 啟用圖像校正
    use_layout_detection=True,         # 啟用版面偵測
    vl_rec_backend="vllm-server",
    vl_rec_server_url="http://localhost:8111/v1"
)

# 處理圖片
result = pipeline.predict("images/2501.10973.png")

for res in result:
    # 修正 NameError: 在此處定義 base_name
    image_basename = os.path.basename(res['input_path'])
    base_name, _ = os.path.splitext(image_basename)

    # 顯示關於整張圖片的整體資訊
    print(f"--- 正在處理圖片：{res['input_path']} ---")
    print(f"圖像旋轉角度：{res['doc_preprocessor_res']['angle']}")
    print("=" * 50)
    
    # res 物件本身即為包含結果的 dictionary
    parsing_res = res['parsing_res_list']
    
    # 根據儲存模式，處理區塊的文字資訊
    if BLOCK_TEXT_SAVE_MODE == 'single':
        single_txt_path = os.path.join("output_data", f"{base_name}_all_blocks.txt")
        with open(single_txt_path, "w", encoding="utf-8") as f:
            print("--- 開始逐一處理區塊 ---")
            f.write(f"--- 圖片 {image_basename} 的所有內容區塊 ---\n\n")
            for i, block in enumerate(parsing_res):
                # 在終端機印出
                print(f"標籤：{block.label}")
                print(f"內容：{block.content}")
                print(f"位置：{block.bbox}")
                print("-" * 50)
                # 寫入單一檔案
                f.write(f"--- 區塊 {i+1}: {block.label} ---\n")
                f.write(f"位置: {block.bbox}\n")
                f.write("-" * 20 + "\n")
                f.write(block.content)
                f.write("\n\n")
        print(f"\n[✓] 已將所有區塊合併儲存至: {single_txt_path}")

    elif BLOCK_TEXT_SAVE_MODE == 'separate':
        print("--- 開始逐一處理區塊 ---")
        for i, block in enumerate(parsing_res):
            print(f"標籤：{block.label}")
            print(f"內容：{block.content}")
            print(f"位置：{block.bbox}")
            print("-" * 50)
            # 儲存為獨立檔案
            block_filename = f"{base_name}_block_{i:02d}_{block.label}.txt"
            block_save_path = os.path.join("output_blocks_data", block_filename)
            with open(block_save_path, "w", encoding="utf-8") as f:
                f.write(f"標籤: {block.label}\n")
                f.write(f"位置: {block.bbox}\n")
                f.write("-" * 20 + "\n")
                f.write(block.content)
        print(f"\n[✓] 已將每個區塊分別儲存至 'output_blocks_data' 資料夾")
    
    else: # mode == 'none'
        print("--- 區塊文字儲存功能已關閉 ---")


    # 根據開關，決定是否儲存 JSON 與 Markdown 檔案
    if SAVE_JSON:
        res.save_to_json(save_path="output_data")
        print(f"\n[✓] 已將完整 JSON 結果儲存至 'output_data' 資料夾")
    
    if SAVE_MARKDOWN:
        res.save_to_markdown(save_path="output_data")
        print(f"\n[✓] 已將完整 Markdown 結果儲存至 'output_data' 資料夾")
    
    print("=" * 50)

