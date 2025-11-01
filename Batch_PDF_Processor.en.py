import os
import subprocess

# ==============================================================================
# --- 1. Settings Area (Modify your configuration here) ---
# ==============================================================================

# --- Input / Output Paths ---
# Place all the PDF files you want to process in this folder
PDF_INPUT_DIR = "pdfs/"      
# All processed results will be stored in this base folder
OUTPUT_BASE_DIR = "output_cli/" 

# --- vLLM Server Configuration ---
# Ensure this URL matches the URL of your running vllm-server
VLLM_SERVER_URL = "http://localhost:8111/v1"

# ==============================================================================
# --- 2. Batch Process All PDF Files ---
# ==============================================================================

# Ensure both input and output directories exist
if not os.path.exists(PDF_INPUT_DIR):
    print(f"!!! Error: Input folder '{PDF_INPUT_DIR}' does not exist. Please create it and place your PDF files inside.")
    exit()
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)


print("--- Starting batch processing of PDFs ---")

# Iterate over all files in the input directory
for filename in os.listdir(PDF_INPUT_DIR):
    if filename.lower().endswith('.pdf'):
        pdf_path = os.path.join(PDF_INPUT_DIR, filename)
        pdf_basename = os.path.splitext(filename)[0]
        
        # Create a separate output subdirectory for each PDF file to avoid mixing up results
        # For example, processing "doc1.pdf" will save results to "output_cli/doc1/"
        pdf_output_path = os.path.join(OUTPUT_BASE_DIR, pdf_basename)
        
        print(f"\n{'='*20} Now processing: {filename} {'='*20}")
        print(f"Results will be saved to: {pdf_output_path}")

        # --- Build and execute the paddleocr command-line instruction ---
        command = [
            "uv", "run", "paddleocr", "doc_parser",
            "-i", pdf_path,
            "--save_path", pdf_output_path,
            "--vl_rec_backend", "vllm-server",
            "--vl_rec_server_url", VLLM_SERVER_URL
        ]
        
        try:
            # Execute the command and wait for it to complete
            # We will display the live output from the CLI so you can see the progress
            subprocess.run(
                command, 
                check=True       # If the command returns a non-zero exit code, an exception will be raised
            )
            print(f"[✓] Successfully processed: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"!!! An error occurred while processing file '{filename}' !!!")
            print(f"Error message: {e}")
        except KeyboardInterrupt:
            print("\n--- User interruption received, stopping batch process ---")
            exit()
        except Exception as e:
            print(f"!!! An unknown error occurred: {e} !!!")


print(f"\n{'='*20} All PDF batch processing complete {'='*20}")

