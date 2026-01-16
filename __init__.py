# -*- coding: utf-8 -*-
"""
ComfyUI-LK-Universal-Pro 插件
围绕 Gemini API 深度开发的 ComfyUI 节点集合

作者: LK Studio
版本: 2.1.0
许可证: MIT
仓库: https://github.com/hdzwzqbxlk/ComfyUI-LK-Universal-Pro
"""

__version__ = "2.1.0"
__author__ = "LK Studio"
__license__ = "MIT"

# 导入所有节点
from .nodes.text_generation import LK_Gemini_Text, LK_Gemini_Chat
from .nodes.image_generation import LK_Gemini_ImageGen, LK_Gemini_ImageEdit, LK_Gemini_Imagen
from .nodes.video_generation import LK_Gemini_VideoGen, LK_Gemini_Image2Video
from .nodes.vision_understanding import LK_Gemini_VisionAnalyze, LK_Gemini_DocumentProcess
from .nodes.advanced_features import LK_Gemini_StructuredOutput, LK_Gemini_PromptOptimizer, LK_Gemini_Thinking
from .nodes.utility_nodes import LK_Gemini_APIConfig, LK_Gemini_ModelInfo, LK_Gemini_PromptBuilder
from .nodes.nano_banana import LK_NanoBanana, LK_NanoBananaPro

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
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
