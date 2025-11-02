from paddleocr import PaddleOCRVL

# 配置使用 vLLM 服務器
pipeline = PaddleOCRVL(
    vl_rec_backend="vllm-server",
    vl_rec_server_url="http://localhost:8555/v1"
)

result = pipeline.predict("images/2501.10973.png")
for res in result:
    res.print()
