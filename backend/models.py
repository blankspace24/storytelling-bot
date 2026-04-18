"""
Pydantic models for structured script analysis output.

These models define the exact JSON schema that the LLM must return,
ensuring consistent, validated responses for every analysis.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class ScriptInput(BaseModel):
    """Input model for the /analyze endpoint."""
    title: str = Field(default="Untitled", description="Title of the script")
    script_text: str = Field(description="The full script text to analyze")
    model: str = Field(default="mistral-large-latest", description="Mistral model to use")


class EmotionBeat(BaseModel):
    """A single emotional beat in the story's arc."""
    moment: str = Field(description="Brief description of the story moment")
    emotion: str = Field(description="The dominant emotion at this moment")
    intensity: float = Field(description="Emotional intensity from 0.0 to 1.0", ge=0.0, le=1.0)


class EmotionAnalysis(BaseModel):
    """Complete emotional analysis of the script."""
    dominant_emotions: List[str] = Field(description="Top 3-5 dominant emotions across the script")
    emotional_arc: List[EmotionBeat] = Field(description="Sequence of emotional beats")
    arc_description: str = Field(description="One-line description of the overall emotional trajectory")


class EngagementFactor(BaseModel):
    """A single factor contributing to the engagement score."""
    name: str = Field(description="Factor name")
    score: float = Field(description="Score from 0 to 100", ge=0, le=100)
    explanation: str = Field(description="Brief explanation of the score")


class EngagementScore(BaseModel):
    """Overall engagement potential assessment."""
    overall_score: float = Field(description="Overall engagement score 0-100", ge=0, le=100)
    factors: List[EngagementFactor] = Field(description="Breakdown of engagement factors")
    verdict: str = Field(description="One-line verdict on engagement potential")


class ImprovementSuggestion(BaseModel):
    """A single improvement suggestion for the script."""
    category: str = Field(description="Category: Pacing, Conflict, Dialogue, Emotional Impact, Structure, or Character Development")
    suggestion: str = Field(description="The specific improvement suggestion")
    priority: str = Field(description="Priority: High, Medium, or Low")
    example: Optional[str] = Field(default=None, description="Optional implementation example")


class CliffhangerMoment(BaseModel):
    """The most suspenseful or cliffhanger moment in the script."""
    moment_text: str = Field(description="The exact line or moment from the script")
    explanation: str = Field(description="Why this moment works as a suspense point")
    storytelling_technique: str = Field(description="The narrative technique used")


class ScriptAnalysis(BaseModel):
    """Complete structured analysis of a script."""
    summary: str = Field(description="A concise 3-4 line summary of the story")
    emotion_analysis: EmotionAnalysis = Field(description="Detailed emotional tone analysis")
    engagement: EngagementScore = Field(description="Engagement potential assessment")
    suggestions: List[ImprovementSuggestion] = Field(description="4-6 actionable improvement suggestions")
    cliffhanger: CliffhangerMoment = Field(description="The most suspenseful moment in the script")
