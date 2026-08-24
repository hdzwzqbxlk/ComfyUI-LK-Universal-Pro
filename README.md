# ComfyUI-LK-Universal-Pro

<div align="center">

![Version](https://img.shields.io/badge/Version-2.2.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Compatible-orange?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Google-Gemini_API-4285F4?style=for-the-badge&logo=google&logoColor=white)

**[English](#english) | [中文说明](#中文说明)**

</div>

---

<a name="english"></a>
## 📖 English

### Introduction
**ComfyUI-LK-Universal-Pro** is a comprehensive extension for ComfyUI, deeply integrated with Google's Gemini API ecosystem. It provides a robust set of nodes designed to unlock the full potential of multi-modal generative AI within the ComfyUI workflow.

This project goes beyond simple text generation, offering native support for image generation (Imagen 3, Nano Banana), video generation (Veo 3.1), advanced computer vision analysis, and structured outputs. It is designed for professionals who require precision, flexibility, and the latest capabilities of the Gemini models.

### 📁 Node Structure

All nodes are organized under `LK_Studio/` with platform-specific subfolders for future expansion:

```
LK_Studio/
└── Gemini/
    ├── 文本/          # Text generation nodes
    ├── 图像/          # Image generation nodes (incl. NanoBanana)
    ├── 视频/          # Video generation nodes
    ├── 视觉/          # Vision understanding nodes
    ├── 高级/          # Advanced feature nodes
    └── 工具/          # Utility nodes
```

### ✨ Key Features

*   **Advanced Text Generation**: Support for Gemini 1.5/2.5/3.0 Pro & Flash models, including "Thinking" mode for complex reasoning.
*   **Multi-Modal Generation**:
    *   **Image**: Native integration of Imagen 3 and Gemini image generation (Nano Banana).
    *   **Video**: Access to Veo 3.1 for high-quality text-to-video and image-to-video transfers.
*   **Computer Vision**: Deep visual analysis and document processing (PDF/Image) capabilities.
*   **Image-to-Prompt**: Reverse engineer prompts from images for style transfer.
*   **Workflow Control**: Structured JSON outputs, automatic prompt optimization, and multi-turn chat memory management.
*   **Utility Tools**: Centralized API key management and model information retrieval.

### 🧩 Node List

| Category | Node Name | Display Name | Description |
| :--- | :--- | :--- | :--- |
| **Text** | `LK_Gemini_Text` | 🌟 LK Gemini 文本生成 | Standard text generation with model selection. |
| | `LK_Gemini_Chat` | 💬 LK Gemini 多轮对话 | Multi-turn conversation with context history. |
| **Image** | `LK_Gemini_ImageGen` | 🎨 LK Gemini 图像生成 (Nano Banana) | Native Gemini image generation. |
| | `LK_Gemini_ImageEdit` | ✏️ LK Gemini 图像编辑 | Edit existing images via text instructions. |
| | `LK_Gemini_Imagen` | 🖼️ LK Imagen 图像生成 | High-fidelity generation using Imagen 3 models. |
| | `LK_NanoBanana` | 🍌 LK Nano Banana | Flash image generation (gemini-2.5-flash-image). |
| | `LK_NanoBananaPro` | 🍌 LK Nano Banana Pro | Pro image generation (gemini-3-pro-image-preview). |
| | `LK_NanoBananaMulti` | 🍌 LK Nano Banana 多图 | Multi-image blending & style transfer (up to 8 inputs). |
| | `LK_ImageToPrompt` | 🔄 LK 图像反推提示词 | Generate prompts from images for recreation. |
| **Video** | `LK_Gemini_VideoGen` | 🎬 LK Gemini 视频生成 (Veo 3.1) | Text-to-Video generation using Veo 3.1. |
| | `LK_Gemini_Image2Video` | 📹 LK Gemini 图生视频 | Transform source images into video sequences. |
| **Vision** | `LK_Gemini_VisionAnalyze`| 👁️ LK Gemini 视觉分析 | Analyze images for descriptions, tagging. |
| | `LK_Gemini_DocumentProcess` | 📄 LK Gemini 文档处理 | Extract and process text from Documents/PDFs. |
| **Advanced**| `LK_Gemini_StructuredOutput`| 📋 LK Gemini 结构化输出 | Enforce JSON output schemas. |
| | `LK_Gemini_PromptOptimizer` | 🔮 LK Gemini 提示词优化 | Optimize user prompts for better results. |
| | `LK_Gemini_Thinking` | 🧠 LK Gemini 深度思考 | Explicit reasoning step for complex queries. |
| **Utils** | `LK_Gemini_APIConfig` | ⚙️ LK Gemini API 配置 | Secure API Key configuration. |
| | `LK_Gemini_ModelInfo` | 📊 LK Gemini 模型信息 | List available models and capabilities. |
| | `LK_Gemini_PromptBuilder` | 🔧 LK 提示词构建器 | Helper tool to construct complex prompts. |

### 📦 Installation

1.  **Clone the Repository**
    ```bash
    cd ComfyUI/custom_nodes
    git clone https://github.com/hdzwzqbxlk/ComfyUI-LK-Universal-Pro.git
    ```

2.  **Install Dependencies**
    ```bash
    cd ComfyUI-LK-Universal-Pro
    pip install -r requirements.txt
    ```

3.  **Restart ComfyUI**

### 🔑 Configuration

1.  Obtain an API Key from [Google AI Studio](https://aistudio.google.com/).
2.  Configure in ComfyUI:
    *   **Direct Input**: Paste the key into the `api_key` widget on any node.
    *   **Environment Variable**: Set `GOOGLE_API_KEY` in your system environment.
    *   **Config Node**: Use the `⚙️ LK Gemini API 配置` node to manage keys centrally.

### 📄 License
This project is licensed under the [MIT License](LICENSE).

---

<a name="中文说明"></a>
## 📖 中文说明

### 项目简介
**ComfyUI-LK-Universal-Pro** 是一个为 ComfyUI 打造的全能型扩展插件，旨在深度集成 Google Gemini API 生态系统。该项目提供了一整套专业级节点，帮助用户在 ComfyUI 工作流中充分释放多模态生成式 AI 的潜力。

本项目支持 Imagen 3 图像生成、Nano Banana 图像生成、Veo 3.1 视频生成、高级计算机视觉分析以及结构化数据输出。

### 📁 节点结构

所有节点统一组织在 `LK_Studio/` 目录下，按平台分类，便于后期扩展：

```
LK_Studio/
└── Gemini/
    ├── 文本/          # 文本生成节点
    ├── 图像/          # 图像生成节点 (含 NanoBanana)
    ├── 视频/          # 视频生成节点
    ├── 视觉/          # 视觉理解节点
    ├── 高级/          # 高级功能节点
    └── 工具/          # 辅助工具节点
```

### ✨ 核心特性

*   **高级文本生成**: 支持 Gemini 1.5/2.5/3.0 Pro & Flash 全系模型，包含"深度思考"模式。
*   **多模态生成**:
    *   **图像**: 原生集成 Imagen 3 及 Gemini 图像生成 (Nano Banana)。
    *   **视频**: 接入 Veo 3.1 模型，支持文生视频及图生视频。
*   **视觉理解**: 深度图像语义分析及文档处理能力。
*   **图像反推**: 从图像反向生成提示词，用于风格迁移。
*   **工作流控制**: JSON 结构化输出、提示词优化、多轮对话管理。
*   **辅助工具**: 统一 API 密钥管理及模型信息查询。

### 🧩 节点列表

| 类别 | 节点类名 | 显示名称 | 功能描述 |
| :--- | :--- | :--- | :--- |
| **文本** | `LK_Gemini_Text` | 🌟 LK Gemini 文本生成 | 标准文本生成，支持模型选择。 |
| | `LK_Gemini_Chat` | 💬 LK Gemini 多轮对话 | 支持上下文历史的多轮对话。 |
| **图像** | `LK_Gemini_ImageGen` | 🎨 LK Gemini 图像生成 (Nano Banana) | Gemini 原生绘图能力。 |
| | `LK_Gemini_ImageEdit` | ✏️ LK Gemini 图像编辑 | 基于文本指令编辑图像。 |
| | `LK_Gemini_Imagen` | 🖼️ LK Imagen 图像生成 | Imagen 3 高保真图像生成。 |
| | `LK_NanoBanana` | 🍌 LK Nano Banana | Flash 图像生成 (gemini-2.5-flash-image)。 |
| | `LK_NanoBananaPro` | 🍌 LK Nano Banana Pro | Pro 高质量图像生成 (gemini-3-pro-image-preview)。 |
| | `LK_NanoBananaMulti` | 🍌 LK Nano Banana 多图 | 多图融合、风格迁移 (支持8图输入)。 |
| | `LK_ImageToPrompt` | 🔄 LK 图像反推提示词 | 分析图像生成提示词，用于风格复刻。 |
| **视频** | `LK_Gemini_VideoGen` | 🎬 LK Gemini 视频生成 (Veo 3.1) | Veo 3.1 文生视频。 |
| | `LK_Gemini_Image2Video` | 📹 LK Gemini 图生视频 | 静态图像转动态视频。 |
| **视觉** | `LK_Gemini_VisionAnalyze`| 👁️ LK Gemini 视觉分析 | 图像描述、打标、分析。 |
| | `LK_Gemini_DocumentProcess` | 📄 LK Gemini 文档处理 | PDF/文档图片解析提取。 |
| **高级** | `LK_Gemini_StructuredOutput`| 📋 LK Gemini 结构化输出 | JSON Schema 约束输出。 |
| | `LK_Gemini_PromptOptimizer` | 🔮 LK Gemini 提示词优化 | 智能优化提示词。 |
| | `LK_Gemini_Thinking` | 🧠 LK Gemini 深度思考 | 复杂问题显式推理。 |
| **工具** | `LK_Gemini_APIConfig` | ⚙️ LK Gemini API 配置 | API 密钥安全配置。 |
| | `LK_Gemini_ModelInfo` | 📊 LK Gemini 模型信息 | 模型列表及配额查询。 |
| | `LK_Gemini_PromptBuilder` | 🔧 LK 提示词构建器 | 辅助构建提示词模板。 |

### 🌐 通用 API 节点（适配任意 OpenAI 兼容自定义接口）

除 Gemini 专属节点外，本插件内置一套**通用 API 节点**，可对接任意遵循 OpenAI 协议的端点（OpenAI / Ollama / OpenRouter / DeepSeek / 火山方舟 / 硅基流动 / 任意自定义 URL）。

| 类别 | 节点类名 | 显示名称 | 功能描述 |
| :--- | :--- | :--- | :--- |
| **工具** | `LK_Universal_APIConfig` | 🌐 LK 通用 API 配置 | 选择厂商预设或自定义 base_url，统一输出连接参数。 |
| | `LK_Universal_ModelFetcher` | 📡 LK 通用 模型获取 | **自动拉取**指定端点的模型列表并写入缓存。 |
| **文本** | `LK_Universal_Chat` | 💬 LK 通用 对话 | 文本 + 多模态（图像）对话，模型下拉框读取缓存。 |
| **高级** | `LK_Universal_Structured` | 📋 LK 通用 结构化输出 | 强制 JSON 输出的结构化生成。 |

#### 典型工作流

1. 拖入 **🌐 LK 通用 API 配置**，选择厂商（如 `Ollama (本地)`）或填自定义 `base_url`。
2. 拖入 **📡 LK 通用 模型获取**，连接上一步的 `Base URL` / `API 密钥`，执行后自动拉取模型。
3. 在 **💬 LK 通用 对话** 节点上点击模型下拉框的刷新按钮，即可看到刚拉取的模型列表。
4. 输入提示词（可接入图像做多模态分析），开始使用。

> 支持的内置厂商预设：`OpenAI`、`Ollama (本地)`、`OpenRouter`、`DeepSeek`、`Together.ai`、`Venus (火山方舟)`、`硅基流动 (SiliconFlow)`、`智谱 GLM`、`Moonshot (Kimi)`、`百川`、`MiniMax`、`阶跃`、`讯飞星火`、`商汤 SenseChat`、`自定义 (Custom)`（共 14 家预设 + 自定义）。

#### Smart 故障转移（主备回退）

`LK_Universal_APIConfig` 与 `LK_Universal_Chat` 支持配置**备用端点**（如主用云端 API、备用本地 Ollama）。当主端点在重试后仍失败（超时 / 连接错误），客户端自动回退到备用端点完成请求，并在回复前标注 `[已回退至备用端点]`，保障工作流不中断。

### 📦 安装说明

1.  **克隆仓库**
    ```bash
    cd ComfyUI/custom_nodes
    git clone https://github.com/hdzwzqbxlk/ComfyUI-LK-Universal-Pro.git
    ```

2.  **安装依赖**
    ```bash
    cd ComfyUI-LK-Universal-Pro
    pip install -r requirements.txt
    ```

3.  **重启 ComfyUI**

### 🔑 配置指南

1.  前往 [Google AI Studio](https://aistudio.google.com/) 获取 API 密钥。
2.  配置方式：
    *   **直接输入**: 在各节点 `api_key` 输入框中填入。
    *   **环境变量**: 设置 `GOOGLE_API_KEY`。
    *   **配置节点**: 使用 `⚙️ LK Gemini API 配置` 节点统一管理。

### 📄 许可证
本项目基于 [MIT License](LICENSE) 开源。

---
<div align="center">
    Copyright © 2026 CCUT_LK Studio. All rights reserved.
</div>
