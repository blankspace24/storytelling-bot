from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum


# ─────────────────────────────────────────────
# Enums (STRICT CONTROL)
# ─────────────────────────────────────────────
class PriorityEnum(str, Enum):
    high = "High"
    medium = "Medium"
    low = "Low"


class CategoryEnum(str, Enum):
    pacing = "Pacing"
    conflict = "Conflict"
    dialogue = "Dialogue"
    emotional_impact = "Emotional Impact"
    structure = "Structure"
    character = "Character Development"


# ─────────────────────────────────────────────
# Input Model
# ─────────────────────────────────────────────
class ScriptInput(BaseModel):
    title: str = Field(default="Untitled", min_length=1)
    script_text: str = Field(min_length=10)
    model: str = Field(default="mistral-large-latest")

    model_config = {"extra": "forbid"}


# ─────────────────────────────────────────────
# Emotion Models
# ─────────────────────────────────────────────
class EmotionBeat(BaseModel):
    moment: str = Field(min_length=5)
    emotion: str = Field(min_length=2)
    intensity: float = Field(ge=0.0, le=1.0)

    model_config = {"extra": "forbid"}


class EmotionAnalysis(BaseModel):
    dominant_emotions: List[str] = Field(min_length=3, max_length=5)
    emotional_arc: List[EmotionBeat] = Field(min_length=3)
    arc_description: str = Field(min_length=10)

    model_config = {"extra": "forbid"}


# ─────────────────────────────────────────────
# Engagement Models
# ─────────────────────────────────────────────
class EngagementFactor(BaseModel):
    name: str = Field(min_length=2)
    score: float = Field(ge=0, le=100)
    explanation: str = Field(min_length=5)

    model_config = {"extra": "forbid"}


class EngagementScore(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    factors: List[EngagementFactor] = Field(min_length=2)
    verdict: str = Field(min_length=5)

    model_config = {"extra": "forbid"}


# ─────────────────────────────────────────────
# Suggestions
# ─────────────────────────────────────────────
class ImprovementSuggestion(BaseModel):
    category: CategoryEnum
    suggestion: str = Field(min_length=10)
    priority: PriorityEnum
    example: Optional[str] = Field(default=None)

    model_config = {"extra": "forbid"}

    @field_validator("suggestion")
    @classmethod
    def clean_text(cls, v: str) -> str:
        return v.strip()


# ─────────────────────────────────────────────
# Cliffhanger
# ─────────────────────────────────────────────
class CliffhangerMoment(BaseModel):
    moment_text: str = Field(min_length=5)
    explanation: str = Field(min_length=10)
    storytelling_technique: str = Field(min_length=5)

    model_config = {"extra": "forbid"}


# ─────────────────────────────────────────────
# Final Output Model
# ─────────────────────────────────────────────
class ScriptAnalysis(BaseModel):
    summary: str = Field(min_length=20)
    emotion_analysis: EmotionAnalysis
    engagement: EngagementScore
    suggestions: List[ImprovementSuggestion] = Field(min_length=3, max_length=6)
    cliffhanger: CliffhangerMoment

    model_config = {"extra": "forbid"}

    @field_validator("summary")
    @classmethod
    def clean_summary(cls, v: str) -> str:
        return v.strip()