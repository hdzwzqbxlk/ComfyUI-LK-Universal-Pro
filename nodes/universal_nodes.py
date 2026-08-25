# -*- coding: utf-8 -*-
"""
通用 API 节点（Universal Nodes）

面向「任意 OpenAI 兼容 API 接口」的通用能力，配合 utils/provider_registry 的
全局模型缓存实现「自动拉取模型列表」。

分类（与 Gemini 系列节点对齐颗粒度）：
  工具  (LK_Studio/通用 API/工具)  : APIConfig / ModelFetcher / HealthCheck / ModelCompare
  文本  (LK_Studio/通用 API/文本)  : TextGen / Chat(多轮) / Session(会话管理)
  图像  (LK_Studio/通用 API/图像)  : ImageGen / ImageEdit
  视频  (LK_Studio/通用 API/视频)  : VideoGen
  视觉  (LK_Studio/通用 API/视觉)  : Vision(多图理解)
  高级  (LK_Studio/通用 API/高级)  : Structured / ToolUse / BatchChat / TokenEstimate

模型下拉框选项来自 UNIVERSAL_MODEL_CACHE，用户在 ModelFetcher 拉取成功后
点击 ComfyUI 节点上的刷新按钮即可看到最新模型。
"""

import json
import os
import time
from typing import Tuple, List, Dict, Any

try:
    from ..utils.api_client import UniversalAPIClient, UniversalAPIError
    from ..utils.provider_registry import (
        PROVIDER_ORDER, UNIVERSAL_MODEL_CACHE, get_cached_models,
        get_provider_base_url, provider_needs_key, resolve_base_url,
    )
    from ..utils.image_utils import (
        tensor_batch_to_pil_list, pil_to_base64, pil_to_tensor,
        base64_to_pil, create_empty_image,
    )
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.api_client import UniversalAPIClient, UniversalAPIError
    from utils.provider_registry import (
        PROVIDER_ORDER, UNIVERSAL_MODEL_CACHE, get_cached_models,
        get_provider_base_url, provider_needs_key, resolve_base_url,
    )
    from utils.image_utils import (
        tensor_batch_to_pil_list, pil_to_base64, pil_to_tensor,
        base64_to_pil, create_empty_image,
    )


# ---------------------------------------------------------------------------
# 公共辅助
# ---------------------------------------------------------------------------
def _load_history(history_str: str) -> List[dict]:
    """安全解析多轮历史 JSON（容错：解析失败返回空列表）。"""
    if not history_str:
        return []
    try:
        hist = json.loads(history_str)
        return hist if isinstance(hist, list) else []
    except Exception:
        return []


def _save_history(messages: List[dict], limit: int = 20) -> str:
    """截断并序列化历史，避免无限膨胀。"""
    if len(messages) > limit:
        messages = messages[-limit:]
    return json.dumps(messages, ensure_ascii=False)


def _images_to_b64(image, max_count: int = 5) -> List[str]:
    """ComfyUI IMAGE tensor -> PNG base64 列表。"""
    out = []
    if image is None:
        return out
    for pil_img in tensor_batch_to_pil_list(image)[:max_count]:
        out.append(pil_to_base64(pil_img))
    return out


def _b64_to_image_tensor(b64_list: List[str]):
    """base64 图像列表 -> ComfyUI IMAGE tensor（批量）。"""
    import torch
    tensors = [pil_to_tensor(base64_to_pil(b)) for b in b64_list if b]
    if not tensors:
        return create_empty_image(8, 8)
    return tensors[0] if len(tensors) == 1 else torch.cat(tensors, dim=0)


def _truncate(text: str, n: int = 2000) -> str:
    return text if len(text) <= n else text[:n] + f"\n...（已截断，共 {len(text)} 字符）"


