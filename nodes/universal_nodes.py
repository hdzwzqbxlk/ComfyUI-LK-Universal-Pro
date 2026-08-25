# -*- coding: utf-8 -*-
"""
通用 API 节点（Universal Nodes）

面向「任意 OpenAI 兼容 API 接口」的通用能力，配合 utils/provider_registry 的
全局模型缓存实现「自动拉取模型列表」：

  - LK_Universal_APIConfig    统一配置节点（厂商预设 + 自定义 base_url）
  - LK_Universal_ModelFetcher 拉取指定端点的模型列表并写入全局缓存
  - LK_Universal_Chat         通用对话（文本 + 多模态视觉）
  - LK_Universal_Structured   通用结构化 JSON 输出

模型下拉框选项来自 UNIVERSAL_MODEL_CACHE，用户在 ModelFetcher 拉取成功后
点击 ComfyUI 节点上的刷新按钮即可看到最新模型。
"""

import json
import os
from typing import Tuple, List

try:
    from ..utils.api_client import UniversalAPIClient, UniversalAPIError
    from ..utils.provider_registry import (
        PROVIDER_ORDER, UNIVERSAL_MODEL_CACHE, get_cached_models,
        get_provider_base_url, provider_needs_key, resolve_base_url,
    )
    from ..utils.image_utils import tensor_batch_to_pil_list, pil_to_base64
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.api_client import UniversalAPIClient, UniversalAPIError
    from utils.provider_registry import (
        PROVIDER_ORDER, UNIVERSAL_MODEL_CACHE, get_cached_models,
        get_provider_base_url, provider_needs_key, resolve_base_url,
    )
    from utils.image_utils import tensor_batch_to_pil_list, pil_to_base64


class LK_Universal_APIConfig:
    """统一 API 配置：选择厂商或自定义端点，输出 base_url / api_key 给下游节点。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "provider": (PROVIDER_ORDER, {"default": "OpenAI"}),
            "api_key": ("STRING", {"default": "", "placeholder": "API 密钥（本地 Ollama 可留空）"}),
        }, "optional": {
            "custom_base_url": ("STRING", {"default": "", "placeholder": "自定义端点 base_url，如 http://127.0.0.1:11434/v1"}),
            "timeout": ("INT", {"default": 120, "min": 10, "max": 600, "step": 10}),
            "max_retries": ("INT", {"default": 3, "min": 1, "max": 10}),
            "fallback_provider": (PROVIDER_ORDER, {"default": "Ollama (本地)"}),
            "fallback_custom_base_url": ("STRING", {"default": "", "placeholder": "备用端点 base_url（主端点失败自动回退）"}),
            "fallback_api_key": ("STRING", {"default": "", "placeholder": "备用端点密钥（留空沿用主密钥逻辑：Ollama 可空）"}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "STRING", "STRING")
    RETURN_NAMES = ("Base URL", "API 密钥", "超时", "重试次数", "Base URL (备)", "API 密钥 (备)")
    FUNCTION = "configure"
    CATEGORY = "LK_Studio/通用 API/工具"

    def configure(self, provider, api_key="", custom_base_url="", timeout=120, max_retries=3,
                  fallback_provider="Ollama (本地)", fallback_custom_base_url="", fallback_api_key=""):
        base_url = resolve_base_url(provider, custom_base_url)
        if not base_url:
            return ("", "", timeout, max_retries, "", "", "错误: 自定义端点必须填写 base_url")
        if provider_needs_key(provider) and not api_key:
            base_url_status = "警告: 该厂商通常需要 API 密钥"
        else:
            base_url_status = f"已配置: {provider} @ {base_url}"
        fb_url = resolve_base_url(fallback_provider, fallback_custom_base_url)
        fb_key = fallback_api_key if fallback_api_key else api_key
        return (base_url, api_key, timeout, max_retries, fb_url, fb_key, base_url_status)


class LK_Universal_ModelFetcher:
    """拉取指定端点的模型列表，写入全局缓存供下游节点下拉框刷新使用。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "base_url": ("STRING", {"default": "http://127.0.0.1:11434/v1",
                                     "placeholder": "端点 base_url，如 https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "timeout": ("INT", {"default": 30, "min": 10, "max": 120, "step": 5}),
            "filter_keyword": ("STRING", {"default": "", "placeholder": "仅保留包含关键字的模型（留空=全部）"}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("模型列表",)
    FUNCTION = "fetch"
    CATEGORY = "LK_Studio/通用 API/工具"

    def fetch(self, base_url, api_key="", timeout=30, filter_keyword=""):
        if not base_url:
            return ("错误: 请提供 base_url",)
        try:
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=2)
            models = client.list_models()
            if filter_keyword:
                kw = filter_keyword.lower()
                models = [m for m in models if kw in m.lower()]
            if not models:
                UNIVERSAL_MODEL_CACHE.set_error("端点未返回任何模型")
                return ("未能获取模型列表（端点可能不支持 /models）",)
            UNIVERSAL_MODEL_CACHE.set_models(models, source="拉取")
            # 截断展示，避免超长
            preview = models[:50]
            shown = "\n".join(f"• {m}" for m in preview)
            more = f"\n... 共 {len(models)} 个（已写入缓存，可在对话节点刷新下拉框）" if len(models) > 50 else ""
            return (f"已拉取 {len(models)} 个模型，来源: {base_url}\n{shown}{more}",)
        except UniversalAPIError as e:
            UNIVERSAL_MODEL_CACHE.set_error(str(e))
            return (f"拉取失败: {str(e)}",)
        except Exception as e:
            UNIVERSAL_MODEL_CACHE.set_error(str(e))
            return (f"拉取失败: {str(e)}",)


class LK_Universal_Chat:
    """通用对话节点：文本 + 多模态（图像）输入，兼容任意 OpenAI 端点。"""

    @classmethod
    def INPUT_TYPES(cls):
        # 模型选项从全局缓存读取；下拉框刷新时 ComfyUI 重新调用 INPUT_TYPES
        models = get_cached_models()
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "输入提示词..."}),
            "model": (models, {"default": models[0] if models else "gpt-4o"}),
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "image": ("IMAGE",),
            "system_instruction": ("STRING", {"multiline": True, "default": ""}),
            "history": ("STRING", {"multiline": True, "default": "", "placeholder": "多轮历史 JSON（可选）"}),
            "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 65536, "step": 256}),
            "timeout": ("INT", {"default": 120, "min": 10, "max": 600, "step": 10}),
            "fallback_base_url": ("STRING", {"default": "", "placeholder": "备用端点 base_url（主端点失败自动回退）"}),
            "fallback_api_key": ("STRING", {"default": "", "placeholder": "备用端点密钥（留空沿用主密钥）"}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("回复", "思考过程", "更新历史")
    FUNCTION = "chat"
    CATEGORY = "LK_Studio/通用 API/文本"

    def chat(self, prompt, model, base_url, api_key, image=None,
             system_instruction="", history="", temperature=1.0,
             max_tokens=2048, timeout=120, fallback_base_url="", fallback_api_key=""):
        if not base_url:
            return ("错误: 请提供 base_url", "", history)
        try:
            fb_key = fallback_api_key if fallback_api_key else api_key
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=3,
                                        fallback_base_url=fallback_base_url, fallback_api_key=fb_key)

            # 组装历史
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            if history:
                try:
                    hist = json.loads(history)
                    if isinstance(hist, list):
                        messages.extend(hist)
                except Exception:
                    pass

            # 多模态：图片以 base64 data-url 注入
            images_b64 = []
            if image is not None:
                for pil_img in tensor_batch_to_pil_list(image)[:5]:
                    images_b64.append(pil_to_base64(pil_img))
            if images_b64:
                content = client.build_vision_content(prompt, images_b64)
                messages.append({"role": "user", "content": content})
            else:
                messages.append({"role": "user", "content": prompt})

            resp = client.chat_completion(
                model=model, messages=messages,
                temperature=temperature, max_tokens=max_tokens,
            )
            reply = client.parse_chat_text(resp)
            reasoning = client.parse_chat_reasoning(resp)
            # 若触发 Smart 回退，提示用户
            if resp.get("_fallback_used"):
                reply = f"[已回退至备用端点] {reply}" if reply else reply

            # 更新历史（用于多轮）
            messages.append({"role": "assistant", "content": reply})
            # 仅保留最近 20 条，避免无限膨胀
            if len(messages) > 20:
                messages = messages[-20:]
            new_history = json.dumps(messages, ensure_ascii=False)

            return (reply, reasoning, new_history)
        except UniversalAPIError as e:
            return (f"API 错误: {str(e)}", "", history)
        except Exception as e:
            return (f"错误: {str(e)}", "", history)


