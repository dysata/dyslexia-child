from fastapi.responses import JSONResponse
from fastapi import APIRouter, File, UploadFile, Query, BackgroundTasks, HTTPException, Header
from app.config import settings
from app.database import create_task, get_task
from app.tasks import run_analysis_task
from app.models import SpeechAnalysisResult
import tempfile
import os
import sys
import json
import subprocess
import uuid
from datetime import datetime, timezone
router = APIRouter(prefix="/speech-analyses", tags=["speech-analyses"])

MODEL_SCRIPT_PATH = os.getenv("MODEL_SCRIPT_PATH")
PYTHON_PATH = os.getenv("MODEL_PYTHON_PATH")

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@router.post("", responses={201: {}, 202: {}})
async def create_speech_analysis(
    text_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    async_: bool = Query(False, alias="async"),
    background_tasks: BackgroundTasks = None,
    x_api_key: str = Header(...)
):
    verify_api_key(x_api_key)

    # Сохраняем загруженные файлы во временные
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tf:
        tf.write(await text_file.read())
        text_path = tf.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as af:
        af.write(await audio_file.read())
        audio_path = af.name

    try:
        if async_:
            task_id = create_task("analysis")
            background_tasks.add_task(run_analysis_task, task_id, text_path, audio_path)
            headers = {"Location": f"/v1/speech-analyses/{task_id}"}
#            return {"task_id": task_id, "status": "processing"}, 202, header
            return JSONResponse(
                content={"task_id": task_id, "status": "processing"},
                status_code=201,
                headers={"Location": f"/v1/speech-analyses/{task_id}"}
            )
        else:
            # Синхронный вызов
            # Check if file exists before calling to avoid confusing errors
            if not os.path.exists(MODEL_SCRIPT_PATH):
                raise FileNotFoundError(f"Model script not found at {MODEL_SCRIPT_PATH}. Is the volume mounted?")
#            print(f'PYTHON_PATH = {PYTHON_PATH}, MODEL_SCRIPT_PATH = {MODEL_SCRIPT_PATH}')
            result = subprocess.run(
                [PYTHON_PATH, MODEL_SCRIPT_PATH, text_path, audio_path],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.dirname(MODEL_SCRIPT_PATH)
            )
            if result.returncode != 0:
                raise HTTPException(500, f"Analysis failed: {result.stderr}")

            output = json.loads(result.stdout)
            triples = output["triples"]

            # Возвращаем результат с created_at как строкой (JSON-совместимо)
            return SpeechAnalysisResult(
                id=f"analysis_{uuid.uuid4()}",
                created_at=datetime.now(timezone.utc).isoformat(),
                triples=triples
            )
    except Exception as e:
        print(f"Error in processing POST on speech analysis: {e}")
        update_task(task_id, "failed")

    finally:
        # Удаляем временные файлы в любом случае
        if not async_:
            if os.path.exists(text_path):
                os.unlink(text_path)
            if os.path.exists(audio_path):
                os.unlink(audio_path)

@router.get("/{analysis_id}")
async def get_speech_analysis(analysis_id: str, x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    task = get_task(analysis_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task["status"] == "completed":
        return task["result"]
    elif task["status"] == "pending":
        return JSONResponse({"status": "processing"}, 202)
    else:
        raise HTTPException(500, "Task failed")
