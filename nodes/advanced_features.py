# -*- coding: utf-8 -*-
"""高级功能节点"""

import json
from typing import Tuple

try:
    from ..utils.api_client import GeminiAPIClient, GeminiAPIError
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.api_client import GeminiAPIClient, GeminiAPIError


class LK_Gemini_StructuredOutput:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "输入提示词..."}),
            "json_schema": ("STRING", {"multiline": True, 
                "default": '{\n  "type": "object",\n  "properties": {\n    "name": {"type": "string"}\n  }\n}'}),
            "model": (["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview"], {"default": "gemini-2.5-flash"}),
            "api_key": ("STRING", {"default": ""})
        }, "optional": {"system_instruction": ("STRING", {"multiline": True, "default": ""})}}
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("JSON 输出", "原始响应")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/Gemini/高级"

    def generate(self, prompt, json_schema, model, api_key, system_instruction=""):
        if not api_key: return ("", "错误: 请提供有效的 API 密钥")
        try: schema = json.loads(json_schema)
        except json.JSONDecodeError as e: return ("", f"JSON Schema 解析错误: {str(e)}")
        try:
            client = GeminiAPIClient(api_key)
            gen_config = {"responseMimeType": "application/json", "responseSchema": schema}
            response = client.generate_content(model=model, contents=prompt,
                system_instruction=system_instruction or None, generation_config=gen_config)
            raw = client.parse_text_response(response)
            try: return (json.dumps(json.loads(raw), ensure_ascii=False, indent=2), raw)
            except: return (raw, raw)
        except GeminiAPIError as e: return ("", f"API 错误: {str(e)}")
        except Exception as e: return ("", f"错误: {str(e)}")


class LK_Gemini_PromptOptimizer:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "raw_prompt": ("STRING", {"multiline": True, "placeholder": "输入原始提示词..."}),
            "target_style": (["SD/FLUX", "Midjourney", "DALL-E", "Gemini Imagen", "通用增强"], {"default": "SD/FLUX"}),
            "model": (["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview"], {"default": "gemini-2.5-flash"}),
            "api_key": ("STRING", {"default": ""})
        }, "optional": {
            "enhancement_level": (["轻微", "中等", "强力"], {"default": "中等"}),
            "include_negative": ("BOOLEAN", {"default": True}),
            "language": (["English", "中文", "保持原文"], {"default": "English"})
        }}
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("优化后正向提示词", "负向提示词", "优化说明")
    FUNCTION = "optimize"
    CATEGORY = "LK_Studio/Gemini/高级"

    def optimize(self, raw_prompt, target_style, model, api_key, enhancement_level="中等",
                 include_negative=True, language="English"):
        if not api_key: return ("", "", "错误: 请提供有效的 API 密钥")
        try:
            client = GeminiAPIClient(api_key)
            system = f"""你是 AI 绘画提示词优化专家。目标风格: {target_style}。优化强度: {enhancement_level}。输出语言: {language}。
输出JSON格式: {{"positive_prompt": "...", "negative_prompt": "...", "explanation": "..."}}"""
            response = client.generate_content(model=model, contents=f"优化此提示词:\n{raw_prompt}",
                system_instruction=system)
            result = client.parse_text_response(response)
            try:
                start, end = result.find("{"), result.rfind("}") + 1
                if start != -1 and end > start:
                    parsed = json.loads(result[start:end])
                    return (parsed.get("positive_prompt", ""), parsed.get("negative_prompt", ""),
                            parsed.get("explanation", ""))
            except: pass
            return (result, "", "无法解析结构化输出")
        except GeminiAPIError as e: return ("", "", f"API 错误: {str(e)}")
        except Exception as e: return ("", "", f"错误: {str(e)}")


class LK_Gemini_Thinking:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "输入需要深度思考的问题..."}),
            "model": (["gemini-2.5-pro", "gemini-2.5-flash", "gemini-3-pro-preview", "gemini-3-flash-preview"],
                      {"default": "gemini-2.5-pro"}),
            "api_key": ("STRING", {"default": ""})
        }, "optional": {
            "thinking_level": (["低", "中", "高", "最高"], {"default": "中"}),
            "thinking_budget": ("INT", {"default": 4096, "min": 0, "max": 24576, "step": 512}),
            "show_thinking_process": ("BOOLEAN", {"default": True})
        }}
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("回答", "思考过程")
    FUNCTION = "think"
    CATEGORY = "LK_Studio/Gemini/高级"

    def think(self, prompt, model, api_key, thinking_level="中", thinking_budget=4096, show_thinking_process=True):
        if not api_key: return ("错误: 请提供有效的 API 密钥", "")
        try:
            client = GeminiAPIClient(api_key, timeout=180)
            level_map = {"低": "low", "中": "medium", "高": "high", "最高": "max"}
            gen_config = {"thinkingConfig": {"thinkingBudget": thinking_budget}}
            if "3" in model: gen_config["thinkingConfig"]["thinkingLevel"] = level_map.get(thinking_level, "medium")
            response = client.generate_content(model=model, contents=prompt, generation_config=gen_config)
            answer, thinking = "", ""
            try:
                for part in response.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                    if part.get("thought"): thinking += part.get("text", "") + "\n"
                    elif "text" in part: answer += part.get("text", "")
            except: answer = client.parse_text_response(response)
            return (answer, thinking if show_thinking_process else "[思考过程已隐藏]")
        except GeminiAPIError as e: return (f"API 错误: {str(e)}", "")
        except Exception as e: return (f"错误: {str(e)}", "")
