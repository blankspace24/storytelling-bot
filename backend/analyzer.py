"""
Script analyzer module using LangChain + Mistral AI.
"""

import asyncio
import logging
from typing import Optional

from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from backend.models import ScriptAnalysis
from backend.prompts import SYSTEM_PROMPT, build_analysis_prompt
from config.settings import settings


logger = logging.getLogger(__name__)


class ScriptAnalyzer:
    def __init__(self, model: Optional[str] = None):
        if not settings.MISTRAL_API_KEY:
            logger.error("Missing MISTRAL_API_KEY in environment")
            raise ValueError(
                "Mistral API key is required. Set MISTRAL_API_KEY in your .env file."
            )

        self.model_name = model or settings.DEFAULT_MODEL

        logger.info(f"Initializing ScriptAnalyzer with model={self.model_name}")

        self.llm = ChatMistralAI(
            model=self.model_name,
            api_key=settings.MISTRAL_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{user_prompt}"),
        ])

        self.parser = JsonOutputParser()

        self.chain = self.prompt_template | self.llm | self.parser

        logger.debug("LangChain pipeline initialized")

    async def analyze_async(
        self,
        title: str,
        script_text: str,
    ) -> ScriptAnalysis:

        if not script_text.strip():
            logger.warning("Empty script text received")
            raise ValueError("Script text cannot be empty.")

        logger.info(f"Starting analysis for title='{title}'")

        user_prompt = build_analysis_prompt(title, script_text)
        max_retries = settings.LLM_MAX_RETRIES
        last_error = None

        for attempt in range(max_retries):
            try:
                logger.debug(f"Attempt {attempt + 1}/{max_retries}")

                # ✅ Timeout added here (30 seconds)
                result: dict = await asyncio.wait_for(
                    self.chain.ainvoke({
                        "system_prompt": SYSTEM_PROMPT,
                        "user_prompt": user_prompt,
                    }),
                    timeout=30  # ⏱️ hard timeout
                )

                logger.debug("LLM response received")

                analysis = ScriptAnalysis(**result)

                logger.info(
                    f"Analysis successful for title='{title}' "
                    f"on attempt {attempt + 1}"
                )

                return analysis

            except asyncio.TimeoutError as e:
                last_error = e

                logger.error(
                    f"Timeout (30s) on attempt {attempt + 1} for title='{title}'",
                    exc_info=True,
                )

            except Exception as e:
                last_error = e

                logger.error(
                    f"Attempt {attempt + 1} failed | "
                    f"{type(e).__name__}: {e}",
                    exc_info=True,
                )

            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                logger.warning(f"Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

        logger.critical(
            f"Analysis failed after {max_retries} attempts for title='{title}'"
        )

        raise RuntimeError(
            f"Analysis failed after {max_retries} attempts. "
            f"Last error: {type(last_error).__name__}: {last_error}"
        )

    def analyze(self, title: str, script_text: str) -> ScriptAnalysis:
        logger.info(f"Starting sync analysis for title='{title}'")

        try:
            loop = asyncio.get_event_loop()

            if loop.is_running():
                logger.debug("Running inside existing event loop")

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
            logger.warning("Fallback to asyncio.run")
            return asyncio.run(self.analyze_async(title, script_text))