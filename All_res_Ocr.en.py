import os
from paddleocr import PaddleOCRVL

# --- 1. Feature Switches (Select here) ---
SAVE_JSON = True         # True = Save the consolidated JSON
SAVE_MARKDOWN = True     # True = Save the consolidated Markdown

# --- Block Text Saving Mode ---
# 'none'     = Do not save
# 'separate' = Save each block as a separate .txt file
# 'single'   = Save all blocks to a single .txt file
BLOCK_TEXT_SAVE_MODE = 'single' 

# --- 2. Configuration & Initialization ---
# Ensure output directories exist
if SAVE_JSON or SAVE_MARKDOWN or BLOCK_TEXT_SAVE_MODE == 'single':
    os.makedirs("output_data", exist_ok=True)
if BLOCK_TEXT_SAVE_MODE == 'separate':
    os.makedirs("output_blocks_data", exist_ok=True)


# Custom configuration
pipeline = PaddleOCRVL(
    use_doc_orientation_classify=True,  # Enable orientation classification
    use_doc_unwarping=True,            # Enable image unwarping
    use_layout_detection=True,         # Enable layout detection
    vl_rec_backend="vllm-server",
    vl_rec_server_url="http://localhost:8111/v1"
)

# Process the image
result = pipeline.predict("images/2501.10973.png")

for res in result:
    # Fix NameError: Define base_name here
    image_basename = os.path.basename(res['input_path'])
    base_name, _ = os.path.splitext(image_basename)

    # Display overall information about the image
    print(f"--- Processing image: {res['input_path']} ---")
    print(f"Image rotation angle: {res['doc_preprocessor_res']['angle']}")
    print("=" * 50)
    
    # The 'res' object itself is a dictionary containing the results
    parsing_res = res['parsing_res_list']
    
    # Process block text information based on the save mode
    if BLOCK_TEXT_SAVE_MODE == 'single':
        single_txt_path = os.path.join("output_data", f"{base_name}_all_blocks.txt")
        with open(single_txt_path, "w", encoding="utf-8") as f:
            print("--- Starting to process blocks one by one ---")
            f.write(f"--- All content blocks for image {image_basename} ---\n\n")
            for i, block in enumerate(parsing_res):
                # Print to terminal
                print(f"Label: {block.label}")
                print(f"Content: {block.content}")
                print(f"Position: {block.bbox}")
                print("-" * 50)
                # Write to the single file
                f.write(f"--- Block {i+1}: {block.label} ---\n")
                f.write(f"Position: {block.bbox}\n")
                f.write("-" * 20 + "\n")
                f.write(block.content)
                f.write("\n\n")
        print(f"\n[✓] All blocks have been merged and saved to: {single_txt_path}")

    elif BLOCK_TEXT_SAVE_MODE == 'separate':
        print("--- Starting to process blocks one by one ---")
        for i, block in enumerate(parsing_res):
            print(f"Label: {block.label}")
            print(f"Content: {block.content}")
            print(f"Position: {block.bbox}")
            print("-" * 50)
            # Save as a separate file
            block_filename = f"{base_name}_block_{i:02d}_{block.label}.txt"
            block_save_path = os.path.join("output_blocks_data", block_filename)
            with open(block_save_path, "w", encoding="utf-8") as f:
                f.write(f"Label: {block.label}\n")
                f.write(f"Position: {block.bbox}\n")
                f.write("-" * 20 + "\n")
                f.write(block.content)
        print(f"\n[✓] Each block has been saved separately to the 'output_blocks_data' folder")
    
    else: # mode == 'none'
        print("--- Block text saving is disabled ---")


    # Decide whether to save JSON and Markdown files based on the switches
    if SAVE_JSON:
        res.save_to_json(save_path="output_data")
        print(f"\n[✓] Full JSON result has been saved to the 'output_data' folder")
    
    if SAVE_MARKDOWN:
        res.save_to_markdown(save_path="output_data")
        print(f"\n[✓] Full Markdown result has been saved to the 'output_data' folder")
    
    print("=" * 50)

