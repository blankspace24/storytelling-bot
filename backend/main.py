"""
FastAPI REST API for StoryLens script analysis.
"""

import asyncio
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.models import ScriptInput, ScriptAnalysis
from backend.analyzer import ScriptAnalyzer
from config.settings import settings


# ─────────────────────────────────────────────
# Logging Configuration
# ─────────────────────────────────────────────
logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_NAME + " API",
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)


# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Startup Event
# ─────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Starting StoryLens API")
    logger.info(f"Model: {settings.DEFAULT_MODEL}")
    logger.info(f"Provider: Mistral AI")


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    logger.debug("Health check called")

    return {
        "status": "healthy",
        "service": "StoryLens API",
        "model": settings.DEFAULT_MODEL,
        "provider": "Mistral AI",
    }


# ─────────────────────────────────────────────
# Analyze Endpoint
# ─────────────────────────────────────────────
@app.post("/api/analyze", response_model=ScriptAnalysis)
async def analyze_script(input_data: ScriptInput, request: Request):
    request_id = id(request)

    logger.info(
        f"[{request_id}] Incoming request | title='{input_data.title}'"
    )

    if not settings.MISTRAL_API_KEY:
        logger.error(f"[{request_id}] Missing MISTRAL_API_KEY")
        raise HTTPException(
            status_code=500,
            detail="MISTRAL_API_KEY not configured on server"
        )

    try:
        analyzer = ScriptAnalyzer(model=input_data.model)

        # ✅ Request-level timeout (30 seconds)
        analysis = await asyncio.wait_for(
            analyzer.analyze_async(
                title=input_data.title,
                script_text=input_data.script_text,
            ),
            timeout=30
        )

        logger.info(f"[{request_id}] Analysis completed successfully")

        return analysis

    except asyncio.TimeoutError:
        logger.error(f"[{request_id}] Request timed out after 30s")

        raise HTTPException(
            status_code=504,
            detail="Request timed out after 30 seconds"
        )

    except ValueError as e:
        logger.warning(f"[{request_id}] Validation error: {e}")

        raise HTTPException(status_code=400, detail=str(e))

    except RuntimeError as e:
        logger.error(f"[{request_id}] Analyzer failure: {e}")

        raise HTTPException(status_code=502, detail=str(e))

    except Exception as e:
        logger.critical(
            f"[{request_id}] Unexpected error: {type(e).__name__}: {e}",
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


# ─────────────────────────────────────────────
# Run Server
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Uvicorn server...")

    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
    )