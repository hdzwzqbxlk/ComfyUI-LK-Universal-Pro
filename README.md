# ComfyUI-LK-Universal-Pro

<div align="center">

![Version](https://img.shields.io/badge/Version-2.0.0-blue?style=for-the-badge)
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

This project goes beyond simple text generation, offering native support for image generation (Imagen 3), video generation (Veo), advanced computer vision analysis, and structured outputs. It is designed for professionals who require precision, flexibility, and the latest capabilities of the Gemini models.

### ✨ Key Features

*   **Advanced Text Generation**: Support for Gemini 1.5/2.5 Pro & Flash models, including "Thinking" mode for complex reasoning.
*   **Multi-Modal Generation**:
    *   **Image**: Native integration of Imagen 3 and Gemini image generation capabilities.
    *   **Video**: Access to Veo 3.1 for high-quality text-to-video and image-to-video transfers.
*   **Computer Vision**: Deep visual analysis and document processing (PDF/Image) capabilities.
*   **Workflow Control**: Structured JSON outputs, automatic prompt optimization, and multi-turn chat memory management.
*   **Utility Tools**: Centralized API key management and model information retrieval.

### 🧩 Node List

| Category | Node Name (Internal) | Display Name | Description |
| :--- | :--- | :--- | :--- |
| **Text** | `LK_Gemini_Text` | 🌟 LK Gemini Text Gen | Standard text generation with model selection. |
| | `LK_Gemini_Chat` | 💬 LK Gemini Chat | Multi-turn conversation with context history. |
| **Image** | `LK_Gemini_ImageGen` | 🎨 LK Gemini Image Gen | Native Gemini image generation (Nano Banana). |
| | `LK_Gemini_ImageEdit` | ✏️ LK Gemini Image Edit | Edit existing images via text instructions. |
| | `LK_Gemini_Imagen` | 🖼️ LK Imagen Image Gen | High-fidelity generation using Imagen 3 models. |
| **Video** | `LK_Gemini_VideoGen` | 🎬 LK Gemini Video Gen | Text-to-Video generation using Veo 3.1. |
| | `LK_Gemini_Image2Video` | 📹 LK Gemini Image2Video | Transform source images into video sequences. |
| **Vision** | `LK_Gemini_VisionAnalyze`| 👁️ LK Gemini Vision | Analyze images for descriptions, tagging, etc. |
| | `LK_Gemini_DocumentProcess` | 📄 LK Gemini Doc Process | Extract and process text from Document/PDFs. |
| **Advanced**| `LK_Gemini_StructuredOutput`| 📋 LK Gemini Structured | Enforce JSON output schemas. |
| | `LK_Gemini_PromptOptimizer` | 🔮 LK Gemini Optimizer | Optimize user prompts for better results. |
| | `LK_Gemini_Thinking` | 🧠 LK Gemini Thinking | Explicit reasoning step for complex queries. |
| **Utils** | `LK_Gemini_APIConfig` | ⚙️ LK Gemini API Config | Secure API Key configuration. |
| | `LK_Gemini_ModelInfo` | 📊 LK Model Info | List available models and capabilities. |
| | `LK_Gemini_PromptBuilder` | 🔧 LK Prompt Builder | Helper tool to construct complex prompts. |

### 📦 Installation

1.  **Clone the Repository**
    Navigate to your ComfyUI `custom_nodes` directory and clone this repo:
    ```bash
    cd ComfyUI/custom_nodes
    git clone https://github.com/hdzwzqbxlk/ComfyUI-LK-Universal-Pro.git
    ```

2.  **Install Dependencies**
    It is recommended to use the Python environment embedded in ComfyUI or your active virtual environment.
    ```bash
    cd ComfyUI-LK-Universal-Pro
    pip install -r requirements.txt
    ```
    *Note: Ensure `google-generativeai` package is installed and up to date.*

3.  **Restart ComfyUI**

### 🔑 Configuration

To use these nodes, you must possess a valid Google Gemini API Key.

1.  Obtain an API Key from [Google AI Studio](https://aistudio.google.com/).
2.  In ComfyUI, you can provide the key in two ways:
    *   **Direct Input**: Paste the key into the relevant widget on any node.
    *   **Environment Variable**: Set `GOOGLE_API_KEY` in your system environment.
    *   **Config Node**: Use the `LK Gemini API Config` node to pass the key downstream to other nodes.

### 📄 License
This project is licensed under the [MIT License](LICENSE).

---

<a name="中文说明"></a>
## 📖 中文说明

### 项目简介
**ComfyUI-LK-Universal-Pro** 是一个为 ComfyUI 打造的全能型扩展插件，旨在深度集成 Google Gemini API 生态系统。该项目提供了一整套专业级节点，帮助用户在 ComfyUI 工作流中充分释放多模态生成式 AI 的潜力。

不同于简单的文本生成工具，本项目原生支持 Imagen 3 图像生成、Veo 视频生成、高级计算机视觉分析以及结构化数据输出。它是为需要精准控制、灵活性以及追求 Gemini 模型最新能力的专业用户设计的。

### ✨ 核心特性

*   **高级文本生成**: 完美支持 Gemini 1.5/2.5 Pro & Flash 全系模型，主要包含"深度思考 (Thinking)"模式，处理复杂逻辑。
*   **多模态生成**:
    *   **图像**: 原生集成 Imagen 3 及 Gemini 图像生成能力。
    *   **视频**: 接入 Veo 3.1 模型，支持高质量的文生视频及图生视频功能。
*   **视觉理解**: 具备深度的图像语义分析及文档（PDF/图像）处理能力。
*   **工作流控制**: 支持 JSON 结构化输出约束、提示词自动优化以及多轮对话上下文管理。
*   **辅助工具**: 提供统一的 API 密钥管理及实时模型信息查询功能。

### 🧩 节点列表

| 类别 | 节点类名 (Internal) | 显示名称 | 功能描述 |
| :--- | :--- | :--- | :--- |
| **文本** | `LK_Gemini_Text` | 🌟 LK Gemini 文本生成 | 标准文本生成，支持模型选择与参数调整。 |
| | `LK_Gemini_Chat` | 💬 LK Gemini 多轮对话 | 支持上下文历史记忆的多轮对话交互。 |
| **图像** | `LK_Gemini_ImageGen` | 🎨 LK Gemini 图像生成 | 调用 Gemini 原生绘图能力 (Nano Banana)。 |
| | `LK_Gemini_ImageEdit` | ✏️ LK Gemini 图像编辑 | 基于文本指令编辑和修改现有图像。 |
| | `LK_Gemini_Imagen` | 🖼️ LK Imagen 图像生成 | 使用 Imagen 3 模型生成高保真图像。 |
| **视频** | `LK_Gemini_VideoGen` | 🎬 LK Gemini 视频生成 | 使用 Veo 3.1 进行文生视频创作。 |
| | `LK_Gemini_Image2Video` | 📹 LK Gemini 图生视频 | 将静态图像转换为动态视频序列。 |
| **视觉** | `LK_Gemini_VisionAnalyze`| 👁️ LK Gemini 视觉分析 | 对输入图像进行详细描述、打标或分析。 |
| | `LK_Gemini_DocumentProcess` | 📄 LK Gemini 文档处理 | 解析和提取 PDF 或文档图片的图文内容。 |
| **高级** | `LK_Gemini_StructuredOutput`| 📋 LK Gemini 结构化输出| 强制模型输出符合特定 Schema 的 JSON 数据。 |
| | `LK_Gemini_PromptOptimizer` | 🔮 LK Gemini 提示词优化 | 智能优化原始提示词以获得更好结果。 |
| | `LK_Gemini_Thinking` | 🧠 LK Gemini 深度思考 | 针对复杂问题进行显式的推理步骤生成。 |
| **工具** | `LK_Gemini_APIConfig` | ⚙️ LK Gemini API 配置 | 安全地配置和分发 API 密钥。 |
| | `LK_Gemini_ModelInfo` | 📊 LK Gemini 模型信息 | 查询当前可用的模型列表及配额信息。 |
| | `LK_Gemini_PromptBuilder` | 🔧 LK 提示词构建器 | 辅助构建复杂的提示词模板。 |

### 📦 安装说明

1.  **克隆仓库**
    进入您的 ComfyUI `custom_nodes` 目录并克隆本项目：
    ```bash
    cd ComfyUI/custom_nodes
    git clone https://github.com/hdzwzqbxlk/ComfyUI-LK-Universal-Pro.git
    ```

2.  **安装依赖**
    建议使用 ComfyUI 自带的 Python 环境或当前激活的虚拟环境进行安装。
    ```bash
    cd ComfyUI-LK-Universal-Pro
    pip install -r requirements.txt
    ```
    *注意：请确保 `google-generativeai` 库已安装并更新至最新版本。*

3.  **重启 ComfyUI**

### 🔑 配置指南

使用本插件所有功能均需要有效的 Google Gemini API Key。

1.  前往 [Google AI Studio](https://aistudio.google.com/) 获取 API 密钥。
2.  在 ComfyUI 中，您可以通过以下方式配置：
    *   **直接输入**: 在各节点的 `api_key` 输入框中直接填入。
    *   **环境变量**: 在系统环境变量中设置 `GOOGLE_API_KEY`。
    *   **配置节点**: 使用 `⚙️ LK Gemini API 配置` 节点统一管理，并将密钥连接至其他节点。

### 📄 许可证
本项目基于 [MIT License](LICENSE) 开源。

---
<div align="center">
    Copyright © 2024 LK Studio. All rights reserved.
</div>
