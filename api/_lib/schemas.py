from __future__ import annotations
from enum import Enum
from typing import List, Optional, Any, Dict, Union
from pydantic import BaseModel, Field, model_validator


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Option(BaseModel):
    id: Optional[str] = Field(None, description="Option identifier A, B, C, D")
    text: str = Field(..., min_length=1, description="Option text or number representation")
    misconception: Optional[str] = Field(None, description="Tag identifying the conceptual mistake if wrong; null if correct")
    misconception_id: Optional[str] = Field(None, description="Tag/ID identifying the conceptual mistake if wrong; null if correct")


class Question(BaseModel):
    id: str = Field(default="q-1", min_length=1)
    topic_id: str = Field(..., min_length=1)
    standard: str = Field(default="standard", min_length=1)
    difficulty: Difficulty
    verifier_type: str = Field(default="fraction_arithmetic", min_length=1)
    stem: str = Field(..., min_length=1)
    expression: str = Field(..., min_length=1)
    params: Optional[Union[List[Any], Dict[str, Any]]] = Field(None, description="Parameters used to generate the question")
    template_id: Optional[str] = Field(None, description="Identifier of the stem template used for this question")
    answer: Optional[str] = Field(None, description="Canonical answer text")
    options: List[Option]
    correct_index: int = Field(..., ge=0, le=3)
    explanation: str = Field(..., min_length=1)
    hint: str = Field(default="Remember to check each step.", min_length=1)
    model: str = Field(default="gemini-1.5-flash", min_length=1)
    prompt_version: str = Field(default="v2", min_length=1)
    verified: bool = Field(default=False)
    provenance: Optional[str] = Field(default=None, description="Provenance status: 'verified' or 'unchecked'")

    @model_validator(mode="after")
    def validate_options_structure(self) -> Question:
        if not self.stem.strip():
            raise ValueError("stem cannot be empty or whitespace")
        if not self.expression.strip():
            raise ValueError("expression cannot be empty or whitespace")
        if not self.explanation.strip():
            raise ValueError("explanation cannot be empty or whitespace")
        if len(self.options) != 4:
            raise ValueError(f"Question must contain exactly 4 options, found {len(self.options)}")
        if not (0 <= self.correct_index < 4):
            raise ValueError(f"correct_index must be between 0 and 3, got {self.correct_index}")
        return self


class WorkedStep(BaseModel):
    step: int = Field(..., ge=1)
    text: str = Field(..., min_length=1)
    math: str = Field(..., min_length=1)


class Lesson(BaseModel):
    title: str = Field(..., min_length=1)
    big_idea: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=1)
    worked_example: List[WorkedStep] = Field(..., min_length=1)
    key_vocab: List[str] = Field(default_factory=list)
    real_world_example: str = Field(..., min_length=1)
    common_mistakes: List[str] = Field(default_factory=list)


class InfographicStep(BaseModel):
    label: str = Field(..., min_length=1)
    detail: str = Field(..., min_length=1)
    math: str = Field(..., min_length=1)


class InfographicData(BaseModel):
    title: str = Field(..., min_length=1)
    steps: List[InfographicStep] = Field(..., min_length=1)
    example: str = Field(..., min_length=1)
    image_prompt: str = Field(..., min_length=1)


class Slide(BaseModel):
    title: str = Field(..., min_length=1)
    visual_hint: str = Field(..., min_length=1)
    narration: str = Field(..., min_length=1)
    highlight: str = Field(..., min_length=1)


class ExplainerScript(BaseModel):
    slides: List[Slide] = Field(..., min_length=1)


class MisconceptionEntry(BaseModel):
    tag: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)

class RegistryMisconception(BaseModel):
    id: str = Field(..., min_length=1)
    topic_ids: List[str] = Field(..., min_length=1)
    kid_label: str = Field(..., min_length=1)
    diagnosis: str = Field(..., min_length=1)
    why_it_fails: str = Field(..., min_length=1)
    mini_example: str = Field(..., min_length=1)
    applies_when: str = Field(..., min_length=1)


class TopicEntry(BaseModel):
    id: str = Field(..., min_length=1)
    grade: int = Field(..., ge=5, le=6)
    realm: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    fantasy_name: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1)
    standard: str = Field(..., min_length=1)
    standard_text: str = Field(..., min_length=1)
    standard_verified: bool
    verifier_type: str = Field(..., min_length=1)
    misconceptions: List[str] = Field(default_factory=list)
    tier: str = Field(..., min_length=1)
    unlock_order: int = Field(..., ge=1)
    icon: str = Field(..., min_length=1)
    island_theme: str = Field(..., min_length=1)


class TopicDerivedMisconception(BaseModel):
    id: str
    kid_label: str


class TopicResponse(BaseModel):
    id: str = Field(..., min_length=1)
    grade: int = Field(..., ge=5, le=6)
    realm: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    fantasy_name: str = Field(..., min_length=1)
    domain: str = Field(..., min_length=1)
    standard: str = Field(..., min_length=1)
    standard_text: str = Field(..., min_length=1)
    standard_verified: bool
    verifier_type: str = Field(..., min_length=1)
    misconceptions: List[TopicDerivedMisconception] = Field(default_factory=list)
    tier: str = Field(..., min_length=1)
    unlock_order: int = Field(..., ge=1)
    play_order: Optional[int] = Field(default=None)
    icon: str = Field(..., min_length=1)
    island_theme: str = Field(..., min_length=1)
    playable: bool = Field(default=False)
    content_source: str = Field(default="coming-soon")



class BankFile(BaseModel):
    topic_id: str = Field(..., min_length=1)
    version: str = Field(default="1.0.0")
    questions: List[Question] = Field(default_factory=list)


class EvalResult(BaseModel):
    model: str = Field(..., min_length=1)
    prompt_version: str = Field(..., min_length=1)
    total_evaluated: int = Field(..., ge=0)
    schema_valid_rate: float = Field(..., ge=0.0, le=1.0)
    math_correct_rate: float = Field(..., ge=0.0, le=1.0)
    distractor_quality: float = Field(..., ge=0.0, le=1.0)
    avg_latency_ms: float = Field(..., ge=0.0)
    rejected_samples: List[Dict[str, Any]] = Field(default_factory=list)


class DiagnosisModel(BaseModel):
    kid_label: str
    diagnosis: str
    why_it_fails: str
    mini_example: str


class AnswerRequest(BaseModel):
    topic_id: str = Field(..., min_length=1)
    question_id: str = Field(..., min_length=1)
    chosen_index: int = Field(..., ge=0, le=3)
    attempt: int = Field(default=1, ge=1)
    state: Optional[Dict[str, Any]] = None


class AnswerResponse(BaseModel):
    correct: bool
    correct_index: int
    explanation: str
    hint: str
    diagnosis: Optional[DiagnosisModel] = None
    xp_awarded: int
    next_difficulty: str
    p_known_updated: float
    combo: int


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorEnvelope(BaseModel):
    error: ErrorDetail

