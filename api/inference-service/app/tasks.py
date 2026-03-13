import asyncio
import subprocess
import sys
import json
from datetime import datetime, timezone
from app.database import update_task, create_task
from app.config import settings
import os

MODEL_SCRIPT_PATH = os.getenv("MODEL_SCRIPT_PATH")
PYTHON_PATH = os.getenv("MODEL_PYTHON_PATH")
DIAGNOSTIC_SCRIPT_PATH = os.getenv("DIAGNOSTIC_SCRIPT_PATH")



async def run_analysis_task(task_id: str, text_path: str, audio_path: str):
    try:
        # Запуск внешнего скрипта

        # Check if file exists before calling to avoid confusing errors
        if not os.path.exists(MODEL_SCRIPT_PATH):
            raise FileNotFoundError(f"Model script not found at {MODEL_SCRIPT_PATH}. Is the volume mounted?")
        result = await asyncio.to_thread(
            subprocess.run,
            [PYTHON_PATH, MODEL_SCRIPT_PATH, text_path, audio_path],
            capture_output=True,
            text=True,
            timeout=240,
            cwd=os.path.dirname(MODEL_SCRIPT_PATH)
        )
        if result.returncode != 0:
            raise RuntimeError(f"Analyzer failed: {result.stderr}")

        output = json.loads(result.stdout)
        triples = output["triples"]

        final_result = {
            "id": task_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "triples": triples
        }

        if os.path.exists(text_path):
            os.unlink(text_path)
        if os.path.exists(audio_path):
            os.unlink(audio_path)
        
        update_task(task_id, "completed", final_result)        
    except Exception as e:
        print(f"Error in analysis task {task_id}: {e}")
        update_task(task_id, "failed")

async def run_diagnosis_task(task_id: str, analyses: list[dict]):
    try:       
        input_data = {"analyses": analyses}
        result = await asyncio.to_thread(
            subprocess.run,
            [PYTHON_PATH, DIAGNOSTIC_SCRIPT_PATH],
            input=json.dumps(input_data, ensure_ascii=False),
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            raise RuntimeError(f"Diagnoser failed: {result.stderr}")

        report = json.loads(result.stdout)
        update_task(task_id, "completed", report)
    except Exception as e:
        print(f"Error in diagnosis task {task_id}: {e}")
        update_task(task_id, "failed")
