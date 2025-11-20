### 3. 使用推理加速框架提升 VLM 推理性能

默认配置下的推理性能未经过充分优化，可能无法满足实际生产需求。此步骤主要介绍如何使用vLLM和SGLang推理加速框架来提升PaddleOCR-VL的推理性能。

### 3.1 启动 VLM 推理服务

启动 VLM 推理服务有以下两种方式，任选一种即可：

• 方法一：使用官方 Docker 镜像启动服务。

• 方法二：通过 PaddleOCR CLI 手动安装依赖后启动服务。

#### 3.1.1 方法一：使用 Docker 镜像

PaddleOCR 提供了 Docker 镜像（镜像大小约为 13 GB），用于快速启动 vLLM 推理服务。可使用以下命令启动服务（要求 Docker 版本  $ \geq $  19.03，机器装配有 GPU 且 NVIDIA 驱动支持 CUDA 12.6 或以上版本）：

docker run \
-it \
--rm \
--gpus all \
--network host \
ccr-2vdh3abv-pub.cnc.bj.baidu.cce.com/paddle.paddle/paddle.ccr-genai-vllm-server::paddle.ccr-genai-server --model_name PaddleOCR-VL-0.9B --host 0.0.0.0 --port 81