# -*- coding: utf-8 -*-
"""
Provider Registry — 通用 API 厂商预设 & 全局模型缓存

设计目标：
  1. 内置主流「OpenAI 兼容」厂商的预设（base_url / 默认模型 / 是否需要 api_key），
     让用户在节点里仅需「选择厂商 → 填 key → 拉取模型」三步即可接入任意自定义 API。
  2. 维护一个进程级全局模型缓存 UNIVERSAL_MODEL_LIST，供节点下拉框在
     点击 ComfyUI 的刷新按钮（refresh）时读取，实现「自动拉取模型列表」。

任何兼容 OpenAI 协议的接口都可被接入：
  - OpenAI            https://api.openai.com/v1
  - Ollama (本地)      http://127.0.0.1:11434/v1
  - OpenRouter        https://openrouter.ai/api/v1
  - DeepSeek          https://api.deepseek.com/v1
  - Together.ai       https://api.together.xyz/v1
  - Venus / 火山方舟   https://ark.cn-beijing.volces.com/api/v3  (OpenAI 兼容)
  - 自定义端点         (用户自行填写任意 URL)
"""

from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# 厂商预设表
# ---------------------------------------------------------------------------
# 字段说明：
#   base_url : API 基址（不含末尾 /chat/completions，仅到 /v1 或版本前缀）
#   need_key : 是否需要 api_key（本地 Ollama 通常不需要）
#   models   : 该厂商的「热门默认模型」，仅作为初始占位；真实列表由运行时拉取覆盖
#   note     : 备注，展示给用户
PROVIDER_PRESETS: Dict[str, Dict] = {
    "自定义 (Custom)": {
        "base_url": "",
        "need_key": False,
        "models": [],
        "note": "自行填写任意 OpenAI 兼容端点的 base_url",
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "need_key": True,
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1", "o1-mini"],
        "note": "OpenAI 官方接口",
    },
    "Ollama (本地)": {
        "base_url": "http://127.0.0.1:11434/v1",
        "need_key": False,
        "models": ["llava", "llama3.2-vision", "qwen2.5-vl", "llama3.1", "mistral"],
        "note": "本地部署，默认无需 key；模型需先 pull",
    },
    "OpenRouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "need_key": True,
        "models": ["openai/gpt-4o", "anthropic/claude-3.5-sonnet", "google/gemini-pro-1.5",
                   "meta-llama/llama-3.1-70b-instruct"],
        "note": "聚合多家模型，模型名带厂商前缀",
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com/v1",
        "need_key": True,
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "note": "DeepSeek 官方接口",
    },
    "Together.ai": {
        "base_url": "https://api.together.xyz/v1",
        "need_key": True,
        "models": ["meta-llama/Llama-3.3-70B-Instruct-Turbo", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
        "note": "Together.ai 开源模型托管",
    },
    "Venus (火山方舟)": {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "need_key": True,
        "models": ["doubao-seed-1.6-250615", "doubao-vision-pro-32k"],
        "note": "字节火山方舟（OpenAI 兼容，版本前缀为 v3）",
    },
    "硅基流动 (SiliconFlow)": {
        "base_url": "https://api.siliconflow.cn/v1",
        "need_key": True,
        "models": ["Qwen/Qwen2.5-72B-Instruct", "deepseek-ai/DeepSeek-V3", "Pro/Qwen/Qwen2.5-VL-72B-Instruct"],
        "note": "硅基流动，国产兼容端点",
    },
    "智谱 GLM (Zhipu)": {
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "need_key": True,
        "models": ["glm-4-plus", "glm-4-flash", "glm-4v-plus", "glm-4v", "glm-4-air"],
        "note": "智谱 AI，OpenAI 兼容（base_url 到 /v4）",
    },
    "Moonshot (Kimi)": {
        "base_url": "https://api.moonshot.cn/v1",
        "need_key": True,
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k", "kimi-k2-0711-preview"],
        "note": "月之暗面 Kimi，OpenAI 兼容",
    },
    "百川 (Baichuan)": {
        "base_url": "https://api.baichuan-ai.com/v1",
        "need_key": True,
        "models": ["Baichuan4", "Baichuan4-Turbo", "Baichuan3-Turbo"],
        "note": "百川智能，OpenAI 兼容",
    },
    "MiniMax": {
        "base_url": "https://api.minimax.chat/v1",
        "need_key": True,
        "models": ["abab6.5-chat", "abab6.5s-chat", "MiniMax-Text-01"],
        "note": "MiniMax，OpenAI 兼容（需在 URL 带 GroupId 的端点另配）",
    },
    "阶跃 (StepFun)": {
        "base_url": "https://api.stepfun.com/v1",
        "need_key": True,
        "models": ["step-1v-8k", "step-1-32k", "step-1-flash"],
        "note": "阶跃星辰，OpenAI 兼容",
    },
    "讯飞星火 (Spark)": {
        "base_url": "https://spark-api-open.xf-yun.com/v1",
        "need_key": True,
        "models": ["generalv3.5", "generalv4.0", "spark-u1"],
        "note": "讯飞星火，OpenAI 兼容（需开通开放平台）",
    },
    "商汤 SenseChat": {
        "base_url": "https://api.sensenova.cn/v1",
        "need_key": True,
        "models": ["SenseChat-5", "SenseChat-5-Cantonese", "SenseChat-Turbo"],
        "note": "商汤日日新 SenseChat，OpenAI 兼容",
    },
}

