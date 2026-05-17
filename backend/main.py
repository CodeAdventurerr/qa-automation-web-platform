from __future__ import annotations

import os
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from backend.ai.test_generator import AITestGenerator
from backend.core.executor import ExecutionController
from backend.core.reporting import ReportBuilder
from backend.core.security import require_api_key
from backend.models.schemas import GenerateTestsRequest, GenerateTestsResponse, Project, RunTestsRequest
from backend.storage.json_store import JsonStore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

app = FastAPI(title="AI QA Automation Web Platform", version="0.1.0")
allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Content-Type", "X-API-Key"],
)

store = JsonStore(Path(__file__).resolve().parent / "storage_data")
generator = AITestGenerator()
executor = ExecutionController()
reporter = ReportBuilder()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/generate-tests", response_model=GenerateTestsResponse, dependencies=[Depends(require_api_key)])
async def generate_tests(request: GenerateTestsRequest) -> GenerateTestsResponse:
    test_cases = await generator.generate(str(request.url), request.feature)
    project = Project(url=str(request.url), feature=request.feature, test_cases=test_cases)
    store.save_project(project)
    return GenerateTestsResponse(project_id=project.id, test_cases=project.test_cases)


@app.post("/run-tests", dependencies=[Depends(require_api_key)])
def run_tests(request: RunTestsRequest):
    try:
        project = store.get_project(request.project_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    report = executor.run_project(project, request)
    store.save_report(report)
    reporter.export_json(report, PROJECT_ROOT / "reports")
    return report


@app.get("/results/{project_id}", dependencies=[Depends(require_api_key)])
def results(project_id: str):
    try:
        return store.get_report(project_id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/logs/{test_id}", dependencies=[Depends(require_api_key)])
def logs(test_id: str):
    return {"test_id": test_id, "logs": store.get_test_logs(test_id)}


@app.get("/reports/{project_id}/download", dependencies=[Depends(require_api_key)])
def download_report(project_id: str):
    report = store.get_report(project_id)
    path = PROJECT_ROOT / "reports" / f"{report.project_id}-{report.run_id}.json"
    if not path.exists():
        reporter.export_json(report, PROJECT_ROOT / "reports")
    return FileResponse(path, filename=f"{project_id}-report.json", media_type="application/json")
