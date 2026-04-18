"""
Prompt engineering module for script analysis.

Techniques used:
1. Expert Role Assignment — professional script analyst persona
2. Structured Analysis Framework — sequential dimension analysis
3. Scoring Rubric — calibrated 0-100 criteria
4. Storytelling Vocabulary — specific narrative terms
5. Schema-Constrained Output — JSON mode enforcement
"""


SYSTEM_PROMPT = """You are a senior script analyst and story consultant at a content intelligence platform \
specializing in short-form scripted content (short films, web series, social media scripts). \
You have 15+ years of experience in screenwriting, narrative design, and audience engagement analysis.

Your role is to provide structured, actionable analysis that helps creators understand \
the quality and engagement potential of their scripts. Your analysis must be:
- Specific and grounded in the actual script content (cite exact lines when relevant)
- Professional yet accessible (avoid overly academic language)
- Constructive and actionable (every critique should come with a clear path forward)
- Calibrated (scores should reflect realistic assessment, not inflate to please)

SCORING RUBRIC for engagement factors (0-100):
- 0-20: Fundamentally missing or broken
- 21-40: Present but weak, needs significant work
- 41-60: Adequate, functional but not memorable
- 61-80: Strong, above average with clear appeal
- 81-100: Exceptional, industry-leading quality

ENGAGEMENT FACTORS to evaluate:
1. Opening Hook — Does the script grab attention in the first few lines?
2. Character Conflict — Is there meaningful tension between characters or within a character?
3. Emotional Tension — Does the scene create genuine emotional stakes?
4. Dialogue Quality — Is the dialogue natural, revealing, and purposeful?
5. Cliffhanger/Resolution — Does the ending leave impact or create anticipation?

You must respond with valid JSON matching the exact schema provided."""


def build_analysis_prompt(title: str, script_text: str) -> str:
    """
    Construct the user prompt for script analysis.
    
    Args:
        title: The title of the script
        script_text: The full script text to analyze
        
    Returns:
        A formatted prompt string
    """
    return f"""Analyze the following script and provide a comprehensive structured analysis.

--- SCRIPT ---
Title: {title}

{script_text}
--- END SCRIPT ---

Provide your analysis as a JSON object with the following structure:

1. **summary** (string): A concise 3-4 line summary capturing the core story, characters, and central conflict.

2. **emotion_analysis** (object):
   - **dominant_emotions** (array of strings): The top 3-5 emotions present across the script.
   - **emotional_arc** (array of objects): A chronological sequence of emotional beats, each with:
     - "moment": brief description of the story moment
     - "emotion": the dominant emotion at this point
     - "intensity": a float from 0.0 (neutral) to 1.0 (extreme)
   - **arc_description** (string): One-line description of the overall emotional trajectory.

3. **engagement** (object):
   - **overall_score** (float, 0-100): The overall engagement potential score.
   - **factors** (array of objects): Score breakdown for each factor:
     - "name": factor name (Opening Hook, Character Conflict, Emotional Tension, Dialogue Quality, Cliffhanger/Resolution)
     - "score": float 0-100
     - "explanation": why this score was given
   - **verdict** (string): One-line verdict on engagement potential.

4. **suggestions** (array of 4-6 objects): Actionable improvement suggestions, each with:
   - "category": one of Pacing, Conflict, Dialogue, Emotional Impact, Structure, Character Development
   - "suggestion": the specific improvement
   - "priority": High, Medium, or Low
   - "example": optional concrete example of how to implement

5. **cliffhanger** (object): The most suspenseful moment:
   - "moment_text": the exact line or moment from the script
   - "explanation": why it works as a suspense point
   - "storytelling_technique": the narrative technique used

Ensure all scores follow the scoring rubric strictly. Be specific and reference actual script content."""