# ===========================================================================
# 工具类
# ===========================================================================
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

    RETURN_TYPES = ("STRING", "STRING", "INT", "INT", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("Base URL", "API 密钥", "超时", "重试次数", "Base URL (备)", "API 密钥 (备)", "状态")
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


class LK_Universal_HealthCheck:
    """端点健康检查：拉取 /models 并测量往返延迟，验证端点可达 + 鉴权有效。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "timeout": ("INT", {"default": 30, "min": 5, "max": 120, "step": 5}),
        }}

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("状态", "是否可用")
    FUNCTION = "check"
    CATEGORY = "LK_Studio/通用 API/工具"

    def check(self, base_url, api_key="", timeout=30):
        if not base_url:
            return ("错误: 请提供 base_url", False)
        try:
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=1)
            t0 = time.time()
            models = client.list_models()
            cost = time.time() - t0
            n = len(models)
            return (f"✅ 可用 | 延迟 {cost:.2f}s | 模型数 {n} | {base_url}", True)
        except Exception as e:
            return (f"❌ 不可用: {str(e)}", False)


class LK_Universal_ModelCompare:
    """对比两个端点的模型列表：主有/备有/共有，辅助做故障转移选型。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "primary_base_url": ("STRING", {"default": "https://api.openai.com/v1", "placeholder": "主端点 base_url"}),
            "primary_api_key": ("STRING", {"default": ""}),
            "secondary_base_url": ("STRING", {"default": "http://127.0.0.1:11434/v1", "placeholder": "备用端点 base_url"}),
            "secondary_api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "timeout": ("INT", {"default": 30, "min": 5, "max": 120, "step": 5}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("对比报告",)
    FUNCTION = "compare"
    CATEGORY = "LK_Studio/通用 API/工具"

    def compare(self, primary_base_url, primary_api_key, secondary_base_url,
                secondary_api_key, timeout=30):
        def _list(url, key):
            if not url:
                return None, "未提供 base_url"
            try:
                c = UniversalAPIClient(url, key, timeout=timeout, max_retries=1)
                return c.list_models(), None
            except Exception as e:
                return None, str(e)
        p, pe = _list(primary_base_url, primary_api_key)
        s, se = _list(secondary_base_url, secondary_api_key)
        if pe or se:
            return (f"主端点: {'OK' if p is not None else pe}\n"
                    f"备端点: {'OK' if s is not None else se}")
        ps, ss = set(p), set(s)
        only_p = sorted(ps - ss)
        only_s = sorted(ss - ps)
        common = sorted(ps & ss)
        lines = [
            f"主端点模型: {len(p)}  备端点模型: {len(s)}  共有: {len(common)}",
            f"\n— 仅主端点 ({len(only_p)}) —",
            "\n".join(f"  • {m}" for m in only_p) or "  （无）",
            f"\n— 仅备用端点 ({len(only_s)}) —",
            "\n".join(f"  • {m}" for m in only_s) or "  （无）",
            f"\n— 共有 ({len(common)}) —",
            "\n".join(f"  • {m}" for m in common) or "  （无）",
        ]
        return ("\n".join(lines),)


# ===========================================================================
# 文本类
# ===========================================================================
class LK_Universal_TextGen:
    """通用文生文（单轮）：不含历史，最轻量的文本生成入口。"""

    @classmethod
    def INPUT_TYPES(cls):
        models = get_cached_models()
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "输入提示词..."}),
            "model": (models, {"default": models[0] if models else "gpt-4o"}),
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "system_instruction": ("STRING", {"multiline": True, "default": ""}),
            "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 65536, "step": 256}),
            "top_p": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.05}),
            "timeout": ("INT", {"default": 120, "min": 10, "max": 600, "step": 10}),
            "fallback_base_url": ("STRING", {"default": "", "placeholder": "备用端点 base_url（主端点失败自动回退）"}),
            "fallback_api_key": ("STRING", {"default": "", "placeholder": "备用端点密钥（留空沿用主密钥）"}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("回复", "思考过程")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/通用 API/文本"

    def generate(self, prompt, model, base_url, api_key, system_instruction="",
                 temperature=1.0, max_tokens=2048, top_p=1.0, timeout=120,
                 fallback_base_url="", fallback_api_key=""):
        if not base_url:
            return ("错误: 请提供 base_url", "")
        try:
            fb_key = fallback_api_key if fallback_api_key else api_key
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=3,
                                        fallback_base_url=fallback_base_url, fallback_api_key=fb_key)
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            resp = client.chat_completion(model=model, messages=messages,
                                          temperature=temperature, max_tokens=max_tokens, top_p=top_p)
            reply = client.parse_chat_text(resp)
            reasoning = client.parse_chat_reasoning(resp)
            if resp.get("_fallback_used"):
                reply = f"[已回退至备用端点] {reply}"
            return (reply, reasoning)
        except UniversalAPIError as e:
            return (f"API 错误: {str(e)}", "")
        except Exception as e:
            return (f"错误: {str(e)}", "")


