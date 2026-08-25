# -*- coding: utf-8 -*-
"""
ComfyUI-LK-Universal-Pro 插件
围绕 Gemini API 深度开发的 ComfyUI 节点集合

作者: CCUT_LK Studio
版本: 2.2.0
许可证: MIT
仓库: https://github.com/hdzwzqbxlk/ComfyUI-LK-Universal-Pro
"""

__version__ = "2.4.0"
__author__ = "CCUT_LK Studio"
__license__ = "MIT"

from .nodes.text_generation import LK_Gemini_Text, LK_Gemini_Chat
from .nodes.image_generation import LK_Gemini_ImageGen, LK_Gemini_ImageEdit, LK_Gemini_Imagen
from .nodes.video_generation import LK_Gemini_VideoGen, LK_Gemini_Image2Video
from .nodes.vision_understanding import LK_Gemini_VisionAnalyze, LK_Gemini_DocumentProcess
from .nodes.advanced_features import LK_Gemini_StructuredOutput, LK_Gemini_PromptOptimizer, LK_Gemini_Thinking
from .nodes.utility_nodes import LK_Gemini_APIConfig, LK_Gemini_ModelInfo, LK_Gemini_PromptBuilder
from .nodes.nano_banana import LK_NanoBanana, LK_NanoBananaPro, LK_NanoBananaMulti, LK_ImageToPrompt
from .nodes.universal_nodes import (
    LK_Universal_APIConfig, LK_Universal_ModelFetcher, LK_Universal_HealthCheck, LK_Universal_ModelCompare,
    LK_Universal_TextGen, LK_Universal_Chat, LK_Universal_Session,
    LK_Universal_ImageGen, LK_Universal_ImageEdit,
    LK_Universal_VideoGen,
    LK_Universal_Vision,
    LK_Universal_Structured, LK_Universal_ToolUse, LK_Universal_BatchChat, LK_Universal_TokenEstimate,
)

NODE_CLASS_MAPPINGS = {
    "LK_Gemini_Text": LK_Gemini_Text,
    "LK_Gemini_Chat": LK_Gemini_Chat,
    "LK_Gemini_ImageGen": LK_Gemini_ImageGen,
    "LK_Gemini_ImageEdit": LK_Gemini_ImageEdit,
    "LK_Gemini_Imagen": LK_Gemini_Imagen,
    "LK_Gemini_VideoGen": LK_Gemini_VideoGen,
    "LK_Gemini_Image2Video": LK_Gemini_Image2Video,
    "LK_Gemini_VisionAnalyze": LK_Gemini_VisionAnalyze,
    "LK_Gemini_DocumentProcess": LK_Gemini_DocumentProcess,
    "LK_Gemini_StructuredOutput": LK_Gemini_StructuredOutput,
    "LK_Gemini_PromptOptimizer": LK_Gemini_PromptOptimizer,
    "LK_Gemini_Thinking": LK_Gemini_Thinking,
    "LK_Gemini_APIConfig": LK_Gemini_APIConfig,
    "LK_Gemini_ModelInfo": LK_Gemini_ModelInfo,
    "LK_Gemini_PromptBuilder": LK_Gemini_PromptBuilder,
    "LK_NanoBanana": LK_NanoBanana,
    "LK_NanoBananaPro": LK_NanoBananaPro,
    "LK_NanoBananaMulti": LK_NanoBananaMulti,
    "LK_ImageToPrompt": LK_ImageToPrompt,
    "LK_Universal_APIConfig": LK_Universal_APIConfig,
    "LK_Universal_ModelFetcher": LK_Universal_ModelFetcher,
    "LK_Universal_HealthCheck": LK_Universal_HealthCheck,
    "LK_Universal_ModelCompare": LK_Universal_ModelCompare,
    "LK_Universal_TextGen": LK_Universal_TextGen,
    "LK_Universal_Chat": LK_Universal_Chat,
    "LK_Universal_Session": LK_Universal_Session,
    "LK_Universal_ImageGen": LK_Universal_ImageGen,
    "LK_Universal_ImageEdit": LK_Universal_ImageEdit,
    "LK_Universal_VideoGen": LK_Universal_VideoGen,
    "LK_Universal_Vision": LK_Universal_Vision,
    "LK_Universal_Structured": LK_Universal_Structured,
    "LK_Universal_ToolUse": LK_Universal_ToolUse,
    "LK_Universal_BatchChat": LK_Universal_BatchChat,
    "LK_Universal_TokenEstimate": LK_Universal_TokenEstimate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LK_Gemini_Text": "🌟 LK Gemini 文本生成",
    "LK_Gemini_Chat": "💬 LK Gemini 多轮对话",
    "LK_Gemini_ImageGen": "🎨 LK Gemini 图像生成 (Nano Banana)",
    "LK_Gemini_ImageEdit": "✏️ LK Gemini 图像编辑",
    "LK_Gemini_Imagen": "🖼️ LK Imagen 图像生成",
    "LK_Gemini_VideoGen": "🎬 LK Gemini 视频生成 (Veo 3.1)",
    "LK_Gemini_Image2Video": "📹 LK Gemini 图生视频",
    "LK_Gemini_VisionAnalyze": "👁️ LK Gemini 视觉分析",
    "LK_Gemini_DocumentProcess": "📄 LK Gemini 文档处理",
    "LK_Gemini_StructuredOutput": "📋 LK Gemini 结构化输出",
    "LK_Gemini_PromptOptimizer": "🔮 LK Gemini 提示词优化",
    "LK_Gemini_Thinking": "🧠 LK Gemini 深度思考",
    "LK_Gemini_APIConfig": "⚙️ LK Gemini API 配置",
    "LK_Gemini_ModelInfo": "📊 LK Gemini 模型信息",
    "LK_Gemini_PromptBuilder": "🔧 LK 提示词构建器",
    "LK_NanoBanana": "🍌 LK Nano Banana (Google Gemini 图像)",
    "LK_NanoBananaPro": "🍌 LK Nano Banana Pro (Google Gemini 图像)",
    "LK_NanoBananaMulti": "🍌 LK Nano Banana 多图 (Google Gemini 图像)",
    "LK_ImageToPrompt": "🔄 LK 图像反推提示词",
    "LK_Universal_APIConfig": "🌐 LK 通用 API 配置",
    "LK_Universal_ModelFetcher": "📡 LK 通用 模型获取 (自动拉取)",
    "LK_Universal_HealthCheck": "🩺 LK 通用 端点健康检查",
    "LK_Universal_ModelCompare": "🔍 LK 通用 模型对比",
    "LK_Universal_TextGen": "📝 LK 通用 文本生成 (单轮)",
    "LK_Universal_Chat": "💬 LK 通用 多轮对话",
    "LK_Universal_Session": "🧵 LK 通用 会话管理",
    "LK_Universal_ImageGen": "🎨 LK 通用 图像生成",
    "LK_Universal_ImageEdit": "✏️ LK 通用 图像编辑",
    "LK_Universal_VideoGen": "🎬 LK 通用 视频生成",
    "LK_Universal_Vision": "👁️ LK 通用 视觉理解 (多图)",
    "LK_Universal_Structured": "📋 LK 通用 结构化输出",
    "LK_Universal_ToolUse": "🛠️ LK 通用 工具调用",
    "LK_Universal_BatchChat": "📚 LK 通用 批量对话",
    "LK_Universal_TokenEstimate": "🧮 LK 通用 Token 估算",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
