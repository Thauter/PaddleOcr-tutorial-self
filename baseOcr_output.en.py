from paddleocr import PaddleOCRVL

# Configure to use the vLLM server
pipeline = PaddleOCRVL(
    vl_rec_backend="vllm-server",
    vl_rec_server_url="http://localhost:8111/v1"
)

result = pipeline.predict("images/2501.10973.png")
for res in result:
    res.print()