class LK_Universal_Chat:
    """通用多轮对话（纯文本）：传入历史可链式多轮，返回更新后的历史 JSON。

    注：多模态视觉请使用「视觉」分类的 LK_Universal_Vision 节点。
    """

    @classmethod
    def INPUT_TYPES(cls):
        models = get_cached_models()
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "输入提示词..."}),
            "model": (models, {"default": models[0] if models else "gpt-4o"}),
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "history": ("STRING", {"multiline": True, "default": "", "placeholder": "多轮历史 JSON（可选）"}),
            "system_instruction": ("STRING", {"multiline": True, "default": ""}),
            "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 65536, "step": 256}),
            "timeout": ("INT", {"default": 120, "min": 10, "max": 600, "step": 10}),
            "fallback_base_url": ("STRING", {"default": "", "placeholder": "备用端点 base_url"}),
            "fallback_api_key": ("STRING", {"default": "", "placeholder": "备用端点密钥（留空沿用主密钥）"}),
        }}

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("回复", "思考过程", "更新历史")
    FUNCTION = "chat"
    CATEGORY = "LK_Studio/通用 API/文本"

    def chat(self, prompt, model, base_url, api_key, history="", system_instruction="",
             temperature=1.0, max_tokens=2048, timeout=120, fallback_base_url="", fallback_api_key=""):
        if not base_url:
            return ("错误: 请提供 base_url", "", history)
        try:
            fb_key = fallback_api_key if fallback_api_key else api_key
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=3,
                                        fallback_base_url=fallback_base_url, fallback_api_key=fb_key)
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.extend(_load_history(history))
            messages.append({"role": "user", "content": prompt})

            resp = client.chat_completion(model=model, messages=messages,
                                          temperature=temperature, max_tokens=max_tokens)
            reply = client.parse_chat_text(resp)
            reasoning = client.parse_chat_reasoning(resp)
            if resp.get("_fallback_used"):
                reply = f"[已回退至备用端点] {reply}" if reply else reply

            messages.append({"role": "assistant", "content": reply})
            return (reply, reasoning, _save_history(messages))
        except UniversalAPIError as e:
            return (f"API 错误: {str(e)}", "", history)
        except Exception as e:
            return (f"错误: {str(e)}", "", history)


