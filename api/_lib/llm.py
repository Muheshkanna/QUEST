#!/usr/bin/env python3
"""LLM client abstractions for the QUEST project.

The production code expects three client classes:
- :class:`GeminiClient` – wraps the real Gemini API (placeholder implementation).
- :class:`GroqClient`   – wraps the Groq API (placeholder implementation).
- :class:`MockClient`   – returns deterministic responses for offline runs.

Only the methods used by the application are defined.  The mock client reads
pre‑generated JSON files from ``data/bank`` so that the front‑end can function
without network access.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Base class (common interface)
# ---------------------------------------------------------------------------

class BaseLLMClient:
    """Abstract base with a minimal interface.

    Sub‑classes implement :meth:`generate` which receives a *prompt* string and
    returns a list of strings (the model's responses).  The real clients would
    perform HTTP calls; the mock client reads from static files.
    """

    def generate(self, prompt: str) -> List[str]:  # pragma: no cover – overridden
        raise NotImplementedError

# ---------------------------------------------------------------------------
# Gemini client (stub – raises if run without API key)
# ---------------------------------------------------------------------------

class GeminiClient(BaseLLMClient):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise RuntimeError("Gemini API key not configured")

    def generate(self, prompt: str) -> List[str]:
        # In a real implementation we would call the Gemini endpoint.
        # For the offline demo we simply raise to alert the developer.
        raise RuntimeError(
            "GeminiClient.generate called in offline mode – no API key configured"
        )

# ---------------------------------------------------------------------------
# Groq client (stub – similar to Gemini)
# ---------------------------------------------------------------------------

class GroqClient(BaseLLMClient):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise RuntimeError("Groq API key not configured")

    def generate(self, prompt: str) -> List[str]:
        raise RuntimeError(
            "GroqClient.generate called in offline mode – no API key configured"
        )

# ---------------------------------------------------------------------------
# Mock client – deterministic offline responses
# ---------------------------------------------------------------------------

class MockClient(BaseLLMClient):
    """Return a deterministic answer based on the prompt.

    The mock looks for a JSON file whose name matches the *template_id* embedded
    in the prompt (e.g. ``"template-id": "g5-fractions-add-easy-1"``).  If the
    file exists it returns the ``explanation`` field; otherwise it returns a
    generic placeholder.
    """

    def __init__(self, bank_root: str | os.PathLike = None):
        # By default use the project's generated bank directory.
        self.bank_root = Path(bank_root) if bank_root else Path(__file__).resolve().parents[2] / "data" / "bank"

    def _extract_template_id(self, prompt: str) -> str | None:
        # Very simple extraction – the real system embeds the id as JSON.
        import re

        m = re.search(r'"template_id"\s*:\s*"(?P<tid>[^"]+)"', prompt)
        return m.group("tid") if m else None

    def generate(self, prompt: str) -> List[str]:
        tid = self._extract_template_id(prompt)
        if not tid:
            return ["Mock response – no template_id found"]
        # Search each topic file for a matching question.
        for topic_file in self.bank_root.glob("*.json"):
            try:
                data = json.loads(topic_file.read_text(encoding="utf-8"))
                for q in data.get("questions", []):
                    if q.get("template_id") == tid:
                        # Return the explanation as the mock "model" output.
                        return [q.get("explanation", "No explanation available")]
            except Exception:
                continue
        return [f"Mock response – template_id '{tid}' not found in bank"]

# ---------------------------------------------------------------------------
# Helper factory – chooses client based on environment variable ``LLM_BACKEND``
# ---------------------------------------------------------------------------

def get_client() -> BaseLLMClient:
    """Return the appropriate LLM client.

    ``LLM_BACKEND`` can be ``gemini``, ``groq`` or ``mock`` (default).
    """
    backend = os.getenv("LLM_BACKEND", "mock").lower()
    if backend == "gemini":
        return GeminiClient()
    if backend == "groq":
        return GroqClient()
    return MockClient()

# End of file
