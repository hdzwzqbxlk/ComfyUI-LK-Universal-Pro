# -*- coding: utf-8 -*-
"""辅助节点"""

import json
from typing import Tuple, List

try:
    from ..utils.api_client import GeminiAPIClient, GeminiAPIError
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.api_client import GeminiAPIClient, GeminiAPIError


class LK_Gemini_APIConfig:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"api_key": ("STRING", {"default": "", "placeholder": "输入 Gemini API 密钥"})},
            "optional": {
                "timeout": ("INT", {"default": 60, "min": 10, "max": 600, "step": 10}),
                "max_retries": ("INT", {"default": 3, "min": 1, "max": 10}),
                "validate_key": ("BOOLEAN", {"default": False})
            }}
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("API 密钥", "配置状态")
    FUNCTION = "configure"
    CATEGORY = "LK_Studio/Gemini/工具"

    def configure(self, api_key, timeout=60, max_retries=3, validate_key=False):
        if not api_key: return ("", "错误: 请提供 API 密钥")
        status = [f"超时: {timeout}秒", f"重试: {max_retries}次"]
        if validate_key:
            try:
                client = GeminiAPIClient(api_key, timeout=30, max_retries=1)
                models = client.list_models()
                status.append(f"验证成功，可用模型: {len(models)} 个")
            except Exception as e: return ("", f"验证失败: {str(e)}")
        else: status.append("密钥未验证")
        return (api_key, " | ".join(status))


class LK_Gemini_ModelInfo:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"api_key": ("STRING", {"default": ""})},
            "optional": {
                "filter_type": (["全部", "文本模型", "图像模型", "视频模型"], {"default": "全部"}),
                "output_format": (["简洁列表", "详细信息", "JSON"], {"default": "简洁列表"})
            }}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("模型信息",)
    FUNCTION = "get_info"
    CATEGORY = "LK_Studio/Gemini/工具"

    def get_info(self, api_key, filter_type="全部", output_format="简洁列表"):
        text_models = ["gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-2.5-pro", "gemini-2.5-flash"]
        image_models = ["gemini-2.5-flash-image", "gemini-3-pro-image-preview", "imagen-3", "imagen-3-fast"]
        video_models = ["veo-3.1-generate-preview", "veo-3.1-fast-preview", "veo-3", "veo-2"]
        all_models = []
        if filter_type in ["全部", "文本模型"]: all_models.extend([{"name": m, "type": "文本"} for m in text_models])
        if filter_type in ["全部", "图像模型"]: all_models.extend([{"name": m, "type": "图像"} for m in image_models])
        if filter_type in ["全部", "视频模型"]: all_models.extend([{"name": m, "type": "视频"} for m in video_models])
        if output_format == "JSON": return (json.dumps(all_models, ensure_ascii=False, indent=2),)
        return ("\n".join([f"• {m['name']} ({m['type']})" for m in all_models]),)


class LK_Gemini_PromptBuilder:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"main_subject": ("STRING", {"multiline": False, "placeholder": "主体描述"})},
            "optional": {
                "action": ("STRING", {"multiline": False, "default": "", "placeholder": "动作/姿态"}),
                "environment": ("STRING", {"multiline": False, "default": "", "placeholder": "环境/背景"}),
                "style": ("STRING", {"multiline": False, "default": "", "placeholder": "艺术风格"}),
                "lighting": ("STRING", {"multiline": False, "default": "", "placeholder": "光照效果"}),
                "quality_tags": ("STRING", {"multiline": False, "default": "masterpiece, best quality, highly detailed"}),
                "additional": ("STRING", {"multiline": True, "default": "", "placeholder": "其他补充"}),
                "separator": ([",", ", ", " | ", "\n"], {"default": ", "})
            }}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("完整提示词",)
    FUNCTION = "build"
    CATEGORY = "LK_Studio/Gemini/工具"

    def build(self, main_subject, action="", environment="", style="", lighting="", 
              quality_tags="", additional="", separator=", "):
        parts = [p.strip() for p in [main_subject, action, environment, style, lighting, quality_tags, additional] if p.strip()]
        return (separator.join(parts),)
