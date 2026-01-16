# -*- coding: utf-8 -*-
"""
图像处理工具函数
提供 ComfyUI Tensor 与 PIL Image 之间的转换，以及 Base64 编码等功能
"""

import torch
import numpy as np
import base64
import io
from PIL import Image
from typing import Optional, Union, Tuple, List


def tensor_to_pil(image_tensor: torch.Tensor) -> Optional[Image.Image]:
    """将 ComfyUI 图像 Tensor 转换为 PIL Image"""
    if image_tensor is None:
        return None
    if len(image_tensor.shape) == 4:
        img = image_tensor[0]
    else:
        img = image_tensor
    img_np = (255.0 * img.cpu().numpy()).clip(0, 255).astype(np.uint8)
    return Image.fromarray(img_np, mode="RGB")


def pil_to_tensor(image: Image.Image) -> torch.Tensor:
    """将 PIL Image 转换为 ComfyUI 图像 Tensor"""
    if image.mode != "RGB":
        image = image.convert("RGB")
    img_np = np.array(image).astype(np.float32) / 255.0
    return torch.from_numpy(img_np)[None,]


def pil_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """将 PIL Image 转换为 Base64 编码字符串"""
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def base64_to_pil(b64_string: str) -> Image.Image:
    """将 Base64 编码字符串转换为 PIL Image"""
    image_bytes = base64.b64decode(b64_string)
    return Image.open(io.BytesIO(image_bytes))


def bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """将字节数据转换为 PIL Image"""
    return Image.open(io.BytesIO(image_bytes))


def resize_image(image: Image.Image, max_size: int = None,
                 target_size: Tuple[int, int] = None,
                 maintain_aspect: bool = True) -> Image.Image:
    """调整图像大小"""
    if target_size:
        if maintain_aspect:
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            return image
        else:
            return image.resize(target_size, Image.Resampling.LANCZOS)
    if max_size:
        width, height = image.size
        if width > max_size or height > max_size:
            ratio = max_size / max(width, height)
            new_size = (int(width * ratio), int(height * ratio))
            return image.resize(new_size, Image.Resampling.LANCZOS)
    return image


def tensor_batch_to_pil_list(image_tensor: torch.Tensor) -> List[Image.Image]:
    """将批量图像 Tensor 转换为 PIL Image 列表"""
    if image_tensor is None:
        return []
    if len(image_tensor.shape) == 3:
        image_tensor = image_tensor.unsqueeze(0)
    images = []
    for i in range(image_tensor.shape[0]):
        img = image_tensor[i]
        img_np = (255.0 * img.cpu().numpy()).clip(0, 255).astype(np.uint8)
        images.append(Image.fromarray(img_np, mode="RGB"))
    return images


def create_empty_image(width: int = 512, height: int = 512,
                       color: Tuple[int, int, int] = (0, 0, 0)) -> torch.Tensor:
    """创建空白图像 Tensor"""
    img = Image.new("RGB", (width, height), color)
    return pil_to_tensor(img)
