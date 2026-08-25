# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [2.5.1] - 2026-08-25

### ✨ 增强：原 Gemini 优秀功能集成进通用节点（不加节点，只增强）

- **ImageGen**：新增 `aspect_ratio`（自动/1:1/16:9/9:16/4:3/3:4，映射到最接近尺寸）与 `seed`（-1 随机，≥0 透传端点做种子控制）
- **ImageEdit**：新增 `reference_images` 多参考图输入（batch，主图+参考图上限 4，覆盖 NanoBananaMulti 多图合成场景）与 `seed`
- **VideoGen**：新增 `resolution`（480p/720p/1080p）与 `last_frame` 尾帧输入（端点支持首尾帧插值时生效）
- **Vision**：新增 `task_preset` 任务预设（自由提问/详细描述/**反推提示词**/提取文字/翻译文字），覆盖原 ImageToPrompt 场景
- **Chat**：新增可选 `file_path` 文本文件注入（读取 txt/md/py/json 等内容作为上下文，覆盖 DocumentProcess 文本处理场景）
- 版本 2.5.0 → 2.5.1

## [2.5.0] - 2026-08-25

### ♻️ 重构：移除 Gemini 专项体系，统一为通用节点并合并精简

- **移除 Gemini 专项节点（18 个）**：删除 `text_generation.py` / `image_generation.py` / `video_generation.py` / `vision_understanding.py` / `advanced_features.py` / `utility_nodes.py` / `nano_banana.py` 共 7 个文件，以及 `__init__.py` 中全部 `LK_Gemini_*` / `LK_NanoBanana*` / `LK_ImageToPrompt` 注册；`utils/api_client.py` 中 Gemini 专属的 `GeminiAPIClient` 与 `GEMINI_*` / `IMAGEN_*` 常量一并移除。所有能力由 `UniversalAPIClient`（OpenAI 兼容）统一承接，彻底消除「Gemini 硬编码端点」与「通用节点」两套并行体系。
- **合并通用节点 15 → 11**：
  - `LK_Universal_TextGen` 并入 `LK_Universal_Chat`（history 可选，空 history 即单轮）
  - `LK_Universal_Session` 移除（历史裁剪/合并可由 Chat 历史链路在下游处理；若需清空可用空 history）
  - `LK_Universal_VideoGen` 新增可选 `image` 输入，覆盖图生视频（透传首帧/参考图，端点支持时生效）
  - `LK_Universal_Structured` 与 `LK_Universal_ToolUse` 合并为 `LK_Universal_Advanced`，用 `mode` 切换「结构化输出 / 工具调用」
- 版本 2.4.1 → 2.5.0（MINOR：架构级重构，移除专项能力并合并节点）

## [2.4.1] - 2026-08-25

### 🐛 修复：通用 API 节点的 `model` 字段无法按端点选择

v2.4.0 交付的 `model` 下拉框只展示 14 家厂商预设模型的并集（gpt-4o / dall-e-3 / llava / ...），而不是节点自己 `base_url` 的真实模型，导致 `token.s...` 这类自定义/中转端点选不到真实模型。本补丁根因级修复：

- **新增 `web/lk_universal_models.js` 前端扩展**：节点创建 / `base_url` / `api_key` 变化时，自动 POST `/lk_universal/fetch_models` 拉取该端点的 `/models` 列表，动态填充 `model` 下拉框（combo `options.values` 实时更新；保留当前选中值若仍在列表内）。失败时静默回退，不破坏既有下拉。
- **新增 `__init__.py` 服务端代理路由 `POST /lk_universal/fetch_models`**：接收 `{base_url, api_key, filter_keyword?}`，调用 `UniversalAPIClient.list_models()`，返回 `{ok, models}`，并把结果写入全局 `UNIVERSAL_MODEL_CACHE`（供执行时校验使用）。
- **新增 `WEB_DIRECTORY = .../web`**：注册 ComfyUI 前端扩展加载路径。
- **执行时硬校验**（`_validate_model`）：每个模型类节点在创建 client 之后立即校验 —— 空模型直接报错；若全局缓存非空且所选 `model` 不在已拉取列表中（下拉未刷新 / 手动输入），抛出 `UniversalAPIError` 并由现有 `except` 分支转换为明确报错（如 `API 错误: 模型「xxx」不在已拉取列表中…`），避免用错模型静默失败。共覆盖 9 个模型类节点（TextGen / Chat / ImageGen / ImageEdit / VideoGen / Vision / Structured / ToolUse / BatchChat）。
- 版本号 2.4.0 → 2.4.1（PATCH：bug 修复 / 小幅体验优化，不升 MINOR/MAJOR）

## [2.4.0] - 2026-08-25

### ✨ 重构：通用 API 节点按 6 大类铺满（对标 Gemini 颗粒度）

将原本 4 个「通用 API」节点扩充为 **15 个**，覆盖 文本 / 图像 / 视频 / 视觉 / 高级 / 工具 六大类，缩小与参考插件的覆盖差距。

- **新增节点（11 个）**
  - 工具：`LK_Universal_HealthCheck`（端点健康检查）、`LK_Universal_ModelCompare`（主备端点模型对比）
  - 文本：`LK_Universal_TextGen`（单轮文生文）、`LK_Universal_Session`（会话/历史管理）
  - 图像：`LK_Universal_ImageGen`（文生图）、`LK_Universal_ImageEdit`（图生图/编辑）
  - 视频：`LK_Universal_VideoGen`（文生视频）
  - 视觉：`LK_Universal_Vision`（多图视觉理解，与纯文本 Chat 分离）
  - 高级：`LK_Universal_ToolUse`（Function Calling）、`LK_Universal_BatchChat`（批量对话）、`LK_Universal_TokenEstimate`（Token 预算估算）
