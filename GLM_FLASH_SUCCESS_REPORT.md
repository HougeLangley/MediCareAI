# MediCare AI - GLM-4.7-Flash 本地部署指南 / Local Deployment Guide

> **重要提示 | Important Notice:**
> 
> 本文档为指导性文档，用户需要根据自身环境配置本地 AI 大模型和 MinerU 服务。
> 
> This is a guidance document. Users need to configure their own local AI models and MinerU services according to their environment.

---

## 🎯 概述 | Overview

MediCare AI 支持接入本地部署的大语言模型（LLM）和 MinerU 文档处理服务，确保数据隐私和安全。

MediCare AI supports integration with locally deployed Large Language Models (LLM) and MinerU document processing services, ensuring data privacy and security.

---

## 🤖 本地 AI 大模型部署选项 | Local AI Model Deployment Options

### 1. Ollama（推荐新手）| Ollama (Recommended for Beginners)

**简介 | Introduction:**
Ollama 是目前最简单易用的本地大模型运行工具，支持 macOS、Linux 和 Windows。

Ollama is the easiest-to-use local LLM running tool, supporting macOS, Linux, and Windows.

**安装步骤 | Installation:**

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# 或者使用 Homebrew (macOS)
brew install ollama

# Windows: 下载安装包从 https://ollama.com/download
```

**运行 GLM-4.7-Flash | Run GLM-4.7-Flash:**

```bash
# 拉取模型
ollama pull unsloth/glm-4.7b

# 运行服务
ollama serve

# 默认监听: http://localhost:11434
```

**配置 MediCare AI | Configure MediCare AI:**

在 `.env` 文件中设置：

```bash
AI_API_KEY=ollama
AI_API_URL=http://localhost:11434/v1/
AI_MODEL_ID=unsloth/glm-4.7b
```

**参考文档 | Reference:**
- 官网: https://ollama.com
- GitHub: https://github.com/ollama/ollama
- 模型库: https://ollama.com/library

---

### 2. llama.cpp（推荐高级用户）| llama.cpp (Recommended for Advanced Users)

**简介 | Introduction:**
llama.cpp 是一个高性能的 LLM 推理库，使用 C/C++ 编写，支持多种量化格式。

llama.cpp is a high-performance LLM inference library written in C/C++, supporting various quantization formats.

**安装步骤 | Installation:**

```bash
# 克隆仓库
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# 编译（CPU 版本）
make

# 编译（CUDA GPU 版本）
make GGML_CUDA=1

# 编译（Metal macOS 版本）
make GGML_METAL=1
```

**下载 GLM-4.7-Flash 模型 | Download Model:**

```bash
# 从 HuggingFace 下载 GGUF 格式模型
# 推荐: unsloth/GLM-4.7-Flash-GGUF

# 创建模型目录
mkdir -p models
cd models

# 下载模型（使用 huggingface-cli）
pip install huggingface-hub
huggingface-cli download unsloth/GLM-4.7-Flash-GGUF --local-dir ./glm-4.7-flash
```

**启动服务器 | Start Server:**

```bash
# 启动 llama.cpp 服务器
./server \
  -m models/glm-4.7-flash/GLM-4.7-Flash-Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8033 \
  -c 4096 \
  -n 2048

# 参数说明:
# -m: 模型路径
# --host: 监听地址
# --port: 监听端口
# -c: 上下文长度
# -n: 最大生成token数
```

**配置 MediCare AI | Configure MediCare AI:**

```bash
AI_API_KEY=your_api_key
AI_API_URL=http://localhost:8033/v1/
AI_MODEL_ID=unsloth/GLM-4.7-Flash-GGUF:BF16
```

**参考文档 | Reference:**
- GitHub: https://github.com/ggerganov/llama.cpp
- 文档: https://github.com/ggerganov/llama.cpp/blob/master/docs

---

### 3. vLLM（推荐生产环境）| vLLM (Recommended for Production)

**简介 | Introduction:**
vLLM 是一个高吞吐量、低延迟的 LLM 推理和服务引擎，支持 PagedAttention 技术。

vLLM is a high-throughput, low-latency LLM inference and serving engine with PagedAttention technology.

**安装步骤 | Installation:**

```bash
# 创建虚拟环境
python -m venv vllm_env
source vllm_env/bin/activate

