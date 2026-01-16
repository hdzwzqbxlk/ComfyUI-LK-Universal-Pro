# -*- coding: utf-8 -*-
"""
文件处理工具函数
"""

import os
import time
import json
import base64
from typing import Optional


def ensure_dir(directory: str) -> str:
    """确保目录存在"""
    os.makedirs(directory, exist_ok=True)
    return directory


def get_output_path(filename: str = None, output_dir: str = None,
                    prefix: str = "gemini", extension: str = ".png") -> str:
    """获取输出文件路径"""
    if output_dir is None:
        comfy_output = os.path.join(os.getcwd(), "output")
        output_dir = comfy_output if os.path.exists(comfy_output) else os.getcwd()
    ensure_dir(output_dir)
    if filename is None:
        timestamp = int(time.time() * 1000)
        filename = f"{prefix}_{timestamp}{extension}"
    return os.path.join(output_dir, filename)


def load_json_file(filepath: str) -> Optional[dict]:
    """加载 JSON 文件"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_json_file(data: dict, filepath: str, indent: int = 2) -> bool:
    """保存数据到 JSON 文件"""
    try:
        ensure_dir(os.path.dirname(filepath) or ".")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
        return True
    except Exception:
        return False


def read_file_as_base64(filepath: str) -> Optional[str]:
    """读取文件并返回 Base64 编码"""
    try:
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        return None


def get_mime_type(filepath: str) -> str:
    """根据文件扩展名获取 MIME 类型"""
    ext = os.path.splitext(filepath)[1].lower()
    mime_types = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".gif": "image/gif", ".webp": "image/webp",
        ".mp4": "video/mp4", ".webm": "video/webm",
        ".pdf": "application/pdf", ".txt": "text/plain", ".json": "application/json"
    }
    return mime_types.get(ext, "application/octet-stream")
