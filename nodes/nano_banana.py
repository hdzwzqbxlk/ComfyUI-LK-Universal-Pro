# -*- coding: utf-8 -*-
"""Nano Banana 图像生成节点 - 仿照 ComfyUI 官方 Google Gemini 图像节点"""

import torch
import os
import random
from typing import Tuple

try:
    from ..utils.api_client import GeminiAPIClient, GeminiAPIError
    from ..utils.image_utils import tensor_to_pil, pil_to_tensor, pil_to_base64, bytes_to_pil, create_empty_image
    from ..utils.file_utils import read_file_as_base64, get_mime_type
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.api_client import GeminiAPIClient, GeminiAPIError
    from utils.image_utils import tensor_to_pil, pil_to_tensor, pil_to_base64, bytes_to_pil, create_empty_image
    from utils.file_utils import read_file_as_base64, get_mime_type


DEFAULT_SYSTEM_PROMPT = """You are an expert image generation engine. You must ALWAYS produce an image.
Interpret all user input—regardless of format, intent, or abstraction—as literal visual directives for image composition.
If a prompt is conversational or lacks specific visual details, you must creatively invent a concrete visual scenario that depicts the concept.
Prioritize generating the visual representation above any text, formatting, or conversational requests."""


class LK_NanoBanana:
    """🍌 LK Nano Banana (Google Gemini 图像) - 使用 gemini-2.5-flash-image 模型"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "输入图像生成提示词...", "dynamicPrompts": True}),
            "model": (["gemini-2.5-flash-image", "gemini-2.5-flash-preview-image"], {"default": "gemini-2.5-flash-image"}),
            "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            "seed_control": (["randomize", "increment", "fixed"], {"default": "randomize"}),
            "aspect_ratio": (["auto", "1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"], {"default": "auto"}),
            "response_modalities": (["IMAGE+TEXT", "IMAGE_ONLY"], {"default": "IMAGE+TEXT"}),
            "api_key": ("STRING", {"default": "", "placeholder": "输入 Gemini API 密钥"})
        }, "optional": {
            "image": ("IMAGE",),
            "file_path": ("STRING", {"default": "", "placeholder": "文件路径（可选）"}),
            "system_prompt": ("STRING", {"multiline": True, "default": DEFAULT_SYSTEM_PROMPT})
        }}
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "文本")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/Gemini/NanoBanana"

    def generate(self, prompt, model, seed, seed_control, aspect_ratio, response_modalities, api_key,
                 image=None, file_path="", system_prompt=None):
        if not api_key: return (create_empty_image(), "错误: 请提供有效的 API 密钥")
        actual_seed = self._process_seed(seed, seed_control)
        try:
            client = GeminiAPIClient(api_key, timeout=120)
            parts = []
            if image is not None:
                parts.append({"inlineData": {"mimeType": "image/png", "data": pil_to_base64(tensor_to_pil(image))}})
            if file_path and os.path.exists(file_path):
                b64 = read_file_as_base64(file_path)
                if b64: parts.append({"inlineData": {"mimeType": get_mime_type(file_path), "data": b64}})
            parts.append({"text": prompt})
            modalities = ["Image"] if response_modalities == "IMAGE_ONLY" else ["Text", "Image"]
            img_config = {"aspectRatio": aspect_ratio} if aspect_ratio != "auto" else {}
            response = client.generate_content(model=model, contents=[{"parts": parts}],
                system_instruction=system_prompt or DEFAULT_SYSTEM_PROMPT, response_modalities=modalities,
                image_config=img_config if img_config else None)
            images = client.parse_image_response(response)
            text = client.parse_text_response(response)
            if images: return (pil_to_tensor(bytes_to_pil(images[0])), text or f"生成成功 (seed: {actual_seed})")
            return (create_empty_image(), text or "未能生成图像")
        except GeminiAPIError as e: return (create_empty_image(), f"API 错误: {str(e)}")
        except Exception as e: return (create_empty_image(), f"错误: {str(e)}")

    def _process_seed(self, seed, seed_control):
        if seed_control == "randomize": return random.randint(0, 0xffffffffffffffff)
        elif seed_control == "increment": return seed + 1
        return seed


class LK_NanoBananaPro:
    """🍌 LK Nano Banana Pro (Google Gemini 图像) - 使用 gemini-3-pro-image-preview 高质量模型"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "输入图像生成提示词...", "dynamicPrompts": True}),
            "model": (["gemini-3-pro-image-preview", "gemini-2.5-pro-image"], {"default": "gemini-3-pro-image-preview"}),
            "seed": ("INT", {"default": 12345, "min": 0, "max": 0xffffffffffffffff}),
            "seed_control": (["fixed", "randomize", "increment"], {"default": "fixed"}),
            "aspect_ratio": (["16:9", "9:16", "1:1", "4:3", "3:4", "3:2", "2:3"], {"default": "16:9"}),
            "resolution": (["1K", "2K", "4K"], {"default": "2K"}),
            "response_modalities": (["IMAGE+TEXT", "IMAGE_ONLY"], {"default": "IMAGE+TEXT"}),
            "api_key": ("STRING", {"default": "", "placeholder": "输入 Gemini API 密钥"})
        }, "optional": {
            "image": ("IMAGE",),
            "file_path": ("STRING", {"default": "", "placeholder": "文件路径（可选）"}),
            "system_prompt": ("STRING", {"multiline": True, "default": DEFAULT_SYSTEM_PROMPT})
        }}
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "文本")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/Gemini/NanoBanana"

    def generate(self, prompt, model, seed, seed_control, aspect_ratio, resolution, response_modalities, api_key,
                 image=None, file_path="", system_prompt=None):
        if not api_key: return (create_empty_image(), "错误: 请提供有效的 API 密钥")
        actual_seed = self._process_seed(seed, seed_control)
        try:
            client = GeminiAPIClient(api_key, timeout=180)
            parts = []
            if image is not None:
                parts.append({"inlineData": {"mimeType": "image/png", "data": pil_to_base64(tensor_to_pil(image))}})
            if file_path and os.path.exists(file_path):
                b64 = read_file_as_base64(file_path)
                if b64: parts.append({"inlineData": {"mimeType": get_mime_type(file_path), "data": b64}})
            parts.append({"text": prompt})
            modalities = ["Image"] if response_modalities == "IMAGE_ONLY" else ["Text", "Image"]
            img_config = {"aspectRatio": aspect_ratio, "imageSize": resolution}
            response = client.generate_content(model=model, contents=[{"parts": parts}],
                system_instruction=system_prompt or DEFAULT_SYSTEM_PROMPT, response_modalities=modalities,
                image_config=img_config)
            images = client.parse_image_response(response)
            text = client.parse_text_response(response)
            if images: return (pil_to_tensor(bytes_to_pil(images[0])), text or f"生成成功 (seed: {actual_seed}, {resolution})")
            return (create_empty_image(), text or "未能生成图像")
        except GeminiAPIError as e: return (create_empty_image(), f"API 错误: {str(e)}")
        except Exception as e: return (create_empty_image(), f"错误: {str(e)}")

    def _process_seed(self, seed, seed_control):
        if seed_control == "randomize": return random.randint(0, 0xffffffffffffffff)
        elif seed_control == "increment": return seed + 1
        return seed
