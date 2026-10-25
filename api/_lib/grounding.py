#!/usr/bin/env python3
"""Curriculum Grounding and Prompt Engineering for QUEST.

Registry retrieval by standard code, not vector search.

This module provides deterministic grounding retrieval for LLM prompt generation.
Rather than using opaque vector databases, it uses exact deterministic lookups into
`data/topics.json` and `data/misconceptions.json` indexed by standard code and topic ID.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "v1"

# Module-level cached registries
_TOPICS_BY_ID: Dict[str, Dict[str, Any]] = {}
_TOPICS_BY_STANDARD: Dict[str, Dict[str, Any]] = {}
_MISCONCEPTIONS_BY_TOPIC: Dict[str, List[Dict[str, Any]]] = {}
_MISCONCEPTIONS_BY_ID: Dict[str, Dict[str, Any]] = {}


def _ensure_loaded() -> None:
    """Load and index topics and misconceptions registries if not already in memory."""
    global _TOPICS_BY_ID, _TOPICS_BY_STANDARD, _MISCONCEPTIONS_BY_TOPIC, _MISCONCEPTIONS_BY_ID
    if _TOPICS_BY_ID and _MISCONCEPTIONS_BY_TOPIC:
        return

    # Load topics
    topics_file = DATA_DIR / "topics.json"
    if topics_file.is_file():
        with open(topics_file, "r", encoding="utf-8") as f:
            topics_data = json.load(f)
            for t in topics_data:
                _TOPICS_BY_ID[t["id"]] = t
                _TOPICS_BY_STANDARD[t["standard"]] = t

    # Load misconceptions registry
    misc_file = DATA_DIR / "misconceptions.json"
    if misc_file.is_file():
        with open(misc_file, "r", encoding="utf-8") as f:
            misc_data = json.load(f)
            misc_list = misc_data.get("misconceptions", [])
            for m in misc_list:
                m_id = m.get("id")
                if m_id:
                    _MISCONCEPTIONS_BY_ID[m_id] = m
                for tid in m.get("topic_ids", []):
                    _MISCONCEPTIONS_BY_TOPIC.setdefault(tid, []).append(m)


def get_topic_by_id(topic_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve topic curriculum entry by topic ID."""
    _ensure_loaded()
    return _TOPICS_BY_ID.get(topic_id)


def get_topic_by_standard(standard_code: str) -> Optional[Dict[str, Any]]:
    """Retrieve topic curriculum entry by standard code (registry retrieval by standard code, not vector search)."""
    _ensure_loaded()
    return _TOPICS_BY_STANDARD.get(standard_code)


def get_misconceptions_for_topic(topic_id: str) -> List[Dict[str, Any]]:
    """Retrieve all registered misconceptions for a given topic ID."""
    _ensure_loaded()
    return _MISCONCEPTIONS_BY_TOPIC.get(topic_id, [])


def get_misconception_by_id(misconception_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve detailed diagnostic information for a specific misconception ID."""
    _ensure_loaded()
    return _MISCONCEPTIONS_BY_ID.get(misconception_id)


def format_misconceptions_text(misconceptions: List[Dict[str, Any]]) -> str:
    """Format list of misconceptions into structured markdown text for prompt injection."""
    if not misconceptions:
        return "- No pre-registered misconceptions; formulate plausible conceptual errors."

    lines = []
    for m in misconceptions:
        lines.append(
            f"- **`{m['id']}`**: {m.get('kid_label', m['id'])}\n"
            f"  Diagnosis: {m.get('diagnosis', '')}\n"
            f"  Why it fails: {m.get('why_it_fails', '')}\n"
            f"  Example: {m.get('mini_example', '')}"
        )
    return "\n".join(lines)


def build_lesson_prompt(topic_id: str) -> str:
    """Inject standard code, standard text, and registry misconceptions into lesson prompt."""
    _ensure_loaded()
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise ValueError(f"Unknown topic ID: {topic_id}")

    template_file = PROMPTS_DIR / "lesson.md"
    if not template_file.is_file():
        raise FileNotFoundError(f"Lesson prompt template not found at {template_file}")

    template = template_file.read_text(encoding="utf-8")
    misconceptions = get_misconceptions_for_topic(topic_id)
    misconceptions_text = format_misconceptions_text(misconceptions)

    return template.format(
        topic_id=topic["id"],
        topic_title=topic["title"],
        standard=topic["standard"],
        standard_text=topic["standard_text"],
        verifier_type=topic.get("verifier_type", "expression_evaluation"),
        misconceptions_text=misconceptions_text,
    )


def build_question_prompt(topic_id: str, difficulty: str = "medium") -> str:
    """Inject standard code, standard text, and registry misconceptions into question prompt."""
    _ensure_loaded()
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise ValueError(f"Unknown topic ID: {topic_id}")

    template_file = PROMPTS_DIR / "questions.md"
    if not template_file.is_file():
        raise FileNotFoundError(f"Questions prompt template not found at {template_file}")

    template = template_file.read_text(encoding="utf-8")
    misconceptions = get_misconceptions_for_topic(topic_id)
    misconceptions_text = format_misconceptions_text(misconceptions)

    return template.format(
        topic_id=topic["id"],
        topic_title=topic["title"],
        standard=topic["standard"],
        standard_text=topic["standard_text"],
        difficulty=difficulty,
        verifier_type=topic.get("verifier_type", "expression_evaluation"),
        misconceptions_text=misconceptions_text,
    )
