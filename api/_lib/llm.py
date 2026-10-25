#!/usr/bin/env python3
"""LLM client implementations for QUEST.

Provides:
- GeminiClient: Real Google Gemini REST API client via httpx with:
    - Free-tier model configuration via GEMINI_MODEL (defaults to gemini-1.5-flash / gemini-2.0-flash)
    - Key strictly from GEMINI_API_KEY (never logged)
    - JSON mode enforcement (responseMimeType: application/json)
    - 20s default timeout
    - Exponential backoff with jitter on HTTP 429 / 5xx
    - Markdown-fence stripping (```json ... ```)
    - Single automatic repair retry on invalid JSON
    - Latency capture (in milliseconds)
- MockClient: Deterministic or programmable mock client for unit testing and offline fallbacks.
"""
from __future__ import annotations

import json
import logging
import os
import random
import re
import time
from typing import Any, Dict, List, Optional, Union

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("quest.llm")


def strip_markdown_fence(text: str) -> str:
    """Strip markdown code fence wrappers such as ```json ... ``` or ``` ... ```."""
    text = text.strip()
    if text.startswith("```"):
        # Match opening ``` or ```json or ```JSON
        pattern = r"^```(?:json|JSON)?\s*\n?(.*?)\n?```$"
        match = re.search(pattern, text, flags=re.DOTALL)
        if match:
            return match.group(1).strip()
    return text


class LLMError(Exception):
    """Base class for LLM client exceptions."""
    pass


class LLMTimeoutError(LLMError):
    """Raised when an LLM call exceeds the allowed timeout."""
    pass


class LLMRateLimitError(LLMError):
    """Raised when the LLM service returns a 429 rate limit that persists after retries."""
    pass


class LLMInvalidJSONError(LLMError):
    """Raised when LLM output cannot be parsed as valid JSON even after repair."""
    pass


