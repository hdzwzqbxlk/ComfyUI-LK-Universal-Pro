# -*- coding: utf-8 -*-
"""
ComfyUI-LK-Universal-Pro 插件
面向「任意 OpenAI 兼容 API」的通用节点集合（工具 / 文本 / 图像 / 视频 / 视觉 / 高级）

作者: CCUT_LK Studio
版本: 2.5.1
许可证: MIT
仓库: https://github.com/hdzwzqbxlk/ComfyUI-LK-Universal-Pro
"""

__version__ = "2.5.1"
__author__ = "CCUT_LK Studio"
__license__ = "MIT"

from .nodes.universal_nodes import (
    LK_Universal_APIConfig, LK_Universal_ModelFetcher, LK_Universal_HealthCheck, LK_Universal_ModelCompare,
    LK_Universal_Chat,
    LK_Universal_ImageGen, LK_Universal_ImageEdit,
    LK_Universal_VideoGen,
    LK_Universal_Vision,
    LK_Universal_Advanced, LK_Universal_BatchChat, LK_Universal_TokenEstimate,
)

import os

# ComfyUI 前端扩展目录（自动加载 web/ 下的 JS 扩展）
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

# 服务端代理：供 web/lk_universal_models.js 调用，按 base_url 拉取真实模型列表
# 填充节点的 model 下拉框，并把结果写入全局 UNIVERSAL_MODEL_CACHE（执行时校验用）
try:
    from server import PromptServer  # type: ignore  # noqa: WPS433
    from aiohttp import web

    @PromptServer.instance.routes.post("/lk_universal/fetch_models")
    async def _lk_universal_fetch_models(request):
        from .utils.api_client import UniversalAPIClient, UniversalAPIError
        from .utils.provider_registry import UNIVERSAL_MODEL_CACHE
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"ok": False, "error": "请求体不是合法 JSON"}, status=400)
        base_url = (data.get("base_url") or "").strip()
        api_key = (data.get("api_key") or "").strip()
        filter_kw = (data.get("filter_keyword") or "").strip()
        if not base_url:
            return web.json_response({"ok": False, "error": "缺少 base_url"}, status=400)
        try:
            client = UniversalAPIClient(base_url, api_key, timeout=30, max_retries=1)
            models = client.list_models()
            if filter_kw:
                k = filter_kw.lower()
                models = [m for m in models if k in m.lower()]
            if models:
                UNIVERSAL_MODEL_CACHE.set_models(models, source="拉取")
            return web.json_response({"ok": True, "models": models})
        except UniversalAPIError as e:
            return web.json_response({"ok": False, "error": str(e)})
        except Exception as e:
            return web.json_response({"ok": False, "error": str(e)})
except Exception:  # PromptServer 未就绪 / aiohttp 缺失时不阻塞插件加载
    pass

NODE_CLASS_MAPPINGS = {
    "LK_Universal_APIConfig": LK_Universal_APIConfig,
    "LK_Universal_ModelFetcher": LK_Universal_ModelFetcher,
    "LK_Universal_HealthCheck": LK_Universal_HealthCheck,
    "LK_Universal_ModelCompare": LK_Universal_ModelCompare,
    "LK_Universal_Chat": LK_Universal_Chat,
    "LK_Universal_ImageGen": LK_Universal_ImageGen,
    "LK_Universal_ImageEdit": LK_Universal_ImageEdit,
    "LK_Universal_VideoGen": LK_Universal_VideoGen,
    "LK_Universal_Vision": LK_Universal_Vision,
    "LK_Universal_Advanced": LK_Universal_Advanced,
    "LK_Universal_BatchChat": LK_Universal_BatchChat,
    "LK_Universal_TokenEstimate": LK_Universal_TokenEstimate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LK_Universal_APIConfig": "🌐 LK 通用 API 配置",
    "LK_Universal_ModelFetcher": "📡 LK 通用 模型获取 (自动拉取)",
    "LK_Universal_HealthCheck": "🩺 LK 通用 端点健康检查",
    "LK_Universal_ModelCompare": "🔍 LK 通用 模型对比",
    "LK_Universal_Chat": "💬 LK 通用 对话 (单轮/多轮)",
    "LK_Universal_ImageGen": "🎨 LK 通用 图像生成",
    "LK_Universal_ImageEdit": "✏️ LK 通用 图像编辑",
    "LK_Universal_VideoGen": "🎬 LK 通用 视频生成 (文/图生视频)",
    "LK_Universal_Vision": "👁️ LK 通用 视觉理解 (多图)",
    "LK_Universal_Advanced": "🧩 LK 通用 高级对话 (结构化/工具调用)",
    "LK_Universal_BatchChat": "📚 LK 通用 批量对话",
    "LK_Universal_TokenEstimate": "🧮 LK 通用 Token 估算",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
