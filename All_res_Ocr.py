import os
from paddleocr import PaddleOCRVL

# --- 1. 功能開關 (可以喺呢度選擇) ---
SAVE_JSON = True         # True = 儲存整合嘅 JSON
SAVE_MARKDOWN = True     # True = 儲存整合嘅 Markdown

# --- Block Text 儲存模式 ---
# 'none'     = 唔儲存
# 'separate' = 每個 block 存成獨立 .txt 檔案
# 'single'   = 所有 block 儲存到一個 .txt 檔案
BLOCK_TEXT_SAVE_MODE = 'single' 

# --- 2. 配置 & 初始化 ---
# 確保輸出目錄存在
if SAVE_JSON or SAVE_MARKDOWN or BLOCK_TEXT_SAVE_MODE == 'single':
    os.makedirs("output_data", exist_ok=True)
if BLOCK_TEXT_SAVE_MODE == 'separate':
    os.makedirs("output_blocks_data", exist_ok=True)


# 自定義配置
pipeline = PaddleOCRVL(
    use_doc_orientation_classify=True,  # 啟用方向分類
    use_doc_unwarping=True,            # 啟用圖像矯正
    use_layout_detection=True,     # 啟用版面檢測
    vl_rec_backend="vllm-server",
    vl_rec_server_url="http://localhost:8111/v1"
)

# 處理圖片
result = pipeline.predict("images/2501.10973.png")

for res in result:
    # 修正 NameError: 喺呢度定義返 base_name
    image_basename = os.path.basename(res['input_path'])
    base_name, _ = os.path.splitext(image_basename)

    # 顯示關於成張圖片嘅整體資訊
    print(f"--- 處理緊圖片：{res['input_path']} ---")
    print(f"圖像旋轉角度：{res['doc_preprocessor_res']['angle']}")
    print("=" * 50)
    
  
    
    # res 物件本身就係包含結果嘅 dictionary
    parsing_res = res['parsing_res_list']
    
    # 根據儲存模式，處理 block 嘅文字資訊
    if BLOCK_TEXT_SAVE_MODE == 'single':
        single_txt_path = os.path.join("output_data", f"{base_name}_all_blocks.txt")
        with open(single_txt_path, "w", encoding="utf-8") as f:
            print("--- 開始逐個區塊處理 ---")
            f.write(f"--- 圖片 {image_basename} 的所有內容區塊 ---\n\n")
            for i, block in enumerate(parsing_res):
                # 喺 Terminal 印出
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
        print(f"\n[✓] 已將所有 Block 合併儲存到: {single_txt_path}")

    elif BLOCK_TEXT_SAVE_MODE == 'separate':
        print("--- 開始逐個區塊處理 ---")
        for i, block in enumerate(parsing_res):
            print(f"標籤：{block.label}")
            print(f"內容：{block.content}")
            print(f"位置：{block.bbox}")
            print("-" * 50)
            # 儲存成獨立檔案
            block_filename = f"{base_name}_block_{i:02d}_{block.label}.txt"
            block_save_path = os.path.join("output_blocks_data", block_filename)
            with open(block_save_path, "w", encoding="utf-8") as f:
                f.write(f"標籤: {block.label}\n")
                f.write(f"位置: {block.bbox}\n")
                f.write("-" * 20 + "\n")
                f.write(block.content)
        print(f"\n[✓] 已將每個 Block 分別儲存到 'output_blocks_data' 資料夾")
    
    else: # mode == 'none'
        print("--- Block 文字儲存功能已關閉 ---")


    # 根據開關，決定係咪儲存 JSON 同 Markdown 檔案
    if SAVE_JSON:
        res.save_to_json(save_path="output_data")
        print(f"\n[✓] 已將完整 JSON 結果儲存到 'output_data' 資料夾")
    
    if SAVE_MARKDOWN:
        res.save_to_markdown(save_path="output_data")
        print(f"\n[✓] 已將完整 Markdown 結果儲存到 'output_data' 資料夾")
    
    print("=" * 50)

