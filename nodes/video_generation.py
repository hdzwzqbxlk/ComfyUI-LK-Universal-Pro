# -*- coding: utf-8 -*-
"""视频生成节点 (Veo 3.1)"""

import torch
import os
from typing import Tuple

try:
    from ..utils.api_client import GeminiAPIClient, GeminiAPIError
    from ..utils.image_utils import tensor_to_pil, pil_to_base64
    from ..utils.video_utils import save_video, get_video_output_path
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.api_client import GeminiAPIClient, GeminiAPIError
    from utils.image_utils import tensor_to_pil, pil_to_base64
    from utils.video_utils import save_video, get_video_output_path


class LK_Gemini_VideoGen:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "描述您想要生成的视频场景..."}),
            "model": (["veo-3.1-generate-preview", "veo-3.1-fast-preview", "veo-3", "veo-3-fast", "veo-2"],
                      {"default": "veo-3.1-generate-preview"}),
            "api_key": ("STRING", {"default": ""})
        }, "optional": {
            "aspect_ratio": (["16:9", "9:16"], {"default": "16:9"}),
            "resolution": (["720p", "1080p", "4K"], {"default": "720p"}),
            "output_filename": ("STRING", {"default": "", "placeholder": "输出文件名"}),
            "max_wait_time": ("INT", {"default": 600, "min": 60, "max": 1800, "step": 60})
        }}
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("视频路径", "状态信息")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/Gemini/视频"
    OUTPUT_NODE = True

    def generate(self, prompt, model, api_key, aspect_ratio="16:9", resolution="720p",
                 output_filename="", max_wait_time=600):
        if not api_key: return ("", "错误: 请提供有效的 API 密钥")
        try:
            client = GeminiAPIClient(api_key, timeout=max_wait_time)
            response = client.generate_video(model=model, prompt=prompt, 
                aspect_ratio=aspect_ratio, resolution=resolution)
            op_name = response.get("name")
            if not op_name: return ("", "错误: 未能获取操作状态")
            result = client.poll_operation(operation_name=op_name, max_wait=max_wait_time, poll_interval=10)
            if result.get("error"): return ("", f"生成失败: {result['error'].get('message', '未知错误')}")
            videos = result.get("response", {}).get("generatedVideos", [])
            if not videos: return ("", "未能生成视频")
            video_uri = videos[0].get("video", {}).get("uri", "")
            if video_uri: return (video_uri, f"视频生成成功\n路径: {video_uri}")
            return ("", "无法获取视频数据")
        except GeminiAPIError as e: return ("", f"API 错误: {str(e)}")
        except Exception as e: return ("", f"错误: {str(e)}")


class LK_Gemini_Image2Video:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "描述视频内容和动作..."}),
            "model": (["veo-3.1-generate-preview", "veo-3.1-fast-preview", "veo-3"],
                      {"default": "veo-3.1-generate-preview"}),
            "api_key": ("STRING", {"default": ""})
        }, "optional": {
            "first_frame": ("IMAGE",), "last_frame": ("IMAGE",),
            "aspect_ratio": (["16:9", "9:16"], {"default": "16:9"}),
            "max_wait_time": ("INT", {"default": 600, "min": 60, "max": 1800})
        }}
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("视频路径", "状态信息")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/Gemini/视频"

    def generate(self, prompt, model, api_key, first_frame=None, last_frame=None,
                 aspect_ratio="16:9", max_wait_time=600):
        if not api_key: return ("", "错误: 请提供有效的 API 密钥")
        try:
            client = GeminiAPIClient(api_key, timeout=max_wait_time)
            first_b64 = pil_to_base64(tensor_to_pil(first_frame)) if first_frame is not None else None
            last_b64 = pil_to_base64(tensor_to_pil(last_frame)) if last_frame is not None else None
            response = client.generate_video(model=model, prompt=prompt, aspect_ratio=aspect_ratio,
                first_frame_image=first_b64, last_frame_image=last_b64)
            op_name = response.get("name")
            if not op_name: return ("", "错误: 未能获取操作状态")
            result = client.poll_operation(operation_name=op_name, max_wait=max_wait_time, poll_interval=10)
            if result.get("error"): return ("", f"生成失败: {result['error'].get('message', '未知错误')}")
            videos = result.get("response", {}).get("generatedVideos", [])
            if videos:
                video_uri = videos[0].get("video", {}).get("uri", "")
                if video_uri: return (video_uri, f"视频生成成功\n路径: {video_uri}")
            return ("", "无法获取视频数据")
        except GeminiAPIError as e: return ("", f"API 错误: {str(e)}")
        except Exception as e: return ("", f"错误: {str(e)}")
