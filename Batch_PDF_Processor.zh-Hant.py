import os
import subprocess

# ==============================================================================
# --- 1. 設定區 (請在此處修改您的設定) ---
# ==============================================================================

# --- 輸入 / 輸出路徑 ---
# 將您所有想處理的 PDF 檔案，放置於此資料夾內
PDF_INPUT_DIR = "pdfs/"      
# 所有處理完成的結果，將存放於此基底資料夾內
OUTPUT_BASE_DIR = "output_cli/" 

# --- vLLM Server 設定 ---
# 確保此 URL 與您啟動 vllm-server 時的 URL 一致
VLLM_SERVER_URL = "http://localhost:8111/v1"

# ==============================================================================
# --- 2. 批次處理所有 PDF 檔案 ---
# ==============================================================================

# 確保輸入與輸出資料夾均存在
if not os.path.exists(PDF_INPUT_DIR):
    print(f"!!! 錯誤: 輸入資料夾 '{PDF_INPUT_DIR}' 不存在。請建立該資料夾並放入 PDF 檔案。")
    exit()
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)


print("--- 開始批次處理 PDF ---")

# 遍歷輸入資料夾中的所有檔案
for filename in os.listdir(PDF_INPUT_DIR):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(PDF_INPUT_DIR, filename)
        pdf_basename = os.path.splitext(filename)[0]
        
        # 為每一個 PDF 檔案，建立一個獨立的輸出子資料夾，以避免結果混淆
        # 例如，處理 "doc1.pdf"，結果將存放於 "output_cli/doc1/"
        pdf_output_path = os.path.join(OUTPUT_BASE_DIR, pdf_basename)
        
        print(f"\n{'='*20} 正在處理: {filename} {'='*20}")
        print(f"結果將儲存至: {pdf_output_path}")

        # --- 建構並執行 paddleocr 命令列指令 ---
        command = [
            "uv", "run", "paddleocr", "doc_parser",
            "-i", pdf_path,
            "--save_path", pdf_output_path,
            "--vl_rec_backend", "vllm-server",
            "--vl_rec_server_url", VLLM_SERVER_URL
        ]
        
        try:
            # 執行指令，並等待其完成
            # 我們會顯示 CLI 的即時輸出，以便您查看進度
            subprocess.run(
                command, 
                check=True       # 若指令出錯 (return code 非 0)，將會拋出例外
            )
            print(f"[✓] 成功處理完成: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"!!! 處理檔案 '{filename}' 時發生錯誤 !!!")
            print(f"錯誤訊息: {e}")
        except KeyboardInterrupt:
            print("\n--- 收到使用者中斷指令，正在停止批次處理 ---")
            exit()
        except Exception as e:
            print(f"!!! 發生未知錯誤: {e} !!!")


print(f"\n{'='*20} 所有 PDF 批次處理完成 {'='*20}")

