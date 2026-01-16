# 更新日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

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
