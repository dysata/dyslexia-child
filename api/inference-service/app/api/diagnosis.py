from fastapi.responses import JSONResponse
from fastapi import APIRouter, BackgroundTasks, HTTPException, Header, Query
from app.config import settings
from app.database import create_task, get_task
from app.tasks import run_diagnosis_task
from app.models import DiagnosticRequest, DiagnosticReport
import sys
import json
import subprocess
import os

router = APIRouter(prefix="/diagnostic-reports", tags=["diagnostic-reports"])

DIAGNOSTIC_SCRIPT_PATH = os.getenv("DIAGNOSTIC_SCRIPT_PATH")
PYTHON_PATH = os.getenv("DIAGNOSTIC_PYTHON_PATH")


def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@router.post("", responses={201: {}, 202: {}})
async def create_diagnostic_report(
    request: DiagnosticRequest,
    async_: bool = Query(False, alias="async"),
    background_tasks: BackgroundTasks = None,
    x_api_key: str = Header(...)
):
    verify_api_key(x_api_key)

    # Преобразуем все анализы в JSON-совместимый формат (строки вместо datetime)
    analyses_data = [analysis.model_dump(mode='json') for analysis in request.analyses]

    if async_:
        task_id = create_task("diagnosis")
        background_tasks.add_task(run_diagnosis_task, task_id, analyses_data)
        headers = {"Location": f"/v1/diagnostic-reports/{task_id}"}
#        return {"task_id": task_id, "status": "processing"}, 202, headers
        return JSONResponse(
            content={"task_id": task_id, "status": "processing"},
            status_code=201,
            headers={"Location": f"/v1/diagnostic-reports/{task_id}"}
        )    
    else:
        # Синхронный вызов
        # Check if file exists before calling to avoid confusing errors
        if not os.path.exists(DIAGNOSTIC_SCRIPT_PATH):
            raise FileNotFoundError(f"Model script not found at {MODEL_SCRIPT_PATH}. Is the volume mounted?")
                
        input_json = json.dumps({"analyses": analyses_data}, ensure_ascii=False)
        result = subprocess.run(
            [PYTHON_PATH, DIAGNOSTIC_SCRIPT_PATH],
            input=input_json,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            raise HTTPException(500, f"Diagnosis failed: {result.stderr}")
        try:
            report = json.loads(result.stdout)
            return report
        except json.JSONDecodeError:
            raise HTTPException(500, "Invalid JSON from diagnoser script")

@router.get("/{report_id}")
async def get_diagnostic_report(report_id: str, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    task = get_task(report_id)
    if not task:
        raise HTTPException(404, "Report not found")
    if task["status"] == "completed":
        return task["result"]
    elif task["status"] == "pending":
        return JSONResponse({"status": "processing"}, 202)
    else:
        raise HTTPException(500, "Report generation failed")
