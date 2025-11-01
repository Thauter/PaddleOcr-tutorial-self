from paddleocr import PaddleOCRVL
import os

pipeline = PaddleOCRVL(
    vl_rec_backend="vllm-server",
    vl_rec_server_url="http://localhost:8111/v1"
)




# 處理目錄中的所有圖片
image_dir = "images/"
output_dir = "output2/"

for filename in os.listdir(image_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(image_dir, filename)
        print(f"處理：{image_path}")
        
        result = pipeline.predict(image_path)
        for res in result:
            res.save_to_markdown(output_dir)
            res.save_to_json(output_dir)
