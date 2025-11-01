import os
import subprocess

# ==============================================================================
# --- 1. 設定區 (請喺呢度修改你嘅配置) ---
# ==============================================================================

# --- 輸入 / 輸出路徑 ---
# 將你所有想處理嘅 PDF 檔案，放喺呢個資料夾入面
PDF_INPUT_DIR = "pdfs/"      
# 所有處理完嘅結果，都會存放喺呢個基底資料夾入面
OUTPUT_BASE_DIR = "output_cli/" 

# --- vLLM Server 配置 ---
# 確保呢個 URL同你啟動 vllm-server 時嘅 URL 一致
VLLM_SERVER_URL = "http://localhost:8111/v1"

# ==============================================================================
# --- 2. 批次處理所有 PDF 檔案 ---
# ==============================================================================

# 確保輸入同輸出資料夾都存在
if not os.path.exists(PDF_INPUT_DIR):
    print(f"!!! 錯誤: 輸入資料夾 '{PDF_INPUT_DIR}' 不存在。請創建並放入 PDF 檔案。")
    exit()
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)


print("--- 開始批次處理 PDF ---")

# 遍歷輸入資料夾入面所有檔案
for filename in os.listdir(PDF_INPUT_DIR):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(PDF_INPUT_DIR, filename)
        pdf_basename = os.path.splitext(filename)[0]
        
        # 為每一個 PDF 檔案，創建一個獨立嘅輸出子資料夾，避免結果撈亂
        # 例如，處理 "doc1.pdf"，結果會放喺 "output_cli/doc1/"
        pdf_output_path = os.path.join(OUTPUT_BASE_DIR, pdf_basename)
        
        print(f"\n{'='*20} 正在處理: {filename} {'='*20}")
        print(f"結果將會儲存到: {pdf_output_path}")

        # --- 構建並執行 paddleocr 命令行指令 ---
        command = [
            "uv", "run", "paddleocr", "doc_parser",
            "-i", pdf_path,
            "--save_path", pdf_output_path,
            "--vl_rec_backend", "vllm-server",
            "--vl_rec_server_url", VLLM_SERVER_URL
        ]
        
        try:
            # 執行指令，並且等待佢完成
            # 我哋會顯示 CLI 嘅即時輸出，等你可以睇到進度
            subprocess.run(
                command, 
                check=True       # 如果指令出錯 (return code唔係0)，就會拋出例外
            )
            print(f"[✓] 成功處理完: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"!!! 處理檔案 '{filename}' 嗰陣發生錯誤 !!!")
            print(f"錯誤訊息: {e}")
        except KeyboardInterrupt:
            print("\n--- 收到使用者中斷指令，正在停止批次處理 ---")
            exit()
        except Exception as e:
            print(f"!!! 發生未知錯誤: {e} !!!")


print(f"\n{'='*20} 所有 PDF 批次處理完成 {'='*20}")

