"""
Script analyzer module using LangChain + Mistral AI.

Architecture:
- LangChain's ChatMistralAI as the LLM wrapper
- LangChain's JsonOutputParser for structured response parsing
- LangChain's ChatPromptTemplate for clean prompt construction
- asyncio-native: uses ainvoke() for non-blocking async calls
- FastAPI async endpoint calls await analyzer.analyze_async()
- Exponential backoff retry via asyncio.sleep (non-blocking)

Model: mistral-large-latest (Mistral's largest, most capable model)
API:   https://api.mistral.ai/v1
"""

import asyncio
from typing import Optional

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from backend.models import ScriptAnalysis
from backend.prompts import SYSTEM_PROMPT, build_analysis_prompt
from config.settings import settings


class ScriptAnalyzer:
    """
    Analyzes scripts using LangChain + Mistral AI via async invocation.

    Uses a LangChain LCEL (LangChain Expression Language) chain:
        prompt | llm | json_parser

    This makes the pipeline composable, observable, and async-ready.
    """

    def __init__(self, model: Optional[str] = None):
        if not settings.MISTRAL_API_KEY:
            raise ValueError(
                "Mistral API key is required. Set MISTRAL_API_KEY in your .env file."
            )

        self.model_name = model or settings.DEFAULT_MODEL

        # ── LangChain Mistral LLM ──
        self.llm = ChatMistralAI(
            model=self.model_name,
            api_key=settings.MISTRAL_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
        )

        # ── LangChain Prompt Template ──
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{user_prompt}"),
        ])

        # ── LangChain Output Parser ──
        self.parser = JsonOutputParser()

        # ── LCEL Chain: prompt | llm | parser ──
        self.chain = self.prompt_template | self.llm | self.parser

    async def analyze_async(
        self,
        title: str,
        script_text: str,
    ) -> ScriptAnalysis:
        """
        Asynchronously analyze a script using LangChain's async invoke.

        Uses asyncio-native non-blocking retries with exponential backoff.
        The LangChain chain (prompt | llm | parser) is invoked with ainvoke().

        Args:
            title: The title of the script
            script_text: The full script text

        Returns:
            A validated ScriptAnalysis Pydantic object
        """
        if not script_text.strip():
            raise ValueError("Script text cannot be empty.")

        user_prompt = build_analysis_prompt(title, script_text)
        max_retries = settings.LLM_MAX_RETRIES
        last_error = None

        for attempt in range(max_retries):
            try:
                # Non-blocking async LangChain chain invocation
                result: dict = await self.chain.ainvoke({
                    "system_prompt": SYSTEM_PROMPT,
                    "user_prompt": user_prompt,
                })

                # Validate against Pydantic schema
                analysis = ScriptAnalysis(**result)
                return analysis

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Non-blocking async sleep (exponential backoff: 1s, 2s, 4s)
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue
                break

        raise RuntimeError(
            f"Analysis failed after {max_retries} attempts. "
            f"Last error: {type(last_error).__name__}: {last_error}"
        )

    def analyze(self, title: str, script_text: str) -> ScriptAnalysis:
        """
        Synchronous wrapper around analyze_async for compatibility.
        Runs the async method in the current or a new event loop.
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run, self.analyze_async(title, script_text)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    self.analyze_async(title, script_text)
                )
        except RuntimeError:
            return asyncio.run(self.analyze_async(title, script_text))
