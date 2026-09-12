"""
providers.py
LLM Provider Abstraction for Critic Minds.
Supports Google Gemini (primary default) and Groq (DocuMind-AI reuse / fallback).
Supports user-supplied API keys (masked in UI) and platform-configured default keys.
Enforces native JSON mode and resilient multi-stage JSON parsing.
"""
import json
import re
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.config import AppConfig


class LLMProviderError(Exception):
    pass


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate_text(self, prompt: str, temperature: float = 0.3, response_format_json: bool = False) -> str:
        pass

    def generate_json(self, prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        """Generates structured JSON output from a prompt with native JSON mode."""
        raw_text = self.generate_text(prompt, temperature=temperature, response_format_json=True)
        return _parse_json_from_llm(raw_text)


def _parse_json_from_llm(text: str) -> Dict[str, Any]:
    """Robustly extracts and parses JSON from an LLM response string."""
    cleaned = text.strip()

    # Fast path: use json_repair library if available
    try:
        import json_repair
        parsed = json_repair.loads(cleaned)
        if isinstance(parsed, dict) and len(parsed) > 0:
            return parsed
    except Exception:
        pass

    # 1. Remove markdown code fences if present
    if "```" in cleaned:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*(?:```|$)", cleaned)
        if match and match.group(1).strip():
            cleaned = match.group(1).strip()
        else:
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    # 2. Extract substring from first { to last }
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start : end + 1]

    # Attempt direct json.loads
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Clean trailing commas before } or ]
    sanitized = re.sub(r",\s*([\]}])", r"\1", cleaned)
    try:
        return json.loads(sanitized)
    except Exception:
        pass

    # Second pass with json_repair on substring
    try:
        import json_repair
        parsed = json_repair.repair_json(cleaned, return_objects=True)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    raise LLMProviderError(f"Failed to parse valid JSON from model response. Preview: {cleaned[:300]}")


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Provider using modern google-genai SDK with automatic model fallback."""

    def __init__(self, api_key: str, model_name: str = "gemini-3.6-flash"):
        self.api_key = api_key.strip()
        self.model_name = model_name

    def generate_text(self, prompt: str, temperature: float = 0.3, response_format_json: bool = False) -> str:
        if not self.api_key:
            raise LLMProviderError("Missing Gemini API Key. Please enter your key or configure default.")

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            config_params = {
                "temperature": temperature,
                "max_output_tokens": 8192,
            }
            if response_format_json:
                config_params["response_mime_type"] = "application/json"

            config = types.GenerateContentConfig(**config_params)

            models_to_try = [self.model_name]
            for alt in ("gemini-3.5-flash-lite", "gemini-flash-latest"):
                if alt not in models_to_try:
                    models_to_try.append(alt)

            last_err = None
            for candidate_model in models_to_try:
                try:
                    response = client.models.generate_content(
                        model=candidate_model,
                        contents=prompt,
                        config=config,
                    )
                    if response and response.text:
                        return response.text
                except Exception as exc:
                    msg = str(exc)
                    if "API_KEY_INVALID" in msg or "401" in msg or "403" in msg:
                        raise LLMProviderError("Invalid Gemini API Key. Please verify your key in AI Settings.")
                    last_err = exc
                    continue

            raise LLMProviderError(f"Gemini API request failed across models: {last_err}")
        except LLMProviderError:
            raise
        except Exception as exc:
            raise LLMProviderError(f"Gemini Client initialization failed: {exc}")


class GroqProvider(BaseLLMProvider):
    """Groq Provider reusing DocuMind-AI's battle-tested REST completion pattern."""

    def __init__(self, api_key: str, model_name: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key.strip()
        self.model_name = model_name

    def generate_text(self, prompt: str, temperature: float = 0.2, response_format_json: bool = False) -> str:
        if not self.api_key:
            raise LLMProviderError("Missing Groq API Key. Please enter your key or configure default.")

        import requests

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": 6000,
        }
        if response_format_json:
            payload["response_format"] = {"type": "json_object"}

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
        except requests.RequestException as exc:
            raise LLMProviderError(f"Could not reach Groq API: {exc}") from exc

        if resp.status_code == 401:
            raise LLMProviderError("Invalid Groq API key. Please check the key in AI Settings.")
        if resp.status_code == 429:
            raise LLMProviderError("Groq rate limit reached. Please wait a moment before trying again.")
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("error", {}).get("message", resp.text)
            except Exception:
                detail = resp.text
            raise LLMProviderError(f"Groq API Error ({resp.status_code}): {detail}")

        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise LLMProviderError(f"Unexpected Groq response structure: {data}") from exc


def get_llm_provider(
    provider_name: str,
    user_api_key: Optional[str] = None,
    use_default: bool = False,
) -> BaseLLMProvider:
    """
    Factory to retrieve an initialized LLM Provider according to Section 20 & 41 requirements.
    Resolves user-supplied key or application default key.
    """
    provider_clean = (provider_name or "gemini").lower().strip()

    # Determine key
    api_key = None
    if not use_default and user_api_key and user_api_key.strip():
        api_key = user_api_key.strip()
    else:
        api_key = AppConfig.get_default_key(provider_clean)

    if not api_key:
        raise LLMProviderError(
            f"No API key available for {provider_clean.capitalize()}. "
            "Please select 'Use my own API key' in AI Settings or configure the default environment key."
        )

    if provider_clean == "gemini":
        return GeminiProvider(api_key=api_key)
    elif provider_clean == "groq":
        return GroqProvider(api_key=api_key)
    else:
        raise LLMProviderError(f"Unsupported provider '{provider_clean}'. Supported: Gemini, Groq.")