# 安装 vLLM
pip install vllm

# 或者使用 Docker
docker pull vllm/vllm-openai:latest
```

**启动服务 | Start Service:**

```bash
# 使用 Python
python -m vllm.entrypoints.openai.api_server \
  --model unsloth/glm-4.7b \
  --host 0.0.0.0 \
  --port 8000 \
  --tensor-parallel-size 1 \
  --max-num-seqs 256

# 或者使用 Docker
docker run --runtime nvidia --gpus all \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model unsloth/glm-4.7b
```

**配置 MediCare AI | Configure MediCare AI:**

```bash
AI_API_KEY=vllm
AI_API_URL=http://localhost:8000/v1/
AI_MODEL_ID=unsloth/glm-4.7b
```

**参考文档 | Reference:**
- GitHub: https://github.com/vllm-project/vllm
- 文档: https://docs.vllm.ai

---

### 4. SGLang（高性能推理）| SGLang (High-Performance Inference)

**简介 | Introduction:**
SGLang 是一个用于大型语言模型的结构化生成语言，提供高性能推理。

SGLang is a structured generation language for large language models, providing high-performance inference.

**安装步骤 | Installation:**

```bash
pip install sglang

# 安装所有依赖
pip install sglang[all]
```

**启动服务 | Start Service:**

```bash
python -m sglang.launch_server \
  --model-path unsloth/glm-4.7b \
  --host 0.0.0.0 \
  --port 30000
```

**配置 MediCare AI | Configure MediCare AI:**

```bash
AI_API_KEY=sglang
AI_API_URL=http://localhost:30000/v1/
AI_MODEL_ID=unsloth/glm-4.7b
```

**参考文档 | Reference:**
- GitHub: https://github.com/sgl-project/sglang
- 文档: https://sglang.readthedocs.io

---

### 5. Text Generation Inference (HuggingFace) | TGI

**简介 | Introduction:**
HuggingFace 开发的用于部署和服务 LLM 的生产就绪工具包。

A toolkit for deploying and serving LLMs developed by HuggingFace.

**使用 Docker 部署 | Deploy with Docker:**

```bash
docker run --gpus all --shm-size 1g -p 8080:80 \
  -v ~/.cache/huggingface:/data \
  ghcr.io/huggingface/text-generation-inference:2.0.0 \
  --model-id unsloth/glm-4.7b \
  --quantize eetq
```

**配置 MediCare AI | Configure MediCare AI:**

```bash
AI_API_KEY=tgi
AI_API_URL=http://localhost:8080/v1/
AI_MODEL_ID=unsloth/glm-4.7b
```

**参考文档 | Reference:**
- GitHub: https://github.com/huggingface/text-generation-inference

---

## 📄 本地 MinerU 文档处理部署 | Local MinerU Document Processing

### 简介 | Introduction

MinerU 是一个强大的文档内容提取工具，可以将 PDF、图片等格式的文档转换为结构化的 Markdown 或 JSON 格式。

MinerU is a powerful document content extraction tool that can convert documents in PDF, image, and other formats into structured Markdown or JSON formats.

### 安装步骤 | Installation

#### 1. 环境要求 | Requirements

```bash
# Python 3.10+
python --version

# 安装系统依赖 (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
  libgl1-mesa-glx \
  libglib2.0-0 \
  libsm6 \
  libxext6 \
  libxrender-dev \
  libgomp1
```

#### 2. 安装 MinerU | Install MinerU

```bash
# 创建虚拟环境
conda create -n mineru python=3.10
conda activate mineru

# 安装 Magic-PDF（包含 MinerU）
pip install magic-pdf[full] --extra-index-url https://wheels.myhloli.com

# 或者使用源码安装
git clone https://github.com/opendatalab/MinerU.git
cd MinerU
pip install -r requirements.txt
pip install -e .
```

#### 3. 下载模型 | Download Models

```bash
# 安装模型下载工具
pip install huggingface-hub

