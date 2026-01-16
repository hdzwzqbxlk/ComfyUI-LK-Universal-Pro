# -*- coding: utf-8 -*-
"""视觉理解节点"""

import torch
import os
from typing import Tuple

try:
    from ..utils.api_client import GeminiAPIClient, GeminiAPIError
    from ..utils.image_utils import tensor_to_pil, pil_to_base64, tensor_batch_to_pil_list
    from ..utils.file_utils import read_file_as_base64, get_mime_type
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.api_client import GeminiAPIClient, GeminiAPIError
    from utils.image_utils import tensor_to_pil, pil_to_base64, tensor_batch_to_pil_list
    from utils.file_utils import read_file_as_base64, get_mime_type


class LK_Gemini_VisionAnalyze:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True, "default": "请详细描述这张图像的内容。"}),
            "model": (["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview", "gemini-1.5-flash"],
                      {"default": "gemini-2.5-flash"}),
            "api_key": ("STRING", {"default": ""})
        }, "optional": {
            "output_format": (["详细描述", "简短描述", "SD/FLUX 提示词", "Midjourney 提示词", "标签列表", "JSON 结构"],
                             {"default": "详细描述"}),
            "language": (["中文", "English", "日本語"], {"default": "中文"})
        }}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("分析结果",)
    FUNCTION = "analyze"
    CATEGORY = "LK_Studio/Gemini/视觉"

    def analyze(self, image, prompt, model, api_key, output_format="详细描述", language="中文"):
        if not api_key: return ("错误: 请提供有效的 API 密钥",)
        try:
            client = GeminiAPIClient(api_key)
            pil_images = tensor_batch_to_pil_list(image)
            format_guide = {"详细描述": "请用详细段落描述图像内容。", "简短描述": "请用一两句话简洁描述。",
                "SD/FLUX 提示词": "生成适合 SD/FLUX 的英文提示词。", "Midjourney 提示词": "生成 Midjourney 格式英文提示词。",
                "标签列表": "列出关键标签，逗号分隔。", "JSON 结构": "以JSON格式输出结构化分析结果。"}
            lang_guide = {"中文": "请使用中文。", "English": "Respond in English.", "日本語": "日本語で回答してください。"}
            full_prompt = f"{prompt}\n\n{format_guide.get(output_format, '')}\n{lang_guide.get(language, '')}"
            parts = [{"text": full_prompt}]
            for pil_img in pil_images[:5]:
                parts.append({"inlineData": {"mimeType": "image/png", "data": pil_to_base64(pil_img)}})
            response = client.generate_content(model=model, contents=[{"parts": parts}])
            return (client.parse_text_response(response),)
        except GeminiAPIError as e: return (f"API 错误: {str(e)}",)
        except Exception as e: return (f"错误: {str(e)}",)


class LK_Gemini_DocumentProcess:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "file_path": ("STRING", {"default": "", "placeholder": "输入 PDF 文件路径..."}),
            "prompt": ("STRING", {"multiline": True, "default": "请总结这份文档的主要内容。"}),
            "model": (["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview"], {"default": "gemini-2.5-flash"}),
            "api_key": ("STRING", {"default": ""})
        }, "optional": {"output_type": (["摘要", "全文提取", "关键信息", "结构化数据 (JSON)", "问答"], {"default": "摘要"})}}
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("处理结果", "结构化数据")
    FUNCTION = "process"
    CATEGORY = "LK_Studio/Gemini/视觉"

    def process(self, file_path, prompt, model, api_key, output_type="摘要"):
        if not api_key: return ("错误: 请提供有效的 API 密钥", "")
        if not file_path or not os.path.exists(file_path): return ("错误: 文件路径无效", "")
        try:
            client = GeminiAPIClient(api_key, timeout=120)
            b64_data = read_file_as_base64(file_path)
            if not b64_data: return ("错误: 无法读取文件", "")
            mime = get_mime_type(file_path)
            output_guide = {"摘要": "提供简洁摘要。", "全文提取": "提取所有文本内容。", 
                "关键信息": "列出关键信息和数据。", "结构化数据 (JSON)": "以JSON格式输出。", "问答": "回答问题。"}
            full_prompt = f"{prompt}\n\n{output_guide.get(output_type, '')}"
            contents = [{"parts": [{"text": full_prompt}, {"inlineData": {"mimeType": mime, "data": b64_data}}]}]
            response = client.generate_content(model=model, contents=contents)
            result = client.parse_text_response(response)
            structured = ""
            if output_type == "结构化数据 (JSON)":
                import json
                try:
                    start, end = result.find("{"), result.rfind("}") + 1
                    if start != -1 and end > start:
                        structured = json.dumps(json.loads(result[start:end]), ensure_ascii=False, indent=2)
                except: structured = result
            return (result, structured)
        except GeminiAPIError as e: return (f"API 错误: {str(e)}", "")
        except Exception as e: return (f"错误: {str(e)}", "")
