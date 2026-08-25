# -*- coding: utf-8 -*-
"""通用 OpenAI 兼容 API 客户端。

对接任意遵循 OpenAI 协议的端点（OpenAI / Ollama / OpenRouter / DeepSeek /
火山方舟 / 硅基流动 / 自定义）。本插件「通用 API 节点」的核心依赖。
"""

import requests
import json
import time
from typing import Optional, Dict, Any, List, Union, Tuple


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
      - images/edits     ：图像编辑（兼容端点支持时）
      - videos/generations：视频生成（兼容端点支持时）
      - models           ：自动拉取可用模型列表
    """

    def __init__(self, base_url: str, api_key: str = "", timeout: int = 120,
                 max_retries: int = 3, retry_delay: float = 2.0,
                 fallback_base_url: str = "", fallback_api_key: str = "",
                 debug: bool = False):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.fallback_base_url = fallback_base_url.rstrip("/") if fallback_base_url else ""
        self.fallback_api_key = fallback_api_key or ""
        self.debug = debug
        self.session = requests.Session()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        self.session.headers.update(headers)
        # 备用端点会话（headers 可能不同）
        self._fallback_session = None

    def _debug_log(self, msg: str):
        if self.debug:
            print(f"[LK-Universal][DEBUG] {msg}")

    @staticmethod
    def merge_extra(extra_json_str: str, explicit: dict = None) -> dict:
        """解析用户自定义参数 JSON 并合并显式参数（显式优先）。

        extra_json 示例：{"frequency_penalty": 0.5, "user": "lk", "top_k": 40}
        非法 JSON 返回 {}（不抛错，容错优先）。
        """
        merged = {}
        if extra_json_str:
            try:
                parsed = json.loads(extra_json_str)
                if isinstance(parsed, dict):
                    merged.update(parsed)
            except Exception:
                print(f"[LK-Universal] ⚠️ extra_json 不是合法 JSON 对象，已忽略: {extra_json_str[:100]}")
        if explicit:
            merged.update(explicit)
        return merged

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
                        top_p: float = 1.0, stream: bool = False, **extra) -> Union[dict, Any]:
        """标准 chat/completions 调用。

        messages 元素形如 {"role": "user"/"system"/"assistant",
                            "content": str | [ {"type":"text"/"image_url", ...} ]}
        多模态图片以 image_url(data:image/png;base64,...) 形式注入 content 数组。
        stream=True 时返回原始 response（SSE 流，由调用方消费）。
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
        }
        # 仅保留有效可选参数（含 extra_json 透传的自定义参数）
        for k, v in extra.items():
            if v is not None:
                payload[k] = v
        if stream:
            return self._request_stream("/chat/completions", payload)
        self._debug_log(f"chat/completions payload keys: {sorted(payload.keys())}")
        return self._request("POST", "/chat/completions", json_body=payload)

    def _request_stream(self, endpoint: str, payload: dict):
        """发起 SSE 流式请求，返回原始 response（iter_content 消费）。

        流式请求不做重试/故障转移（避免重复生成），失败直接抛错。
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        body = dict(payload)
        body["stream"] = True
        resp = self.session.post(url, json=body, timeout=self.timeout, stream=True)
        if resp.status_code >= 400:
            try:
                msg = resp.json().get("error", {})
                if isinstance(msg, dict):
                    msg = msg.get("message", str(resp.text[:300]))
            except Exception:
                msg = resp.text[:300]
            raise UniversalAPIError(f"API 错误 {resp.status_code}: {msg}",
                                    status_code=resp.status_code)
        resp.raise_for_status()
        return resp

    @staticmethod
    def consume_sse_stream(response) -> Tuple[str, str]:
        """消费 OpenAI SSE 流，返回 (完整文本, 思考过程)。

        兼容 reasoning_content（DeepSeek-R1 风格）与普通 delta.content。
        """
        text_parts = []
        reasoning_parts = []
        for line in response.iter_lines(decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            data_str = line[len("data:"):].strip()
            if data_str == "[DONE]":
                break
            try:
                chunk = json.loads(data_str)
            except Exception:
                continue
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta", {}) or {}
            rc = delta.get("reasoning_content")
            if rc:
                reasoning_parts.append(rc)
            c = delta.get("content")
            if c:
                text_parts.append(c)
        return ("".join(text_parts), "".join(reasoning_parts))

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

    # ---- 图像编辑（兼容端点支持时）----------------------------------------
    def edit_image(self, model: str, prompt: str, image_b64: List[str] = None,
                   mask_b64: str = None, n: int = 1, size: str = "1024x1024",
                   response_format: str = "b64_json", **extra) -> dict:
        """/images/edits：以图 + 提示词编辑/重绘。

        image_b64: 待编辑图像 base64 列表（部分端点只取第一张）。
        mask_b64 : 可选遮罩，白色区域被重绘（DALL·E 系列语义）。
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "response_format": response_format,
        }
        if image_b64:
            payload["image"] = image_b64[0]
        if mask_b64:
            payload["mask"] = mask_b64
        for k, v in extra.items():
            if v is not None:
                payload[k] = v
        return self._request("POST", "/images/edits", json_body=payload, allow_fallback=False)

    # ---- 视频生成（兼容端点支持时）----------------------------------------
    def generate_video(self, model: str, prompt: str, duration: float = 5.0,
                       aspect_ratio: str = "16:9", n: int = 1, **extra) -> dict:
        """/videos/generations：文生视频（OpenAI 兼容扩展端点）。

        返回结构兼容 {"data":[{"b64_json":...} | {"url":...}]}。
        不支持的端点会抛 UniversalAPIError（调用方提示「该端点未开放视频能力」）。
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "duration": duration,
            "aspect_ratio": aspect_ratio,
            "n": n,
        }
        for k, v in extra.items():
            if v is not None:
                payload[k] = v
        return self._request("POST", "/videos/generations", json_body=payload, allow_fallback=False)

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

    @staticmethod
    def parse_tool_calls(response: dict) -> List[dict]:
        """提取 assistant message 的 tool_calls（function calling）。

        返回 [{ "id", "name", "arguments"(已解析 dict) }, ...]。
        无 tool_calls 时返回空列表。
        """
        out = []
        try:
            msg = response["choices"][0]["message"]
            for tc in msg.get("tool_calls", []) or []:
                if tc.get("type") != "function":
                    continue
                fn = tc.get("function", {})
                raw_args = fn.get("arguments", "") or ""
                try:
                    args = json.loads(raw_args) if raw_args.strip() else {}
                except Exception:
                    args = {"__raw__": raw_args}
                out.append({
                    "id": tc.get("id", ""),
                    "name": fn.get("name", ""),
                    "arguments": args,
                })
        except Exception:
            pass
        return out

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """粗略 token 估算：中文按字、英文按词，约 1 token/词。

        仅用于「单次请求预算」提示，非精确计数。
        """
        if not text:
            return 0
        # CJK 字符每个约 1 token，其余按空白分词
        cjk = sum(1 for ch in text if ord(ch) > 0x2E80)
        non_cjk = len(text) - cjk
        words = max(1, len(text.split()) - cjk) if non_cjk > 0 else 0
        return cjk + words