# 下载模型权重
huggingface-cli download opendatalab/PDF-Extract-Kit-1.0 --local-dir ./models/PDF-Extract-Kit-1.0

# 或者从 ModelScope 下载
# pip install modelscope
# python scripts/download_models.py
```

#### 4. 配置文件 | Configuration

创建配置文件 `magic-pdf.json`：

```json
{
  "models_dir": "/path/to/models",
  "device_mode": "cuda",
  "table_config": {
    "model": "tablemaster",
    "enable": true
  }
}
```

#### 5. 启动服务 | Start Service

**命令行使用 | Command Line:**

```bash
# 处理单个 PDF
magic-pdf pdf-document --input /path/to/document.pdf --output /path/to/output

# 批量处理
magic-pdf pdf-directory --input /path/to/pdfs/ --output /path/to/output
```

**API 服务（需要自行封装）| API Service (needs wrapper):**

由于 MinerU 主要提供命令行工具，您可以创建一个简单的 FastAPI 包装器：

```python
# mineru_service.py
from fastapi import FastAPI, File, UploadFile
import subprocess
import tempfile
import os

app = FastAPI()

@app.post("/extract")
async def extract_document(file: UploadFile = File(...)):
    # 保存上传的文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    # 调用 MinerU 处理
    output_dir = tempfile.mkdtemp()
    subprocess.run([
        "magic-pdf", "pdf-document",
        "--input", tmp_path,
        "--output", output_dir
    ])
    
    # 读取结果
    result_file = os.path.join(output_dir, "document.md")
    with open(result_file, 'r') as f:
        content = f.read()
    
    # 清理临时文件
    os.unlink(tmp_path)
    
    return {"extracted_text": content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

**Docker 部署 | Docker Deployment:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 安装 MinerU
RUN pip install magic-pdf[full] --extra-index-url https://wheels.myhloli.com

# 复制模型（需要提前下载）
COPY models /app/models

# 配置文件
COPY magic-pdf.json /app/magic-pdf.json

# 启动脚本
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8001

CMD ["/app/start.sh"]
```

### 配置 MediCare AI | Configure MediCare AI

```bash
# MinerU API 配置
MINERU_TOKEN=your_mineru_token_or_local_key
MINERU_API_URL=http://localhost:8001/extract
```

### 参考文档 | Reference

- **GitHub**: https://github.com/opendatalab/MinerU
- **中文文档**: https://github.com/opendatalab/MinerU/blob/master/README_zh-CN.md
- **英文文档**: https://github.com/opendatalab/MinerU/blob/master/README.md
- **在线演示**: https://opendatalab.com/OpenSourceTools

---

## 🔧 系统配置示例 | System Configuration Example

### 完整的 .env 配置 | Complete .env Configuration

```bash
# ============================================
# AI 大模型配置 | AI Model Configuration
# 根据您的部署方式选择对应的配置
# ============================================

# 选项 1: Ollama
AI_API_KEY=ollama
AI_API_URL=http://localhost:11434/v1/
AI_MODEL_ID=unsloth/glm-4.7b

# 选项 2: llama.cpp
# AI_API_KEY=llamacpp
# AI_API_URL=http://localhost:8033/v1/
# AI_MODEL_ID=unsloth/GLM-4.7-Flash-GGUF:BF16

# 选项 3: vLLM
# AI_API_KEY=vllm
# AI_API_URL=http://localhost:8000/v1/
# AI_MODEL_ID=unsloth/glm-4.7b

# ============================================
# MinerU 配置 | MinerU Configuration
# ============================================

# 如果使用官方 API（不推荐用于生产环境）
# MINERU_TOKEN=your_official_token

# 如果使用本地部署
MINERU_TOKEN=local_mineru_key
MINERU_API_URL=http://localhost:8001/extract

# ============================================
# 数据库配置 | Database Configuration
# ============================================
POSTGRES_PASSWORD=your_secure_password
REDIS_PASSWORD=your_secure_password

# ============================================
# JWT 配置 | JWT Configuration
# ============================================
JWT_SECRET_KEY=your_random_secret_key_min_32_chars
```

---

## ✅ 验证部署 | Verify Deployment

### 测试 AI 服务 | Test AI Service

```bash
# 测试健康检查
curl http://localhost:11434/api/tags

# 测试对话（Ollama）
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "unsloth/glm-4.7b",
    "prompt": "你好，请介绍一下自己",
    "stream": false
  }'

