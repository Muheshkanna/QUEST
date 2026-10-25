#!/usr/bin/env python3
"""Math Quest Serverless FastAPI Backend.

Provides curriculum, question banks, adaptive answer diagnosis, AI lesson refreshing,
multimodal infographic/explainer retrieval, and benchmark evaluations.
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from api._lib.adaptive import compute_xp, update_difficulty
from api._lib.bkt import update as update_bkt
from api._lib.grounding import (
    build_lesson_prompt,
    get_misconception_by_id,
    get_topic_by_id,
)
from api._lib.llm import (
    BaseLLMClient,
    GeminiClient,
    LLMError,
    LLMInvalidJSONError,
    LLMTimeoutError,
)
from api._lib.schemas import (
    AnswerRequest,
    AnswerResponse,
    DiagnosisModel,
    Difficulty,
    ErrorDetail,
    ErrorEnvelope,
    Lesson,
    TopicResponse,
)
from api._lib.verifier import (
    VerificationError,
    evaluate_expression,
    normalize_option,
    safe_fraction,
    verify_lesson,
    verify_question,
)

logger = logging.getLogger("quest.api")

app = FastAPI(
    title="Math Quest API",
    version="1.0.0",
    description="Deterministic math verification and misconception diagnosis API for Math Quest",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global Exception Handlers (Standardizing on {error: {code, message}})
# ---------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMITED",
        500: "INTERNAL_SERVER_ERROR",
    }
    code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": code, "message": str(exc.detail)}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters or payload",
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
            }
        },
    )


# ---------------------------------------------------------------------------
# Helpers & State (LLM Injection, Path Resolution, Rate Limiting & TTL Cache)
# ---------------------------------------------------------------------------

_LLM_CLIENT_OVERRIDE: Optional[BaseLLMClient] = None
_LESSON_CACHE: Dict[str, Tuple[Dict[str, Any], float]] = {}  # topic_id -> (data, expires_at)
_IP_REFRESH_LOG: Dict[str, List[float]] = {}  # ip -> list of timestamps


def get_data_dir() -> Path:
    """Find data/ directory across local development and Vercel serverless paths."""
    candidates = [
        Path(__file__).resolve().parents[1] / "data",
        Path.cwd() / "data",
        Path("data"),
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return candidates[0]


def get_llm_client() -> BaseLLMClient:
    """Return configured LLM client (allows test injection via set_llm_client)."""
    global _LLM_CLIENT_OVERRIDE
    if _LLM_CLIENT_OVERRIDE is not None:
        return _LLM_CLIENT_OVERRIDE
    return GeminiClient()


def set_llm_client(client: Optional[BaseLLMClient]) -> None:
    """Override the active LLM client for testing."""
    global _LLM_CLIENT_OVERRIDE
    _LLM_CLIENT_OVERRIDE = client


def check_ip_rate_limit(ip: str, limit: int = 5, window_sec: float = 60.0) -> bool:
    """In-memory rate limiter per IP address for expensive refresh calls."""
    now = time.time()
    history = _IP_REFRESH_LOG.setdefault(ip, [])
    # Evict timestamps outside the sliding window
    history = [t for t in history if now - t < window_sec]
    _IP_REFRESH_LOG[ip] = history
    if len(history) >= limit:
        return False
    history.append(now)
    return True


def find_correct_option_index(expression: str, options: List[Any]) -> int:
    """Recomputes true correct option index from expression via AST arithmetic evaluation.

    Never trusts stored `correct_index`.
    """
    try:
        computed = evaluate_expression(expression)
    except Exception as exc:
        logger.warning(f"Failed to evaluate expression '{expression}': {exc}")
        return -1

    target_str = str(computed).strip().lower()

    # 1. Exact Fraction comparison
    try:
        target_frac = safe_fraction(computed)
        for idx, opt in enumerate(options):
            txt = opt.get("text", "") if isinstance(opt, dict) else opt.text
            norm_key, opt_frac = normalize_option(txt)
            if opt_frac is not None and opt_frac == target_frac:
                return idx
    except Exception:
        pass

    # 2. Canonical string or remainder format comparison
    for idx, opt in enumerate(options):
        txt = opt.get("text", "") if isinstance(opt, dict) else opt.text
        norm_key, _ = normalize_option(txt)
        clean_opt = (
            norm_key.replace("frac:", "")
            .replace("ratio:", "")
            .replace("rem:", "")
            .strip()
            .lower()
        )
        clean_raw = str(txt).strip().lower()
        if clean_opt == target_str or clean_raw == target_str or norm_key == target_str:
            return idx

    return -1


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/api/health",
    response_model=Dict[str, Any],
    responses={500: {"model": ErrorEnvelope}},
)
def health():
    """System health check and engine metadata."""
    return {
        "status": "online",
        "version": "1.0.0",
        "time": datetime.now(timezone.utc).isoformat(),
        "engine": "FastAPI + Python 3.11",
    }


@app.get(
    "/api/topics",
    response_model=List[TopicResponse],
    responses={404: {"model": ErrorEnvelope}},
)
def get_topics(grade: Optional[int] = Query(None, description="Filter topics by grade (5 or 6)")):
    """Retrieve curriculum registry with dynamically computed `playable` status and `content_source`."""
    data_dir = get_data_dir()
    topics_file = data_dir / "topics.json"
    if not topics_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topics registry not found",
        )

    with open(topics_file, "r", encoding="utf-8") as f:
        topics_data = json.load(f)

    bank_dir = data_dir / "bank"
    results: List[TopicResponse] = []

    for t in topics_data:
        topic_id = t["id"]
        topic_grade = t["grade"]

        if grade is not None and topic_grade != grade:
            continue

        bank_file = bank_dir / f"{topic_id}.json"
        is_playable = False
        content_source = "coming-soon"

        if bank_file.is_file():
            try:
                with open(bank_file, "r", encoding="utf-8") as bf:
                    bank_data = json.load(bf)
                questions = bank_data.get("questions", [])

                easy_count = 0
                med_count = 0
                hard_count = 0
                verified_count = 0

                for q in questions:
                    if q.get("provenance") == "verified":
                        verified_count += 1
                        diff = q.get("difficulty")
                        if diff == "easy":
                            easy_count += 1
                        elif diff == "medium":
                            med_count += 1
                        elif diff == "hard":
                            hard_count += 1

                if (
                    len(questions) >= 9
                    and verified_count == len(questions)
                    and easy_count >= 3
                    and med_count >= 3
                    and hard_count >= 3
                ):
                    is_playable = True
                    content_source = "verified-bank"
                elif len(questions) > 0:
                    content_source = "partial-bank"
            except Exception as e:
                logger.warning(f"Error reading bank for topic {topic_id}: {e}")

        topic_resp = TopicResponse(
            **t,
            playable=is_playable,
            content_source=content_source,
        )
        results.append(topic_resp)

    return results


@app.get(
    "/api/lesson/{topic_id}",
    response_model=Dict[str, Any],
    responses={404: {"model": ErrorEnvelope}},
)
def get_lesson(topic_id: str):
    """Retrieve verified lesson for a given topic."""
    data_dir = get_data_dir()
    lesson_file = data_dir / "lessons" / f"{topic_id}.json"
    if not lesson_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson for topic '{topic_id}' not found",
        )

    with open(lesson_file, "r", encoding="utf-8") as f:
        lesson_data = json.load(f)

    lesson_data["source"] = "offline"
    return lesson_data


@app.get(
    "/api/questions/{topic_id}",
    response_model=Dict[str, Any],
    responses={404: {"model": ErrorEnvelope}},
)
def get_questions(
    topic_id: str,
    difficulty: Optional[str] = Query(None, description="Filter by difficulty (easy, medium, hard)"),
    exclude: Optional[str] = Query(None, description="Comma-separated question IDs to exclude"),
    limit: Optional[int] = Query(10, ge=1, le=50, description="Maximum questions to return"),
):
    """Retrieve verified questions for a topic, re-verifying mathematical accuracy at load time."""
    data_dir = get_data_dir()
    bank_file = data_dir / "bank" / f"{topic_id}.json"
    if not bank_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question bank for topic '{topic_id}' not found",
        )

    with open(bank_file, "r", encoding="utf-8") as bf:
        bank_data = json.load(bf)

    raw_questions = bank_data.get("questions", [])
    exclude_set = set(re.split(r"[\s,]+", exclude.strip())) if exclude else set()

    verified_questions: List[Dict[str, Any]] = []

    for q in raw_questions:
        q_id = q.get("id")
        if q_id in exclude_set:
            continue

        if difficulty and q.get("difficulty") != difficulty:
            continue

        # Re-verify at load: skip broken math or corrupt questions
        try:
            ver_res = verify_question(q)
            if not ver_res.passed:
                logger.warning(f"Skipping corrupt bank question {q_id}: {ver_res.reasons}")
                continue
        except Exception as exc:
            logger.warning(f"Exception during load-time verification of {q_id}: {exc}")
            continue

        verified_questions.append(q)
        if limit is not None and len(verified_questions) >= limit:
            break

    return {
        "topic_id": topic_id,
        "questions": verified_questions,
        "total": len(verified_questions),
        "source": "offline",
    }


@app.post(
    "/api/answer",
    response_model=AnswerResponse,
    responses={404: {"model": ErrorEnvelope}, 422: {"model": ErrorEnvelope}},
)
def submit_answer(payload: AnswerRequest):
    """Submit student answer, recomputing true correctness from expression and diagnosing misconceptions."""
    data_dir = get_data_dir()
    bank_file = data_dir / "bank" / f"{payload.topic_id}.json"
    if not bank_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question bank for topic '{payload.topic_id}' not found",
        )

    with open(bank_file, "r", encoding="utf-8") as bf:
        bank_data = json.load(bf)

    question = None
    for q in bank_data.get("questions", []):
        if q.get("id") == payload.question_id:
            question = q
            break

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question '{payload.question_id}' not found in topic '{payload.topic_id}'",
        )

    expression = question.get("expression", "")
    options = question.get("options", [])
    if payload.chosen_index < 0 or payload.chosen_index >= len(options):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"chosen_index {payload.chosen_index} out of bounds for {len(options)} options",
        )

    # Recompute the correct answer from `expression` (never trust the stored index)
    true_correct_index = find_correct_option_index(expression, options)
    if true_correct_index == -1:
        # Fallback to stored index if expression evaluation fails
        true_correct_index = question.get("correct_index", 0)

    is_correct = payload.chosen_index == true_correct_index

    # Misconception diagnosis
    diagnosis: Optional[DiagnosisModel] = None
    if not is_correct:
        chosen_opt = options[payload.chosen_index]
        misc_id = chosen_opt.get("misconception_id") or chosen_opt.get("misconception")
        if misc_id:
            m = get_misconception_by_id(misc_id)
            if m:
                diagnosis = DiagnosisModel(
                    kid_label=m.get("kid_label", misc_id),
                    diagnosis=m.get("diagnosis", "A common conceptual error was detected."),
                    why_it_fails=m.get("why_it_fails", ""),
                    mini_example=m.get("mini_example", ""),
                )

    # Adaptive mechanics, BKT mastery update, XP & combo
    state = payload.state or {}
    prev_combo = state.get("combo", 0)
    new_combo = (prev_combo + 1) if is_correct else 0

    diff_str = question.get("difficulty", "medium")
    xp_awarded = compute_xp(diff_str, combo=new_combo, attempt_number=payload.attempt) if is_correct else 0

    p_known = float(state.get("p_known", 0.20))
    p_known_updated = update_bkt(p_known, is_correct, difficulty=diff_str)

    curr_difficulty = Difficulty(diff_str)
    consecutive_correct = state.get("consecutive_correct", 0)
    next_diff_enum, _ = update_difficulty(curr_difficulty, consecutive_correct, is_correct)

    return AnswerResponse(
        correct=is_correct,
        correct_index=true_correct_index,
        explanation=question.get("explanation", ""),
        hint=question.get("hint", "Check your calculations carefully."),
        diagnosis=diagnosis,
        xp_awarded=xp_awarded,
        next_difficulty=next_diff_enum.value,
        p_known_updated=p_known_updated,
        combo=new_combo,
    )


@app.post(
    "/api/lesson/{topic_id}/refresh",
    response_model=Dict[str, Any],
    responses={404: {"model": ErrorEnvelope}},
)
def refresh_lesson(topic_id: str, request: Request):
    """Generate fresh AI lesson with 15s timeout, verifier gating, and graceful offline fallback."""
    topic = get_topic_by_id(topic_id)
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_id}' not found in curriculum",
        )

    # 1. In-memory per-IP rate limit (max 5 requests per minute)
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not check_ip_rate_limit(client_ip, limit=5, window_sec=60.0):
        # Return offline stored lesson with reason code
        stored = get_lesson(topic_id)
        stored["source"] = "offline"
        stored["reason_code"] = "RATE_LIMITED"
        return stored

    # 2. In-memory TTL cache (5-minute TTL)
    now = time.time()
    if topic_id in _LESSON_CACHE:
        cached_data, expires_at = _LESSON_CACHE[topic_id]
        if now < expires_at:
            resp = dict(cached_data)
            resp["source"] = "ai-live"
            return resp

    # 3. Live LLM call with hard 15s timeout
    client = get_llm_client()
    try:
        prompt = build_lesson_prompt(topic_id)
        generated_json = client.generate_json(prompt, timeout=15.0)

        # Validate with Pydantic
        lesson_obj = Lesson.model_validate(generated_json)

        # Mathematical verification
        ver_res = verify_lesson(lesson_obj)
        if not ver_res.passed:
            raise VerificationError(f"Lesson math verification failed: {ver_res.reasons}")

        data = lesson_obj.model_dump()
        _LESSON_CACHE[topic_id] = (data, now + 300.0)  # 5-min TTL
        data["source"] = "ai-live"
        return data

    except Exception as exc:
        reason_code = "OFFLINE_FALLBACK"
        if isinstance(exc, (LLMTimeoutError, TimeoutError)):
            reason_code = "TIMEOUT"
        elif isinstance(exc, (LLMInvalidJSONError, json.JSONDecodeError)):
            reason_code = "INVALID_JSON"
        elif isinstance(exc, (VerificationError,)):
            reason_code = "WRONG_MATH"
        elif isinstance(exc, (ValidationError,)):
            reason_code = "SCHEMA_ERROR"
        else:
            reason_code = f"ERROR_{type(exc).__name__}"

        logger.warning(f"Lesson refresh fallback for {topic_id} triggered by {exc} (reason: {reason_code})")
        # On ANY failure, return the stored lesson with source: offline and reason code
        try:
            stored = get_lesson(topic_id)
            stored["source"] = "offline"
            stored["reason_code"] = reason_code
            return stored
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stored lesson for topic '{topic_id}' not found",
            )


@app.get(
    "/api/infographic/{topic_id}",
    response_model=Dict[str, Any],
    responses={404: {"model": ErrorEnvelope}},
)
def get_infographic(topic_id: str):
    """Retrieve structured infographic steps with Pollinations AI image URL and fallback image path."""
    data_dir = get_data_dir()
    infographic_file = data_dir / "infographics" / f"{topic_id}.json"
    if not infographic_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Infographic for topic '{topic_id}' not found",
        )

    with open(infographic_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Build Pollinations image URL from sanitized prompt
    raw_prompt = data.get("image_prompt", f"dark fantasy mathematical illustration of {topic_id}")
    clean_prompt = re.sub(r"[^a-zA-Z0-9\s,\-\.]", " ", raw_prompt).strip()
    clean_prompt = re.sub(r"\s+", " ", clean_prompt)[:200]
    encoded_prompt = urllib.parse.quote_plus(clean_prompt)
    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=600&nologo=true"

    data["image_url"] = pollinations_url
    data["fallback_image"] = f"/fallback/infographics/{topic_id}.svg"
    data["source"] = "offline"
    return data


@app.get(
    "/api/explainer/{topic_id}",
    response_model=Dict[str, Any],
    responses={404: {"model": ErrorEnvelope}},
)
def get_explainer(topic_id: str):
    """Retrieve audio-narratable explainer script."""
    data_dir = get_data_dir()
    explainer_file = data_dir / "explainers" / f"{topic_id}.json"
    if not explainer_file.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Explainer script for topic '{topic_id}' not found",
        )

    with open(explainer_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["source"] = "offline"
    return data


@app.get(
    "/api/eval",
    response_model=Dict[str, Any],
)
def get_eval_results():
    """Retrieve offline benchmark evaluation metrics or a graceful empty state."""
    data_dir = get_data_dir()
    eval_file = data_dir / "eval_results.json"
    if eval_file.is_file():
        try:
            with open(eval_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["source"] = "offline"
            return data
        except Exception as e:
            logger.warning(f"Error reading eval_results.json: {e}")

    return {
        "status": "no_eval_data",
        "models": [],
        "benchmarks": [],
        "source": "offline",
    }