class BaseLLMClient:
    """Base interface for QUEST LLM clients."""

    def __init__(self) -> None:
        self.last_latency_ms: float = 0.0

    def generate(self, prompt: str, timeout: Optional[float] = None) -> str:
        raise NotImplementedError

    def generate_json(self, prompt: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        raise NotImplementedError


class GeminiClient(BaseLLMClient):
    """Real Gemini client using Google's Generative Language REST API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: float = 20.0,
        max_retries: int = 3,
    ) -> None:
        super().__init__()
        # Key read strictly from parameter or GEMINI_API_KEY env var
        raw_key = api_key or os.getenv("GEMINI_API_KEY") or ""
        self._api_key = raw_key.strip()
        # Free-tier model names: gemini-flash-lite-latest, gemini-3.5-flash-lite, gemini-3.8-flash
        self.model_name = (model_name or os.getenv("GEMINI_MODEL") or "gemini-flash-lite-latest").strip()
        self.default_timeout = timeout
        self.max_retries = max_retries
        self._endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def _call_gemini_api(self, prompt: str, timeout: float) -> str:
        """Call Gemini REST endpoint with exponential backoff and jitter on 429/5xx."""
        if not self._api_key:
            raise LLMError("GEMINI_API_KEY is not configured")

        url = f"{self._endpoint}?key={self._api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2,
            },
        }

        client_timeout = httpx.Timeout(timeout, connect=5.0)
        retries = 0
        backoff_base = 1.0

        while True:
            try:
                with httpx.Client(timeout=client_timeout) as client:
                    response = client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    candidates = data.get("candidates", [])
                    if not candidates:
                        raise LLMError("Gemini returned no candidates")
                    content_parts = candidates[0].get("content", {}).get("parts", [])
                    if not content_parts or "text" not in content_parts[0]:
                        raise LLMError("Gemini candidate contains no text parts")
                    return content_parts[0]["text"]

                # Handle transient 429 or 5xx server errors
                if response.status_code in (429, 500, 502, 503, 504):
                    retries += 1
                    if retries > self.max_retries:
                        if response.status_code == 429:
                            raise LLMRateLimitError(f"Gemini 429 rate limit exceeded after {retries} retries")
                        raise LLMError(f"Gemini server error {response.status_code} after {retries} retries")

                    delay = (backoff_base * (2 ** (retries - 1))) + random.uniform(0.1, 0.5)
                    time.sleep(delay)
                    continue

                # Non-retryable error (e.g. 400, 403, 404)
                # Note: NEVER log API key or URL containing the key!
                raise LLMError(f"Gemini API returned error status {response.status_code}: {response.text[:200]}")

            except httpx.TimeoutException as exc:
                raise LLMTimeoutError(f"Gemini call timed out after {timeout}s") from exc
            except (httpx.ConnectError, httpx.NetworkError) as exc:
                retries += 1
                if retries > self.max_retries:
                    raise LLMError(f"Gemini network error after {retries} retries: {exc}") from exc
                delay = (backoff_base * (2 ** (retries - 1))) + random.uniform(0.1, 0.5)
                time.sleep(delay)

    def generate(self, prompt: str, timeout: Optional[float] = None) -> str:
        """Generate text from Gemini, measuring latency and stripping markdown fences."""
        t_req = timeout if timeout is not None else self.default_timeout
        start_time = time.perf_counter()
        try:
            raw_text = self._call_gemini_api(prompt, timeout=t_req)
            return strip_markdown_fence(raw_text)
        finally:
            self.last_latency_ms = (time.perf_counter() - start_time) * 1000.0

    def generate_json(self, prompt: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Generate valid JSON from Gemini, performing one repair retry on invalid JSON."""
        t_req = timeout if timeout is not None else self.default_timeout
        start_time = time.perf_counter()
        try:
            raw_text = self._call_gemini_api(prompt, timeout=t_req)
            clean_text = strip_markdown_fence(raw_text)

            try:
                return json.loads(clean_text)
            except json.JSONDecodeError as decode_err:
                logger.warning(f"Gemini output not valid JSON ({decode_err}), attempting 1 repair retry...")
                # Attempt single repair retry
                repair_prompt = (
                    "The following output was supposed to be strictly valid JSON, but had a syntax error:\n\n"
                    f"{clean_text}\n\n"
                    "Please repair and return ONLY strictly valid RFC 8259 JSON. No markdown fences, no comments, no prose."
                )
                repair_text = self._call_gemini_api(repair_prompt, timeout=t_req)
                repaired_clean = strip_markdown_fence(repair_text)
                try:
                    return json.loads(repaired_clean)
                except json.JSONDecodeError as second_err:
                    raise LLMInvalidJSONError(f"Failed to parse repaired JSON: {second_err}") from second_err
        finally:
            self.last_latency_ms = (time.perf_counter() - start_time) * 1000.0


class MockClient(BaseLLMClient):
    """Programmable MockClient for testing API endpoints and offline scenarios."""

    def __init__(
        self,
        default_response: Optional[Union[Dict[str, Any], str]] = None,
        should_timeout: bool = False,
        invalid_json: bool = False,
        error_to_raise: Optional[Exception] = None,
        latency_ms: float = 12.0,
    ) -> None:
        super().__init__()
        self.default_response = default_response
        self.should_timeout = should_timeout
        self.invalid_json = invalid_json
        self.error_to_raise = error_to_raise
        self.fixed_latency_ms = latency_ms
        self.call_count: int = 0
        self.last_prompt: Optional[str] = None

    def generate(self, prompt: str, timeout: Optional[float] = None) -> str:
        self.call_count += 1
        self.last_prompt = prompt
        self.last_latency_ms = self.fixed_latency_ms

        if self.should_timeout:
            raise LLMTimeoutError("MockClient forced timeout")
        if self.error_to_raise:
            raise self.error_to_raise
        if self.invalid_json:
            return "```json\n{ broken json: [unclosed\n```"

        if isinstance(self.default_response, dict):
            return json.dumps(self.default_response)
        if isinstance(self.default_response, str):
            return self.default_response

        # Fallback default response
        return json.dumps({"title": "Mock Title", "big_idea": "Mock Idea"})

    def generate_json(self, prompt: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        raw = self.generate(prompt, timeout=timeout)
        cleaned = strip_markdown_fence(raw)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as err:
            raise LLMInvalidJSONError(f"MockClient returned invalid JSON: {err}") from err