# 测试 OpenAI 兼容接口
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "unsloth/glm-4.7b",
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

### 测试 MinerU | Test MinerU

```bash
# 下载测试文档
wget https://example.com/test-document.pdf -O test.pdf

# 使用 MinerU 处理
magic-pdf pdf-document --input test.pdf --output ./output

# 检查结果
ls ./output/
cat ./output/document.md
```

---

## 🚀 快速启动检查清单 | Quick Start Checklist

部署 MediCare AI 前，请确保：

- [ ] **AI 模型服务已启动并运行正常**
  - [ ] 可以通过 HTTP 访问 API
  - [ ] 模型已正确加载
  - [ ] 响应时间可接受（< 30秒）

- [ ] **MinerU 服务已配置**
  - [ ] 命令行工具安装成功
  - [ ] 模型文件已下载
  - [ ] 可以成功提取 PDF 文本

- [ ] **环境变量已正确配置**
  - [ ] AI_API_URL 指向正确的地址
  - [ ] MINERU_TOKEN 已设置
  - [ ] 数据库密码已设置（如果使用远程数据库）

- [ ] **Docker 服务已启动**
  - [ ] PostgreSQL 容器运行中
  - [ ] Redis 容器运行中（可选）
  - [ ] MediCare AI 后端可以连接数据库

---

## 📚 更多资源 | Additional Resources

### AI 模型资源 | AI Model Resources
- **HuggingFace**: https://huggingface.co/models
- **ModelScope**: https://modelscope.cn
- **OpenXLab**: https://openxlab.org.cn

### 模型推荐 | Model Recommendations
- **GLM-4.7-Flash**: 适合中文医疗场景，推理速度快
- **Qwen2.5-7B**: 阿里巴巴开源模型，中文表现优秀
- **Baichuan2-7B**: 百川智能开源模型，医疗领域表现良好
- **Llama-3-8B**: Meta 开源模型，英文表现优秀

### 硬件要求 | Hardware Requirements

| 模型大小 | 显存要求 | 推荐 GPU | 说明 |
|---------|---------|---------|------|
| 4B-7B | 8-12GB | RTX 3060/4060 | 适合个人使用 |
| 7B-13B | 16-24GB | RTX 3090/4090 | 高性能推理 |
| 70B+ | 多卡或 A100 | 专业 GPU | 企业级部署 |

---

## 🆘 故障排除 | Troubleshooting

### AI 服务连接失败 | AI Service Connection Failed

```bash
# 检查服务是否运行
netstat -tlnp | grep <port>

# 检查防火墙设置
sudo ufw allow <port>/tcp

# 测试本地连接
curl -v http://localhost:<port>/health
```

### MinerU 处理失败 | MinerU Processing Failed

```bash
# 检查依赖安装
pip list | grep magic-pdf

# 检查模型文件
ls -la ~/.cache/huggingface/

# 查看详细日志
magic-pdf pdf-document --input test.pdf --output ./output --debug
```

### 内存不足 | Out of Memory

```bash
# 使用量化模型（减小显存占用）
# Q4_K_M 量化级别可以在保持质量的同时减少 75% 的显存使用

# 减少上下文长度
# 在 llama.cpp 中使用 -c 2048 而不是默认的 4096

# 启用交换分区
sudo swapon -a
```

---

**注意 | Note:**
所有 IP 地址、API Key 和敏感信息都需要根据您的实际环境进行配置。请勿使用文档中的示例值作为生产环境配置。

All IP addresses, API keys, and sensitive information need to be configured according to your actual environment. Do not use example values from this document as production configurations.

---

**最后更新 | Last Updated:** 2025-02-01  
**版本 | Version:** 2.0.0 - 本地部署指南版
