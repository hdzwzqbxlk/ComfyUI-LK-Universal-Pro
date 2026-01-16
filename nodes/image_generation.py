# -*- coding: utf-8 -*-
"""图像生成节点"""

import torch
from typing import Tuple
from PIL import Image

try:
    from ..utils.api_client import GeminiAPIClient, GeminiAPIError
    from ..utils.image_utils import tensor_to_pil, pil_to_tensor, pil_to_base64, bytes_to_pil, create_empty_image
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.api_client import GeminiAPIClient, GeminiAPIError
    from utils.image_utils import tensor_to_pil, pil_to_tensor, pil_to_base64, bytes_to_pil, create_empty_image


class LK_Gemini_ImageGen:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "描述您想要生成的图像..."}),
            "model": (["gemini-2.5-flash-image", "gemini-3-pro-image-preview"], {"default": "gemini-2.5-flash-image"}),
            "aspect_ratio": (["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"], {"default": "1:1"}),
            "api_key": ("STRING", {"default": "", "placeholder": "输入 Gemini API 密钥"})
        }, "optional": {
            "image_size": (["auto", "1K", "2K", "4K"], {"default": "auto"}),
            "response_mode": (["IMAGE+TEXT", "IMAGE_ONLY"], {"default": "IMAGE+TEXT"})
        }}
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "描述文本")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/Gemini/图像"

    def generate(self, prompt, model, aspect_ratio, api_key, image_size="auto", response_mode="IMAGE+TEXT"):
        if not api_key: return (create_empty_image(), "错误: 请提供有效的 API 密钥")
        try:
            client = GeminiAPIClient(api_key, timeout=120)
            modalities = ["Image"] if response_mode == "IMAGE_ONLY" else ["Text", "Image"]
            img_config = {"aspectRatio": aspect_ratio}
            if model == "gemini-3-pro-image-preview" and image_size != "auto":
                img_config["imageSize"] = image_size
            response = client.generate_content(model=model, contents=prompt, 
                response_modalities=modalities, image_config=img_config)
            images = client.parse_image_response(response)
            text = client.parse_text_response(response)
            if images: return (pil_to_tensor(bytes_to_pil(images[0])), text or "图像生成成功")
            return (create_empty_image(), text or "未能生成图像")
        except GeminiAPIError as e: return (create_empty_image(), f"API 错误: {str(e)}")
        except Exception as e: return (create_empty_image(), f"错误: {str(e)}")


class LK_Gemini_ImageEdit:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True, "placeholder": "描述您想要对图像进行的修改..."}),
            "model": (["gemini-2.5-flash-image", "gemini-3-pro-image-preview"], {"default": "gemini-2.5-flash-image"}),
            "api_key": ("STRING", {"default": ""})
        }, "optional": {"aspect_ratio": (["original", "1:1", "16:9", "9:16", "4:3", "3:4"], {"default": "original"})}}
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("编辑后图像", "描述文本")
    FUNCTION = "edit"
    CATEGORY = "LK_Studio/Gemini/图像"

    def edit(self, image, prompt, model, api_key, aspect_ratio="original"):
        if not api_key: return (image, "错误: 请提供有效的 API 密钥")
        try:
            client = GeminiAPIClient(api_key, timeout=120)
            pil_img = tensor_to_pil(image)
            b64 = pil_to_base64(pil_img)
            contents = [{"parts": [{"text": prompt}, {"inlineData": {"mimeType": "image/png", "data": b64}}]}]
            img_config = {} if aspect_ratio == "original" else {"aspectRatio": aspect_ratio}
            response = client.generate_content(model=model, contents=contents, 
                response_modalities=["Text", "Image"], image_config=img_config or None)
            images = client.parse_image_response(response)
            text = client.parse_text_response(response)
            if images: return (pil_to_tensor(bytes_to_pil(images[0])), text or "图像编辑成功")
            return (image, text or "未能生成编辑后的图像")
        except GeminiAPIError as e: return (image, f"API 错误: {str(e)}")
        except Exception as e: return (image, f"错误: {str(e)}")


class LK_Gemini_Imagen:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "描述您想要生成的图像..."}),
            "model": (["imagen-3", "imagen-3-fast"], {"default": "imagen-3"}),
            "aspect_ratio": (["1:1", "16:9", "9:16", "4:3", "3:4"], {"default": "1:1"}),
            "api_key": ("STRING", {"default": ""})
        }, "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 999999})}}
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "状态")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/Gemini/图像"

    def generate(self, prompt, model, aspect_ratio, api_key, seed=0):
        if not api_key: return (create_empty_image(), "错误: 请提供有效的 API 密钥")
        try:
            client = GeminiAPIClient(api_key, timeout=120)
            response = client.generate_image_imagen(model=model, prompt=prompt, 
                aspect_ratio=aspect_ratio, seed=seed if seed > 0 else None)
            images = client.parse_image_response(response)
            if images: return (pil_to_tensor(bytes_to_pil(images[0])), "生成成功")
            return (create_empty_image(), "未能生成图像")
        except GeminiAPIError as e: return (create_empty_image(), f"API 错误: {str(e)}")
        except Exception as e: return (create_empty_image(), f"错误: {str(e)}")