# ComfyUI 下拉框展示顺序（自定义永远排第一）
PROVIDER_ORDER: List[str] = ["自定义 (Custom)"] + [k for k in PROVIDER_PRESETS if k != "自定义 (Custom)"]


# ---------------------------------------------------------------------------
# 全局模型缓存：被节点下拉框读取
# ---------------------------------------------------------------------------
class _ModelCache:
    """进程级模型缓存。

    节点 INPUT_TYPES 的 model 下拉框调用 get_cached_models() 读取。
    当用户在「模型获取」节点拉取成功后，调用 set_models() 更新。
    """

    def __init__(self):
        # 默认放入所有厂商的占位模型，保证未拉取时下拉框也不会空
        self._models: List[str] = []
        self._source: str = "预设"
        self._error: Optional[str] = None
        self.refresh_defaults()

    def refresh_defaults(self):
        """用所有厂商预设模型初始化/补充缓存（不覆盖已拉取的列表）。"""
        if self._source != "拉取":
            merged = []
            for name in PROVIDER_ORDER:
                for m in PROVIDER_PRESETS[name].get("models", []):
                    if m not in merged:
                        merged.append(m)
            self._models = merged
            self._source = "预设"

    def set_models(self, models: List[str], source: str = "拉取"):
        if not models:
            return
        # 去重，保持顺序
        seen, dedup = set(), []
        for m in models:
            if m and m not in seen:
                seen.add(m)
                dedup.append(m)
        self._models = dedup
        self._source = source
        self._error = None

    def set_error(self, err: str):
        self._error = err

    def get_models(self) -> List[str]:
        if not self._models:
            self.refresh_defaults()
        return self._models

    def get_source(self) -> str:
        return self._source

    def get_error(self) -> Optional[str]:
        return self._error


# 全局单例 —— 整个 ComfyUI 进程共享
UNIVERSAL_MODEL_CACHE = _ModelCache()


def get_provider_base_url(provider: str) -> str:
    """返回指定厂商的默认 base_url（自定义返回空）。"""
    return PROVIDER_PRESETS.get(provider, {}).get("base_url", "")


def provider_needs_key(provider: str) -> bool:
    return PROVIDER_PRESETS.get(provider, {}).get("need_key", False)


def get_cached_models() -> List[str]:
    """供节点下拉框调用。"""
    return UNIVERSAL_MODEL_CACHE.get_models()


def resolve_base_url(provider: str, custom_url: str = "") -> str:
    """根据厂商选择解析最终 base_url：选了预设用预设，自定义用用户填写值。"""
    if provider == "自定义 (Custom)":
        return custom_url.strip().rstrip("/")
    return PROVIDER_PRESETS.get(provider, {}).get("base_url", "").rstrip("/")