class LK_Universal_Structured:
    """通用结构化输出：强制 JSON 返回（兼容 json_object / response_schema 端点）。"""

    @classmethod
    def INPUT_TYPES(cls):
        models = get_cached_models()
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "输入提示词..."}),
            "json_schema": ("STRING", {"multiline": True,
                "default": '{\n  "type": "object",\n  "properties": {\n    "result": {"type": "string"}\n  }\n}'}),
            "model": (models, {"default": models[0] if models else "gpt-4o"}),
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "system_instruction": ("STRING", {"multiline": True, "default": "你只输出符合 schema 的 JSON。"}),
            "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 65536, "step": 256}),
            "timeout": ("INT", {"default": 120, "min": 10, "max": 600, "step": 10}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("JSON 输出", "原始响应")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/通用 API/高级"

    def generate(self, prompt, json_schema, model, base_url, api_key,
                 system_instruction="", temperature=0.7, max_tokens=2048, timeout=120):
        if not base_url:
            return ("错误: 请提供 base_url", "")
        try:
            schema = json.loads(json_schema)
        except json.JSONDecodeError as e:
            return ("", f"JSON Schema 解析错误: {str(e)}")

        try:
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=3)
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})

            # OpenAI 官方用 response_format；兼容端点若不支持则退化为普通请求
            try:
                resp = client.chat_completion(
                    model=model, messages=messages,
                    temperature=temperature, max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
            except UniversalAPIError:
                # 某些端点不支持 response_format，重试一次不带该字段
                resp = client.chat_completion(
                    model=model, messages=messages,
                    temperature=temperature, max_tokens=max_tokens,
                )
            raw = client.parse_chat_text(resp)
            # 尝试格式化并校验是否符合 schema（宽松校验：能解析即为 JSON）
            try:
                parsed = json.loads(raw)
                return (json.dumps(parsed, ensure_ascii=False, indent=2), raw)
            except Exception:
                return (raw, raw)
        except UniversalAPIError as e:
            return ("", f"API 错误: {str(e)}")
        except Exception as e:
            return ("", f"错误: {str(e)}")
