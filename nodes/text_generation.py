# -*- coding: utf-8 -*-
"""文本生成节点"""

import torch
from typing import Tuple

try:
    from ..utils.api_client import GeminiAPIClient, GeminiAPIError
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.api_client import GeminiAPIClient, GeminiAPIError


class LK_Gemini_Text:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "prompt": ("STRING", {"multiline": True, "placeholder": "请输入您的提示词..."}),
            "model": (["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-lite", "gemini-3-flash-preview", 
                       "gemini-3-pro-preview", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"], 
                      {"default": "gemini-2.5-flash"}),
            "api_key": ("STRING", {"default": "", "placeholder": "输入 Gemini API 密钥"})
        }, "optional": {
            "system_instruction": ("STRING", {"multiline": True, "default": ""}),
            "temperature": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            "max_output_tokens": ("INT", {"default": 8192, "min": 1, "max": 65536}),
            "enable_thinking": ("BOOLEAN", {"default": False}),
            "thinking_budget": ("INT", {"default": 1024, "min": 0, "max": 24576})
        }}
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("文本输出", "思考摘要")
    FUNCTION = "generate"
    CATEGORY = "LK_Studio/Gemini/文本"

    def generate(self, prompt, model, api_key, system_instruction="", temperature=1.0,
                 max_output_tokens=8192, enable_thinking=False, thinking_budget=1024):
        if not api_key: return ("错误: 请提供有效的 API 密钥", "")
        try:
            client = GeminiAPIClient(api_key)
            gen_config = {"temperature": temperature, "maxOutputTokens": max_output_tokens}
            if enable_thinking and ("2.5" in model or "3" in model):
                gen_config["thinkingConfig"] = {"thinkingBudget": thinking_budget}
            response = client.generate_content(model=model, contents=prompt,
                system_instruction=system_instruction or None, generation_config=gen_config)
            text_output = client.parse_text_response(response)
            thinking = ""
            try:
                for part in response.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                    if part.get("thought"): thinking = part.get("text", ""); break
            except: pass
            return (text_output, thinking)
        except GeminiAPIError as e: return (f"API 错误: {str(e)}", "")
        except Exception as e: return (f"错误: {str(e)}", "")


class LK_Gemini_Chat:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "user_message": ("STRING", {"multiline": True, "placeholder": "输入您的消息..."}),
            "model": (["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-flash-preview", "gemini-3-pro-preview"],
                      {"default": "gemini-2.5-flash"}),
            "api_key": ("STRING", {"default": ""})
        }, "optional": {
            "chat_history": ("STRING", {"multiline": True, "default": ""}),
            "system_instruction": ("STRING", {"multiline": True, "default": ""}),
            "max_history_turns": ("INT", {"default": 10, "min": 1, "max": 50})
        }}
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("助手回复", "更新的历史")
    FUNCTION = "chat"
    CATEGORY = "LK_Studio/Gemini/文本"

    def chat(self, user_message, model, api_key, chat_history="", system_instruction="", max_history_turns=10):
        if not api_key: return ("错误: 请提供有效的 API 密钥", chat_history)
        try:
            import json
            history = json.loads(chat_history) if chat_history else []
            if len(history) > max_history_turns * 2: history = history[-(max_history_turns * 2):]
            history.append({"role": "user", "parts": [{"text": user_message}]})
            client = GeminiAPIClient(api_key)
            response = client.generate_content(model=model, contents=history,
                system_instruction=system_instruction or None)
            reply = client.parse_text_response(response)
            history.append({"role": "model", "parts": [{"text": reply}]})
            return (reply, json.dumps(history, ensure_ascii=False, indent=2))
        except GeminiAPIError as e: return (f"API 错误: {str(e)}", chat_history)
        except Exception as e: return (f"错误: {str(e)}", chat_history)