- **扩展 `utils/api_client.py`**：`UniversalAPIClient` 新增 `edit_image`（/images/edits）、`generate_video`（/videos/generations）、`parse_tool_calls`、`estimate_tokens` 方法
- **复用**：图像转换沿用 `utils/image_utils` 的 `pil_to_tensor` / `base64_to_pil`，不重复造轮子
- 版本号 2.3.1 → 2.4.0（README 徽章 / __init__ 同步）

### 🔧 变更
- `LK_Universal_Chat` 收敛为纯文本多轮对话；多模态视觉能力拆分至 `LK_Universal_Vision`
- 所有节点兼容既有 Smart 故障转移与全局模型缓存，未破坏现有工作流

---

## [2.3.0] - 2026-08-24

### 🌐 新增：通用 API 兼容层（Universal API）

参考 ComfyUI-AI-CustomURL、ComfyUI-OpenAI-Compat-LLM-Node 等开源插件，
将插件从「仅 Gemini」扩展为「兼容任意 OpenAI 兼容自定义 API 接口」。

- **新增通用节点**（`LK_Studio/通用 API/` 分类）
  - `LK_Universal_APIConfig` — 厂商预设（OpenAI/Ollama/OpenRouter/DeepSeek/Together/火山方舟/硅基流动/自定义）+ 自定义 base_url 统一配置
  - `LK_Universal_ModelFetcher` — **自动拉取**指定端点的 `/models` 模型列表并写入全局缓存（含 Ollama 原生 `/api/tags` 兜底）
  - `LK_Universal_Chat` — 通用对话，支持文本 + 多模态（图像 base64 注入），模型下拉框读取缓存
  - `LK_Universal_Structured` — 通用结构化 JSON 输出（`response_format=json_object`，并对不支持的端点自动降级）
- **新增 `utils/provider_registry.py`** — 厂商预设表 + 进程级全局模型缓存 `UNIVERSAL_MODEL_CACHE`，对话节点下拉框刷新即读取
- **扩展 `utils/api_client.py`** — 新增 `UniversalAPIClient`（Bearer 鉴权、chat/completions、images/generations、/models 拉取、重试/超时、思考链解析）

### 🔧 变更
- 移除未实际使用的 `google-genai` 依赖（改为直接调用官方 REST API），降低耦合、便于对接多端点
- 版本号 2.0.0 → 2.3.0（pyproject / README / __init__ 同步）

## [2.3.1] - 2026-08-24（补强）

### ✨ 新增（借鉴 ComfyUI-LLMs-Toolkit / ComfyUI-LLM-Chat）
- **国产厂商深度覆盖**：`provider_registry` 预设由 7 家扩充至 14 家，新增 智谱 GLM、Moonshot(Kimi)、百川、MiniMax、阶跃、讯飞星火、商汤 SenseChat
- **Smart 故障转移**：`UniversalAPIClient` 支持 `fallback_base_url/fallback_api_key`，主端点重试失败后自动回退备用端点（如云端→本地 Ollama）；`LK_Universal_APIConfig` 与 `LK_Universal_Chat` 新增备用端点配置项，回退成功时在回复标注 `[已回退至备用端点]`

---

## [2.0.0] - 2026-01-16

### 🎉 重大更新
完全重构插件，围绕 Gemini API 深度开发。

### ✨ 新增
- **文本生成节点**
  - `LK_Gemini_Text` - 通用文本生成，支持 Gemini 3/2.5 全系列模型和思考模式
  - `LK_Gemini_Chat` - 多轮对话，对话历史管理

- **图像生成节点 (Nano Banana)**
  - `LK_Gemini_ImageGen` - Gemini 原生图像生成
  - `LK_Gemini_ImageEdit` - 文本指令图像编辑
  - `LK_Gemini_Imagen` - Imagen 3 模型图像生成

- **视频生成节点 (Veo 3.1)**
  - `LK_Gemini_VideoGen` - 文生视频，支持原生音频
  - `LK_Gemini_Image2Video` - 图生视频，首帧/末帧指定

- **视觉理解节点**
  - `LK_Gemini_VisionAnalyze` - 多模态图像分析
  - `LK_Gemini_DocumentProcess` - PDF 文档处理

- **高级功能节点**
  - `LK_Gemini_StructuredOutput` - JSON Schema 结构化输出
  - `LK_Gemini_PromptOptimizer` - AI 提示词优化
  - `LK_Gemini_Thinking` - 深度思考模式

- **辅助节点**
  - `LK_Gemini_APIConfig` - API 密钥集中管理
  - `LK_Gemini_ModelInfo` - 模型信息查询
  - `LK_Gemini_PromptBuilder` - 提示词组合构建器

### 🔧 变更
- 项目结构重构为模块化设计
- 新增 `utils/` 工具模块目录
- 新增 `nodes/` 节点模块目录

---

## [1.0.0] - 初始版本

### 节点
- `LK_Pro_Visual_Engine` - Imagen 3 图像生成
- `LK_Prompt_Optimizer` - 提示词优化
- `LK_Vision_Describer` - 图像描述

---

[2.0.0]: https://github.com/hdzwzqbxlk/ComfyUI-LK-Universal-Pro/releases/tag/v2.0.0
[1.0.0]: https://github.com/hdzwzqbxlk/ComfyUI-LK-Universal-Pro/releases/tag/v1.0.0
