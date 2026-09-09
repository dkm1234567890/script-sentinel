from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.pipeline import analyze_parallel_demo, analyze_screenplay


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Script Sentinel",
    description="Source-backed screenplay pre-clearance research with Gemini, Google ADK, and Parallel Search.",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/health")
async def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "service": "script-sentinel",
        "configured": not settings.missing_credentials(),
        "missing": settings.missing_credentials(),
    }


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)) -> dict:
    settings = get_settings()
    if missing := settings.missing_credentials():
        raise HTTPException(
            status_code=503,
            detail=f"Service setup is incomplete: {', '.join(missing)}",
        )
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Please upload a PDF screenplay.")

    data = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"The PDF must be {settings.max_upload_mb} MB or smaller.",
        )
    if not data.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="The uploaded file is not a valid PDF.")

    try:
        report = await analyze_screenplay(data)
        return report.model_dump(mode="json")
    except Exception as exc:
        if (
            settings.allow_parallel_demo_fallback
            and file.filename == "synthetic-screenplay.pdf"
        ):
            report = analyze_parallel_demo()
            return report.model_dump(mode="json")
        raise HTTPException(
            status_code=502,
            detail=f"Analysis could not be completed ({type(exc).__name__}). Please retry.",
        ) from exc
