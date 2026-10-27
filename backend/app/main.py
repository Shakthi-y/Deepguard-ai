from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.agents import orchestrator
from app.storage import get_analysis, list_history
from app.models.deepfake_detector import get_model_status
from app.services.gemini_service import chat_answer

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "model": get_model_status(),
    }


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    analysis = orchestrator.run_pipeline(content, file.content_type or "", file.filename or "upload.jpg")

    if analysis.get("error"):
        raise HTTPException(status_code=422, detail={
            "message": "Analysis could not be completed.",
            "reason": analysis["error"],
            "agent_log": analysis["agent_log"],
        })

    return analysis


@app.get("/api/analysis/{analysis_id}")
def get_analysis_endpoint(analysis_id: str):
    analysis = get_analysis(analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return analysis


@app.get("/api/history")
def history(limit: int = 50):
    return {"items": list_history(limit)}


@app.get("/api/report/{analysis_id}")
def report(analysis_id: str):
    path = orchestrator.generate_report(analysis_id)
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Analysis not found or report generation failed.")
    return FileResponse(path, media_type="application/pdf",
                         filename=f"DeepGuard_Report_{analysis_id}.pdf")


@app.post("/api/chat")
async def chat(payload: dict):
    question = payload.get("question", "")
    analysis_id = payload.get("analysis_id")
    context = get_analysis(analysis_id) if analysis_id else {}
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    answer = chat_answer(question, context or {})
    return {"answer": answer}
