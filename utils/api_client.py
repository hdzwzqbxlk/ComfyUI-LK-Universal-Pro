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


# =============================================================================
# 通用 OpenAI 兼容客户端
# 用于对接任意遵循 OpenAI 协议的端点（OpenAI / Ollama / OpenRouter / DeepSeek /
# 火山方舟 / 硅基流动 / 自定义）。这是「兼容各种标准自定义 API 接口」的核心。
# =============================================================================

class UniversalAPIError(Exception):
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class UniversalAPIClient:
    """OpenAI 兼容 API 客户端。

    通过 base_url + api_key(Bearer) 接入任意兼容端点：
      - chat/completions ：文本 / 多模态（图文）对话
      - images/generations：图像生成（兼容端点支持时）
      - models           ：自动拉取可用模型列表
    """

    def __init__(self, base_url: str, api_key: str = "", timeout: int = 120,
                 max_retries: int = 3, retry_delay: float = 2.0,
                 fallback_base_url: str = "", fallback_api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.fallback_base_url = fallback_base_url.rstrip("/") if fallback_base_url else ""
        self.fallback_api_key = fallback_api_key or ""
        self.session = requests.Session()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        self.session.headers.update(headers)
        # 备用端点会话（headers 可能不同）
        self._fallback_session = None

    def _get_fallback_session(self):
        if self._fallback_session is None:
            s = requests.Session()
            headers = {"Content-Type": "application/json"}
            if self.fallback_api_key:
                headers["Authorization"] = f"Bearer {self.fallback_api_key}"
            s.headers.update(headers)
            self._fallback_session = s
        return self._fallback_session

    def _do_request(self, session, method: str, endpoint: str,
                    json_body: dict = None, raw_data: str = None) -> dict:
        """单次请求（不含重试）。供主/备端点复用。"""
        url = f"{self.base_url if session is self.session else self.fallback_base_url}/{endpoint.lstrip('/')}"
        if method.upper() == "GET":
            resp = session.get(url, timeout=self.timeout)
        else:
            if raw_data is not None:
                resp = session.post(url, data=raw_data, timeout=self.timeout)
            else:
                resp = session.post(url, json=json_body, timeout=self.timeout)
        if 400 <= resp.status_code < 500:
            try:
                body = resp.json()
                msg = body.get("error", {})
                if isinstance(msg, dict):
                    msg = msg.get("message", str(body))
            except Exception:
                msg = resp.text[:500]
            raise UniversalAPIError(f"API 错误 {resp.status_code}: {msg}",
                                    status_code=resp.status_code)
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content:
            return {}
        return resp.json()

    # ---- 底层请求（含 Smart 故障转移）-----------------------------------
    def _request(self, method: str, endpoint: str, json_body: dict = None,
                 raw_data: str = None, allow_fallback: bool = True) -> dict:
        last_exc = None
        # 主端点重试
        for attempt in range(self.max_retries):
            try:
                return self._do_request(self.session, method, endpoint, json_body, raw_data)
            except UniversalAPIError:
                raise
            except Exception as e:
                last_exc = e
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
        # 主端点彻底失败 → Smart 回退到备用端点
        if allow_fallback and self.fallback_base_url:
            try:
                fb = self._get_fallback_session()
                result = self._do_request(fb, method, endpoint, json_body, raw_data)
                # 标记回退成功（用于返回信息提示）
                if isinstance(result, dict):
                    result["_fallback_used"] = True
                return result
            except UniversalAPIError:
                raise
            except Exception as e:
                last_exc = e
        raise UniversalAPIError(f"请求失败（已重试 {self.max_retries} 次）: {last_exc}")

    # ---- 自动拉取模型列表 --------------------------------------------------
    def list_models(self) -> List[str]:
        """拉取 /models 并返回模型 id 列表。

        兼容两种返回结构：
          - OpenAI 规范：{"data": [{"id": "...", ...}, ...]}
          - 部分端点直接返回数组：["m1", "m2", ...]
        """
        try:
            data = self._request("GET", "/models", allow_fallback=False)
        except UniversalAPIError as e:
            # 某些端点（如 Ollama 原生、部分网关）用 /api/tags，尝试兜底
            try:
                alt = self._request("GET", "/api/tags", allow_fallback=False)
                models = [m.get("name") for m in alt.get("models", []) if m.get("name")]
                if models:
                    return models
            except Exception:
                pass
            raise
        if isinstance(data, list):
            return [m if isinstance(m, str) else m.get("id") for m in data if m]
        items = data.get("data", [])
        out = []
        for m in items:
            if isinstance(m, str):
                out.append(m)
            elif isinstance(m, dict) and m.get("id"):
                out.append(m["id"])
        return out

    # ---- 对话 / 补全 -------------------------------------------------------
    def chat_completion(self, model: str, messages: List[dict],
                        temperature: float = 1.0, max_tokens: int = 2048,
                        top_p: float = 1.0, **extra) -> dict:
        """标准 chat/completions 调用。

        messages 元素形如 {"role": "user"/"system"/"assistant",
                            "content": str | [ {"type":"text"/"image_url", ...} ]}
        多模态图片以 image_url(data:image/png;base64,...) 形式注入 content 数组。
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }
        # 仅保留有效可选参数
        for k, v in extra.items():
            if v is not None:
                payload[k] = v
        return self._request("POST", "/chat/completions", json_body=payload)

    # ---- 图像生成（兼容端点支持时）----------------------------------------
    def generate_image(self, model: str, prompt: str, n: int = 1,
                       size: str = "1024x1024", response_format: str = "b64_json",
                       **extra) -> dict:
        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": response_format,
        }
        for k, v in extra.items():
            if v is not None:
                payload[k] = v
        return self._request("POST", "/images/generations", json_body=payload, allow_fallback=False)

    # ---- 响应解析 ----------------------------------------------------------
    @staticmethod
    def parse_chat_text(response: dict) -> str:
        try:
            return response["choices"][0]["message"]["content"] or ""
        except Exception:
            return ""

    @staticmethod
    def parse_chat_reasoning(response: dict) -> str:
        """提取 reasoning_content（DeepSeek-R1 / Qwen 思考链等扩展字段）。"""
        try:
            msg = response["choices"][0]["message"]
            return msg.get("reasoning_content", "") or ""
        except Exception:
            return ""

    @staticmethod
    def parse_image_b64(response: dict) -> List[str]:
        out = []
        try:
            for item in response.get("data", []):
                if "b64_json" in item:
                    out.append(item["b64_json"])
                elif "url" in item:
                    out.append(item["url"])
        except Exception:
            pass
        return out

    @staticmethod
    def build_vision_content(text: str, images_b64: List[str] = None) -> list:
        """构造多模态 content（用于 user message）。

        images_b64: 已编码为 PNG base64 的字符串列表。
        """
        content = []
        if images_b64:
            for b64 in images_b64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"},
                })
        content.append({"type": "text", "text": text})
        return content
