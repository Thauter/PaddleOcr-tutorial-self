import os
from paddleocr import PaddleOCRVL

# ==============================================================================
# --- 1. Settings Area (Modify your configuration here) ---
# ==============================================================================

# --- Input / Output Paths ---
PDF_INPUT_DIR = "pdfs/"      # The folder where your PDF files are stored
OUTPUT_BASE_DIR = "output_pdfs/"  # The base folder for all processing results

# --- Feature Switches ---
SAVE_JSON = True         # True = Save the consolidated JSON
SAVE_MARKDOWN = True     # True = Save the consolidated Markdown

# --- Block Text Saving Mode ---
# 'none'     = Do not save
# 'separate' = Save each block as a separate .txt file
# 'single'   = Save all blocks to a single .txt file (will be inside each page's folder)
BLOCK_TEXT_SAVE_MODE = 'single'

# ==============================================================================
# --- 2. Initialize PaddleOCR Pipeline ---
# ==============================================================================
print("--- Initializing PaddleOCR Pipeline... ---")
pipeline = PaddleOCRVL(
    use_doc_orientation_classify=True,
    use_doc_unwarping=True,
    use_layout_detection=True,
    vl_rec_backend="vllm-server",
    vl_rec_server_url="http://localhost:8111/v1"
)
print("--- Pipeline initialization complete ---")

# ==============================================================================
# --- 3. Batch Process All PDF Files ---
# ==============================================================================
# Ensure the input folder exists
if not os.path.exists(PDF_INPUT_DIR):
    print(f"!!! Error: Input folder '{PDF_INPUT_DIR}' does not exist. Please create it and place your PDF files inside.")
    exit()

for filename in os.listdir(PDF_INPUT_DIR):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(PDF_INPUT_DIR, filename)
        pdf_basename = os.path.splitext(filename)[0]
        
        print(f"\n{'='*20} Now processing PDF: {filename} {'='*20}")
        
        # The predict method can directly handle a PDF and returns a list containing the results for each page
        result_list = pipeline.predict(pdf_path)
        
        print(f"--- PDF '{filename}' has a total of {len(result_list)} pages ---")

        # --- Process and save results page by page ---
        for res in result_list:
            page_num = res['page_index'] + 1
            print(f"\n  --- Processing page {page_num} ---")

            # Create a separate output folder for each page
            page_output_dir = os.path.join(OUTPUT_BASE_DIR, pdf_basename, f"page_{page_num}")
            os.makedirs(page_output_dir, exist_ok=True)

            # Save JSON based on the switch
            if SAVE_JSON:
                res.save_to_json(save_path=page_output_dir)
                print(f"    [✓] JSON saved")

            # Save Markdown based on the switch
            if SAVE_MARKDOWN:
                res.save_to_markdown(save_path=page_output_dir)
                print(f"    [✓] Markdown saved")

            # Save Block Texts based on the mode
            parsing_res = res['parsing_res_list']
            if BLOCK_TEXT_SAVE_MODE == 'single':
                single_txt_path = os.path.join(page_output_dir, f"{pdf_basename}_page_{page_num}_all_blocks.txt")
                with open(single_txt_path, "w", encoding="utf-8") as f:
                    for i, block in enumerate(parsing_res):
                        f.write(f"--- Block {i+1}: {block.label} ---\n")
                        f.write(f"Position: {block.bbox}\n")
                        f.write("-" * 20 + "\n")
                        f.write(block.content)
                        f.write("\n\n")
                print(f"    [✓] All blocks have been merged and saved to a single .txt file")
            
            elif BLOCK_TEXT_SAVE_MODE == 'separate':
                blocks_data_dir = os.path.join(page_output_dir, "blocks_data")
                os.makedirs(blocks_data_dir, exist_ok=True)
                for i, block in enumerate(parsing_res):
                    block_filename = f"{pdf_basename}_p{page_num}_b{i:02d}_{block.label}.txt"
                    block_save_path = os.path.join(blocks_data_dir, block_filename)
                    with open(block_save_path, "w", encoding="utf-8") as f:
                        f.write(f"Label: {block.label}\n")
                        f.write(f"Position: {block.bbox}\n")
                        f.write("-" * 20 + "\n")
                        f.write(block.content)
                print(f"    [✓] Each block has been saved separately")

print(f"\n{'='*20} All PDF processing complete {'='*20}")

