# ComfyUI-LK-Universal-Pro

<div align="center">

![Version](https://img.shields.io/badge/Version-2.6.0-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Compatible-orange?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-Compatible-007EA7?style=for-the-badge)

**[English](#english) | [中文说明](#中文说明)**

</div>

---

<a name="english"></a>
## 📖 English

### Introduction
**ComfyUI-LK-Universal-Pro** is a ComfyUI extension that connects to **any OpenAI-compatible API endpoint** — OpenAI / Ollama / OpenRouter / DeepSeek / Volcano Ark / SiliconFlow / any custom URL. It provides a focused set of universal nodes covering text, image, video, vision and tool-use workflows, with **no vendor lock-in**.

### 📁 Node Structure
All nodes live under `LK_Studio/通用 API`:

```
LK_Studio/通用 API/
├── 工具/    # APIConfig / ModelFetcher / HealthCheck / ModelCompare
├── 文本/    # Chat (single & multi-turn)
├── 图像/    # ImageGen / ImageEdit
├── 视频/    # VideoGen (text→video / image→video)
├── 视觉/    # Vision (multi-image)
└── 高级/    # Advanced (structured / tool-calling) / BatchChat / TokenEstimate
```

### ✨ Key Features
* **Universal API**: one node family for any OpenAI-compatible endpoint.
* **Auto model fetch**: `ModelFetcher` pulls the real `/models` list from your endpoint and fills the dropdown (refresh button).
* **Smart failover**: configure a backup endpoint; auto-fallback on failure.
* **Multi-modal**: image generation, image editing, video generation, vision understanding.
* **Advanced**: structured JSON output, function calling, batch chat, token estimation.

### 🧩 Node List

| Category | Node | Display | Description |
| :--- | :--- | :--- | :--- |
| **Text** | `LK_Universal_Chat` | 💬 对话 (单轮/多轮) | Single/multi-turn chat, outputs history JSON. |
| **Image** | `LK_Universal_ImageGen` | 🎨 图像生成 | Text-to-image (`/images/generations`). |
| | `LK_Universal_ImageEdit` | ✏️ 图像编辑 | Image edit/inpaint (`/images/edits`). |
| **Video** | `LK_Universal_VideoGen` | 🎬 视频生成 | Text/image-to-video (`/videos/generations`). |
| **Vision** | `LK_Universal_Vision` | 👁️ 视觉理解 | Multi-image + text understanding. |
| **Advanced** | `LK_Universal_Advanced` | 🧩 高级对话 | Structured JSON output OR function calling (mode switch). |
| | `LK_Universal_BatchChat` | 📚 批量对话 | Batch prompts (one row each), summarize results. |
| | `LK_Universal_TokenEstimate` | 🧮 Token 估算 | Rough token-budget estimation. |
| **Tools** | `LK_Universal_APIConfig` | 🌐 API 配置 | Provider presets / custom `base_url` + backup. |
| | `LK_Universal_ModelFetcher` | 📡 模型获取 | Auto-pull model list (`/models`). |
| | `LK_Universal_HealthCheck` | 🩺 健康检查 | Latency + auth check. |
| | `LK_Universal_ModelCompare` | 🔍 模型对比 | Compare primary/backup model sets. |

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
1.  Obtain an API key from your provider (OpenAI / Ollama / OpenRouter / DeepSeek / …).
2.  Configure in ComfyUI:
    *   **Direct Input**: Paste the key into the `api_key` widget on any node.
    *   **Config Node**: Use the `🌐 LK 通用 API 配置` node to manage base_url / key centrally (with optional backup endpoint).

### 🌐 典型工作流
1. 拖入 **🌐 LK 通用 API 配置**，选择厂商（如 `Ollama (本地)`）或填自定义 `base_url`。
2. 拖入 **📡 LK 通用 模型获取**，连接上一步的 `Base URL` / `API 密钥`，执行后自动拉取模型。
3. 在对话节点上点击模型下拉框的刷新按钮，即可看到刚拉取的模型列表。
4. 输入提示词（可接入图像做多模态分析），开始使用。

> 支持的内置厂商预设：`OpenAI`、`Ollama (本地)`、`OpenRouter`、`DeepSeek`、`Together.ai`、`Venus (火山方舟)`、`硅基流动 (SiliconFlow)`、`智谱 GLM`、`Moonshot (Kimi)`、`百川`、`MiniMax`、`阶跃`、`讯飞星火`、`商汤 SenseChat`、`自定义 (Custom)`（共 14 家预设 + 自定义）。

### 📄 License
This project is licensed under the [MIT License](LICENSE).

---

<a name="中文说明"></a>
## 📖 中文说明

### 项目简介
**ComfyUI-LK-Universal-Pro** 是一个为 ComfyUI 打造的通用型扩展插件，可对接**任意遵循 OpenAI 协议的端点**（OpenAI / Ollama / OpenRouter / DeepSeek / 火山方舟 / 硅基流动 / 任意自定义 URL），提供覆盖文本、图像、视频、视觉与工具调用的节点，**不绑定任何单一厂商**。

### 📁 节点结构
所有节点统一组织在 `LK_Studio/通用 API` 目录下，按能力分类：

```
LK_Studio/通用 API/
├── 工具/    # APIConfig / ModelFetcher / HealthCheck / ModelCompare
├── 文本/    # Chat (单轮/多轮)
├── 图像/    # ImageGen / ImageEdit
├── 视频/    # VideoGen (文生视频 / 图生视频)
├── 视觉/    # Vision (多图理解)
└── 高级/    # Advanced (结构化/工具调用) / BatchChat / TokenEstimate
```

### ✨ 核心特性
*   **通用 API**：一套节点对接任意 OpenAI 兼容端点，告别厂商硬编码。
*   **自动拉取模型**：`📡 模型获取` 从端点拉取真实 `/models` 列表并填充下拉框（点击刷新即可刷新）。
*   **Smart 故障转移**：配置备用端点，主端点失败时自动回退。
*   **多模态**：图像生成、图像编辑、视频生成、视觉理解。
*   **高级能力**：结构化 JSON 输出、Function Calling、批量对话、Token 预算估算。

### 🧩 节点列表

| 类别 | 节点类名 | 显示名称 | 功能描述 |
| :--- | :--- | :--- | :--- |
| **文本** | `LK_Universal_Chat` | 💬 LK 通用 对话 (单轮/多轮) | 单轮/多轮对话，输出历史 JSON。 |
| **图像** | `LK_Universal_ImageGen` | 🎨 LK 通用 图像生成 | 文生图（`/images/generations`）。 |
| | `LK_Universal_ImageEdit` | ✏️ LK 通用 图像编辑 | 图生图/编辑（`/images/edits`）。 |
| **视频** | `LK_Universal_VideoGen` | 🎬 LK 通用 视频生成 (文/图生视频) | 文生视频 / 图生视频（`/videos/generations`，端点支持时）。 |
| **视觉** | `LK_Universal_Vision` | 👁️ LK 通用 视觉理解 (多图) | 多图 + 文本，图文理解。 |
| **高级** | `LK_Universal_Advanced` | 🧩 LK 通用 高级对话 (结构化/工具调用) | `mode` 切换「结构化输出」或「工具调用」。 |
| | `LK_Universal_BatchChat` | 📚 LK 通用 批量对话 | 一次提交多组提示词（按行），逐条调用汇总。 |
| | `LK_Universal_TokenEstimate` | 🧮 LK 通用 Token 估算 | 按系统/提示/历史/预留输出粗略估算，提前判断超限。 |
| **工具** | `LK_Universal_APIConfig` | 🌐 LK 通用 API 配置 | 选择厂商预设或自定义 `base_url`，统一输出连接参数（含备用端点）。 |
| | `LK_Universal_ModelFetcher` | 📡 LK 通用 模型获取 (自动拉取) | 自动拉取指定端点的模型列表并写入缓存。 |
| | `LK_Universal_HealthCheck` | 🩺 LK 通用 端点健康检查 | 拉取 /models 并测往返延迟，验证端点可达 + 鉴权有效。 |
| | `LK_Universal_ModelCompare` | 🔍 LK 通用 模型对比 | 对比主/备端点模型集合（仅主/仅备/共有），辅助故障转移选型。 |

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
1.  从你的服务商获取 API 密钥（OpenAI / Ollama / OpenRouter / DeepSeek / …）。
2.  配置方式：
    *   **直接输入**: 在各节点 `api_key` 输入框中填入。
    *   **配置节点**: 使用 `🌐 LK 通用 API 配置` 节点统一管理（含备用端点）。

### 🌐 典型工作流
1. 拖入 **🌐 LK 通用 API 配置**，选择厂商（如 `Ollama (本地)`）或填自定义 `base_url`。
2. 拖入 **📡 LK 通用 模型获取**，连接上一步的 `Base URL` / `API 密钥`，执行后自动拉取模型。
3. 在对话节点上点击模型下拉框的刷新按钮，即可看到刚拉取的模型列表。
4. 输入提示词（可接入图像做多模态分析），开始使用。

> 支持的内置厂商预设：`OpenAI`、`Ollama (本地)`、`OpenRouter`、`DeepSeek`、`Together.ai`、`Venus (火山方舟)`、`硅基流动 (SiliconFlow)`、`智谱 GLM`、`Moonshot (Kimi)`、`百川`、`MiniMax`、`阶跃`、`讯飞星火`、`商汤 SenseChat`、`自定义 (Custom)`（共 14 家预设 + 自定义）。

### 📄 许可证
本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">
    Copyright © 2026 CCUT_LK Studio. All rights reserved.
</div>
