# -*- coding: utf-8 -*-
"""
视频处理工具函数
"""

import os
import base64
from typing import Optional, Tuple

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def save_video(video_bytes: bytes, output_path: str) -> str:
    """保存视频字节数据到文件"""
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(video_bytes)
    return output_path


def load_video(video_path: str) -> bytes:
    """从文件加载视频字节数据"""
    with open(video_path, "rb") as f:
        return f.read()


def video_to_base64(video_path: str) -> str:
    """将视频文件转换为 Base64 编码"""
    video_bytes = load_video(video_path)
    return base64.b64encode(video_bytes).decode("utf-8")


def get_video_output_path(filename: str = None, output_dir: str = None) -> str:
    """获取视频输出路径"""
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), "output", "videos")
    os.makedirs(output_dir, exist_ok=True)
    if filename is None:
        import time
        filename = f"gemini_video_{int(time.time())}.mp4"
    return os.path.join(output_dir, filename)


def get_resolution_dimensions(resolution: str) -> Tuple[int, int]:
    """将分辨率字符串转换为宽高尺寸"""
    resolution_map = {
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "4K": (3840, 2160)
    }
    return resolution_map.get(resolution, (1280, 720))
