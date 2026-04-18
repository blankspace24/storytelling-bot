"""
FastAPI REST API for StoryLens script analysis.

Endpoints:
  POST /api/analyze  — Analyze a script and return structured insights
  GET  /api/health   — Health check
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models import ScriptInput, ScriptAnalysis
from backend.analyzer import ScriptAnalyzer
from config.settings import settings

app = FastAPI(
    title=settings.APP_NAME + " API",
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
)

# CORS — allow Streamlit frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "StoryLens API",
        "model": settings.DEFAULT_MODEL,
        "provider": "Mistral AI",
    }


@app.post("/api/analyze", response_model=ScriptAnalysis)
async def analyze_script(input_data: ScriptInput):
    """
    Analyze a script and return structured insights.

    Fully async: FastAPI awaits the LangChain ainvoke() call directly,
    keeping the server non-blocking while the LLM processes the request.
    """
    if not settings.MISTRAL_API_KEY:
        raise HTTPException(status_code=500, detail="MISTRAL_API_KEY not configured on server")
    
    try:
        analyzer = ScriptAnalyzer(model=input_data.model)
        # Directly await the async method — no thread blocking
        analysis = await analyzer.analyze_async(
            title=input_data.title,
            script_text=input_data.script_text,
        )
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
