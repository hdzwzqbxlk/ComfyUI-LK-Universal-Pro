# -*- coding: utf-8 -*-
"""Gemini API 客户端封装"""

import requests
import json
import time
from typing import Optional, Dict, Any, List, Union

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

GEMINI_TEXT_MODELS = ["gemini-3-pro-preview", "gemini-3-flash-preview", "gemini-2.5-pro",
    "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
GEMINI_IMAGE_MODELS = ["gemini-2.5-flash-image", "gemini-3-pro-image-preview"]
GEMINI_VIDEO_MODELS = ["veo-3.1-generate-preview", "veo-3.1-fast-preview", "veo-3", "veo-3-fast", "veo-2"]
IMAGEN_MODELS = ["imagen-3", "imagen-3-fast"]


class GeminiAPIError(Exception):
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class GeminiAPIClient:
    def __init__(self, api_key: str, timeout: int = 60, max_retries: int = 3):
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries

    def _make_request(self, method: str, url: str, payload: dict = None, headers: dict = None) -> dict:
        if headers is None:
            headers = {"Content-Type": "application/json"}
        url = f"{url}{'&' if '?' in url else '?'}key={self.api_key}"
        for attempt in range(self.max_retries):
            try:
                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, timeout=self.timeout)
                else:
                    response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
                data = response.json()
                if response.status_code != 200:
                    raise GeminiAPIError(f"API 请求失败: {data.get('error', {}).get('message', '未知错误')}",
                        status_code=response.status_code, response_data=data)
                return data
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise GeminiAPIError(f"请求超时，已重试 {self.max_retries} 次")
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                raise GeminiAPIError(f"网络请求错误: {str(e)}")

    def generate_content(self, model: str, contents: Union[str, List[dict]], 
                        system_instruction: str = None, generation_config: dict = None,
                        response_modalities: List[str] = None, image_config: dict = None) -> dict:
        url = f"{GEMINI_API_BASE}/models/{model}:generateContent"
        if isinstance(contents, str):
            contents = [{"parts": [{"text": contents}]}]
        payload = {"contents": contents}
        if system_instruction:
            payload["system_instruction"] = {"parts": [{"text": system_instruction}]}
        if generation_config or response_modalities or image_config:
            config = generation_config or {}
            if response_modalities:
                config["responseModalities"] = response_modalities
            if image_config:
                config["imageConfig"] = image_config
            payload["generationConfig"] = config
        return self._make_request("POST", url, payload)

    def generate_image_imagen(self, model: str, prompt: str, aspect_ratio: str = "1:1",
                              sample_count: int = 1, seed: int = None) -> dict:
        url = f"{GEMINI_API_BASE}/models/{model}:predict"
        payload = {"instances": [{"prompt": prompt}], "parameters": {"sampleCount": sample_count, 
            "aspectRatio": aspect_ratio, "outputMimeType": "image/png"}}
        if seed is not None:
            payload["parameters"]["seed"] = seed % 1000000
        return self._make_request("POST", url, payload)

    def generate_video(self, model: str, prompt: str, aspect_ratio: str = "16:9",
                      resolution: str = "720p", first_frame_image: str = None, last_frame_image: str = None) -> dict:
        url = f"{GEMINI_API_BASE}/models/{model}:generateVideos"
        payload = {"prompt": prompt, "config": {"aspectRatio": aspect_ratio, "resolution": resolution}}
        if first_frame_image:
            payload["firstFrameImage"] = {"bytesBase64Encoded": first_frame_image, "mimeType": "image/png"}
        if last_frame_image:
            payload["lastFrameImage"] = {"bytesBase64Encoded": last_frame_image, "mimeType": "image/png"}
        return self._make_request("POST", url, payload)

    def poll_operation(self, operation_name: str, max_wait: int = 600, poll_interval: int = 10) -> dict:
        url = f"{GEMINI_API_BASE}/{operation_name}"
        start_time = time.time()
        while time.time() - start_time < max_wait:
            data = self._make_request("GET", url)
            if data.get("done"):
                return data
            time.sleep(poll_interval)
        raise GeminiAPIError(f"操作超时，等待了 {max_wait} 秒")

    def list_models(self) -> List[dict]:
        data = self._make_request("GET", f"{GEMINI_API_BASE}/models")
        return data.get("models", [])

    @staticmethod
    def get_text_models() -> List[str]: return GEMINI_TEXT_MODELS.copy()
    @staticmethod
    def get_image_models() -> List[str]: return GEMINI_IMAGE_MODELS.copy()
    @staticmethod
    def get_video_models() -> List[str]: return GEMINI_VIDEO_MODELS.copy()
    @staticmethod
    def get_imagen_models() -> List[str]: return IMAGEN_MODELS.copy()

    @staticmethod
    def parse_text_response(response: dict) -> str:
        try:
            candidates = response.get("candidates", [])
            if not candidates: return ""
            parts = candidates[0].get("content", {}).get("parts", [])
            return "\n".join([p["text"] for p in parts if "text" in p])
        except: return ""

    @staticmethod
    def parse_image_response(response: dict) -> List[bytes]:
        import base64
        images = []
        try:
            candidates = response.get("candidates", [])
            if candidates:
                for part in candidates[0].get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        images.append(base64.b64decode(part["inlineData"].get("data", "")))
            for pred in response.get("predictions", []):
                if "bytesBase64Encoded" in pred:
                    images.append(base64.b64decode(pred["bytesBase64Encoded"]))
        except: pass
        return images