class LK_Universal_Session:
    """会话管理：合并/裁剪/清空历史 JSON，便于在工作流中编排多轮上下文。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "history_a": ("STRING", {"multiline": True, "default": "", "placeholder": "历史 A（JSON 数组）"}),
        }, "optional": {
            "history_b": ("STRING", {"multiline": True, "default": "", "placeholder": "历史 B（可选，追加到 A 后）"}),
            "max_messages": ("INT", {"default": 20, "min": 1, "max": 100, "step": 1}),
            "reset": ("BOOLEAN", {"default": False}),
        }}

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("合并历史", "消息条数")
    FUNCTION = "manage"
    CATEGORY = "LK_Studio/通用 API/文本"

    def manage(self, history_a, history_b="", max_messages=20, reset=False):
        if reset:
            return ("[]", 0)
        merged = _load_history(history_a) + _load_history(history_b)
        merged = merged[-max_messages:]
        return (_save_history(merged, limit=max_messages), len(merged))


# ===========================================================================
# 图像类
# ===========================================================================
class LK_Universal_ImageGen:
    """通用文生图：调用 /images/generations（兼容端点支持时）。"""

    @classmethod
    def INPUT_TYPES(cls):
        models = get_cached_models()
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "图像描述..."}),
            "model": (models, {"default": models[0] if models else "gpt-4o"}),
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "n": ("INT", {"default": 1, "min": 1, "max": 4}),
            "size": (["1024x1024", "1792x1024", "1024x1792", "512x512", "256x256"], {"default": "1024x1024"}),
            "timeout": ("INT", {"default": 180, "min": 10, "max": 600, "step": 10}),
        }}

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "状态")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/通用 API/图像"

    def generate(self, prompt, model, base_url, api_key, n=1, size="1024x1024", timeout=180):
        if not base_url:
            return (create_empty_image(8, 8), "错误: 请提供 base_url")
        try:
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=2)
            resp = client.generate_image(model=model, prompt=prompt, n=n, size=size)
            b64_list = client.parse_image_b64(resp)
            if not b64_list:
                return (create_empty_image(8, 8), "端点未返回图像数据（可能不支持 /images/generations）")
            return (_b64_to_image_tensor(b64_list), f"已生成 {len(b64_list)} 张")
        except UniversalAPIError as e:
            return (create_empty_image(8, 8), f"API 错误: {str(e)}")
        except Exception as e:
            return (create_empty_image(8, 8), f"错误: {str(e)}")


class LK_Universal_ImageEdit:
    """通用图生图/编辑：调用 /images/edits（待编辑图 + 提示词，可选遮罩）。"""

    @classmethod
    def INPUT_TYPES(cls):
        models = get_cached_models()
        return {"required": {
            "image": ("IMAGE",),
            "prompt": ("STRING", {"multiline": True, "placeholder": "编辑指令..."}),
            "model": (models, {"default": models[0] if models else "gpt-4o"}),
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "mask": ("IMAGE",),
            "n": ("INT", {"default": 1, "min": 1, "max": 4}),
            "size": (["1024x1024", "1792x1024", "1024x1792"], {"default": "1024x1024"}),
            "timeout": ("INT", {"default": 180, "min": 10, "max": 600, "step": 10}),
        }}

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图像", "状态")
    FUNCTION = "edit"
    CATEGORY = "LK_Studio/通用 API/图像"

    def edit(self, image, prompt, model, base_url, api_key, mask=None, n=1, size="1024x1024", timeout=180):
        if not base_url:
            return (create_empty_image(8, 8), "错误: 请提供 base_url")
        try:
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=2)
            img_b64 = _images_to_b64(image, max_count=1)
            mask_b64 = _images_to_b64(mask, max_count=1)[0] if mask is not None else None
            resp = client.edit_image(model=model, prompt=prompt, image_b64=img_b64,
                                     mask_b64=mask_b64, n=n, size=size)
            b64_list = client.parse_image_b64(resp)
            if not b64_list:
                return (create_empty_image(8, 8), "端点未返回图像数据（可能不支持 /images/edits）")
            return (_b64_to_image_tensor(b64_list), f"已编辑 {len(b64_list)} 张")
        except UniversalAPIError as e:
            return (create_empty_image(8, 8), f"API 错误: {str(e)}")
        except Exception as e:
            return (create_empty_image(8, 8), f"错误: {str(e)}")


# ===========================================================================
# 视频类
# ===========================================================================
class LK_Universal_VideoGen:
    """通用文生视频：调用 /videos/generations（兼容端点支持时）。

    返回结果说明（取决于端点）：URL 直链 或 base64 片段。
    若端点未开放视频能力，会明确提示而非静默失败。
    """

    @classmethod
    def INPUT_TYPES(cls):
        models = get_cached_models()
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "视频描述..."}),
            "model": (models, {"default": models[0] if models else "gpt-4o"}),
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "duration": ("FLOAT", {"default": 5.0, "min": 1.0, "max": 60.0, "step": 1.0}),
            "aspect_ratio": (["16:9", "9:16", "1:1"], {"default": "16:9"}),
            "timeout": ("INT", {"default": 300, "min": 30, "max": 1200, "step": 30}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("结果",)
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/通用 API/视频"

    def generate(self, prompt, model, base_url, api_key, duration=5.0, aspect_ratio="16:9", timeout=300):
        if not base_url:
            return ("错误: 请提供 base_url",)
        try:
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=2)
            resp = client.generate_video(model=model, prompt=prompt, duration=duration, aspect_ratio=aspect_ratio)
            # 兼容 url 或 b64
            items = resp.get("data", []) if isinstance(resp, dict) else []
            if not items:
                return ("端点未返回视频数据（可能不支持 /videos/generations，或任务异步未完成）",)
            parts = []
            for it in items:
                if "url" in it:
                    parts.append(f"[URL] {it['url']}")
                elif "b64_json" in it:
                    parts.append(f"[B64] 长度 {len(it['b64_json'])}")
                else:
                    parts.append(str(it)[:200])
            return ("\n".join(parts),)
        except UniversalAPIError as e:
            return (f"API 错误: {str(e)}（该端点可能未开放视频能力）",)
        except Exception as e:
            return (f"错误: {str(e)}",)


# ===========================================================================
# 视觉类
# ===========================================================================
class LK_Universal_Vision:
    """通用视觉理解：多图 + 文本，专注图文对话（与纯文本 Chat 分离）。"""

    @classmethod
    def INPUT_TYPES(cls):
        models = get_cached_models()
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "关于图像的问题..."}),
            "model": (models, {"default": models[0] if models else "gpt-4o"}),
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "image": ("IMAGE",),
            "history": ("STRING", {"multiline": True, "default": "", "placeholder": "多轮历史 JSON（可选）"}),
            "system_instruction": ("STRING", {"multiline": True, "default": ""}),
            "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 65536, "step": 256}),
            "timeout": ("INT", {"default": 120, "min": 10, "max": 600, "step": 10}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("回复", "更新历史")
    FUNCTION = "understand"
    CATEGORY = "LK_Studio/通用 API/视觉"

    def understand(self, prompt, model, base_url, api_key, image=None, history="",
                   system_instruction="", temperature=1.0, max_tokens=2048, timeout=120):
        if not base_url:
            return ("错误: 请提供 base_url", history)
        try:
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=3)
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.extend(_load_history(history))

            images_b64 = _images_to_b64(image, max_count=8)
            if images_b64:
                messages.append({"role": "user", "content": client.build_vision_content(prompt, images_b64)})
            else:
                messages.append({"role": "user", "content": prompt})

            resp = client.chat_completion(model=model, messages=messages,
                                          temperature=temperature, max_tokens=max_tokens)
            reply = client.parse_chat_text(resp)
            messages.append({"role": "assistant", "content": reply})
            return (reply, _save_history(messages))
        except UniversalAPIError as e:
            return (f"API 错误: {str(e)}", history)
        except Exception as e:
            return (f"错误: {str(e)}", history)


# ===========================================================================
# 高级类
# ===========================================================================
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

            try:
                resp = client.chat_completion(
                    model=model, messages=messages,
                    temperature=temperature, max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
            except UniversalAPIError:
                resp = client.chat_completion(
                    model=model, messages=messages,
                    temperature=temperature, max_tokens=max_tokens,
                )
            raw = client.parse_chat_text(resp)
            try:
                parsed = json.loads(raw)
                return (json.dumps(parsed, ensure_ascii=False, indent=2), raw)
            except Exception:
                return (raw, raw)
        except UniversalAPIError as e:
            return ("", f"API 错误: {str(e)}")
        except Exception as e:
            return ("", f"错误: {str(e)}")


class LK_Universal_ToolUse:
    """通用工具调用（Function Calling）：传入工具定义，返回模型选择的调用清单。"""

    @classmethod
    def INPUT_TYPES(cls):
        models = get_cached_models()
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "用户请求..."}),
            "tools": ("STRING", {"multiline": True,
                "default": '[\n  {\n    "type": "function",\n    "function": {\n      "name": "get_weather",\n      "description": "查询天气",\n      "parameters": {"type": "object", "properties": {"city": {"type": "string"}}}\n    }\n  }\n]'}),
            "model": (models, {"default": models[0] if models else "gpt-4o"}),
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "system_instruction": ("STRING", {"multiline": True, "default": "你按需调用提供的工具。"}),
            "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.1}),
            "max_tokens": ("INT", {"default": 2048, "min": 1, "max": 65536, "step": 256}),
            "timeout": ("INT", {"default": 120, "min": 10, "max": 600, "step": 10}),
        }}

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("调用清单(JSON)", "原始响应")
    FUNCTION = "call_tools"
    CATEGORY = "LK_Studio/通用 API/高级"

    def call_tools(self, prompt, tools, model, base_url, api_key, system_instruction="",
                   temperature=0.7, max_tokens=2048, timeout=120):
        if not base_url:
            return ("错误: 请提供 base_url", "")
        try:
            tool_defs = json.loads(tools)
        except json.JSONDecodeError as e:
            return ("", f"工具定义解析错误: {str(e)}")

        try:
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=3)
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            messages.append({"role": "user", "content": prompt})
            resp = client.chat_completion(
                model=model, messages=messages,
                temperature=temperature, max_tokens=max_tokens,
                tools=tool_defs, tool_choice="auto",
            )
            calls = client.parse_tool_calls(resp)
            if not calls:
                text = client.parse_chat_text(resp)
                return ("（模型未触发工具调用）", text)
            return (json.dumps(calls, ensure_ascii=False, indent=2), client.parse_chat_text(resp))
        except UniversalAPIError as e:
            return ("", f"API 错误: {str(e)}")
        except Exception as e:
            return ("", f"错误: {str(e)}")


class LK_Universal_BatchChat:
    """批量对话：一次提交多组提示词（按行分隔），逐条调用后汇总结果。"""

    @classmethod
    def INPUT_TYPES(cls):
        models = get_cached_models()
        return {"required": {
            "prompts": ("STRING", {"multiline": True, "placeholder": "每行一个提示词..."}),
            "model": (models, {"default": models[0] if models else "gpt-4o"}),
            "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
            "api_key": ("STRING", {"default": ""}),
        }, "optional": {
            "system_instruction": ("STRING", {"multiline": True, "default": ""}),
            "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            "max_tokens": ("INT", {"default": 1024, "min": 1, "max": 65536, "step": 256}),
            "timeout": ("INT", {"default": 300, "min": 30, "max": 1200, "step": 30}),
        }}

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("汇总结果", "成功条数")
    FUNCTION = "batch"
    CATEGORY = "LK_Studio/通用 API/高级"

    def batch(self, prompts, model, base_url, api_key, system_instruction="",
              temperature=1.0, max_tokens=1024, timeout=300):
        if not base_url:
            return ("错误: 请提供 base_url", 0)
        items = [p for p in prompts.split("\n") if p.strip()]
        if not items:
            return ("错误: 没有有效提示词（每行一个）", 0)
        try:
            client = UniversalAPIClient(base_url, api_key, timeout=timeout, max_retries=2)
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            out, ok = [], 0
            for i, p in enumerate(items, 1):
                try:
                    resp = client.chat_completion(
                        model=model,
                        messages=messages + [{"role": "user", "content": p}],
                        temperature=temperature, max_tokens=max_tokens,
                    )
                    reply = client.parse_chat_text(resp)
                    ok += 1
                    out.append(f"[#{i}] {p}\n{_truncate(reply)}")
                except Exception as e:
                    out.append(f"[#{i}] {p}\n⚠️ 失败: {str(e)}")
            return ("\n\n".join(out), ok)
        except UniversalAPIError as e:
            return (f"API 错误: {str(e)}", 0)
        except Exception as e:
            return (f"错误: {str(e)}", 0)


class LK_Universal_TokenEstimate:
    """Token 预算预估：按系统/提示/历史/预留输出粗略估算，提前判断是否会超限。"""

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "default": ""}),
        }, "optional": {
            "system_instruction": ("STRING", {"multiline": True, "default": ""}),
            "history": ("STRING", {"multiline": True, "default": "", "placeholder": "多轮历史 JSON（可选）"}),
            "reserved_output_tokens": ("INT", {"default": 1024, "min": 0, "max": 65536, "step": 256}),
            "context_limit": ("INT", {"default": 128000, "min": 1024, "max": 1000000, "step": 1024, "placeholder": "模型上下文上限（仅用于预警）"}),
        }}

    RETURN_TYPES = ("INT", "INT", "STRING")
    RETURN_NAMES = ("输入 Tokens", "合计 Tokens", "明细")
    FUNCTION = "estimate"
    CATEGORY = "LK_Studio/通用 API/高级"

    def estimate(self, prompt, system_instruction="", history="", reserved_output_tokens=1024, context_limit=128000):
        sys_t = UniversalAPIClient.estimate_tokens(system_instruction)
        prompt_t = UniversalAPIClient.estimate_tokens(prompt)
        hist_t = sum(UniversalAPIClient.estimate_tokens(json.dumps(m, ensure_ascii=False))
                     for m in _load_history(history))
        input_t = sys_t + prompt_t + hist_t
        total = input_t + reserved_output_tokens
        over = total > context_limit
        detail = (f"系统指令: {sys_t}\n提示词: {prompt_t}\n历史: {hist_t}\n"
                  f"预留输出: {reserved_output_tokens}\n合计: {total} / 上限 {context_limit}"
                  f"{'  ⚠️ 超出上下文上限' if over else '  ✅ 在安全范围内'}")
        return (input_t, total, detail)
