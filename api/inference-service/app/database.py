import sqlite3
import json
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from app.config import settings

DB_PATH = settings.database_url.replace("sqlite:///", "")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL, -- 'analysis' or 'diagnosis'
            status TEXT NOT NULL, -- 'pending', 'completed', 'failed'
            result TEXT, -- JSON
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def create_task(task_type: str) -> str:
    task_id = f"{task_type}_{str(uuid.uuid4())}"
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (id, type, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (task_id, task_type, "pending", now, now)
        )
        conn.commit()
    return task_id

def update_task(task_id: str, status: str, result: dict | None = None):
    now = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        cur = conn.cursor()
        if result is not None:
            cur.execute(
                "UPDATE tasks SET status = ?, result = ?, updated_at = ? WHERE id = ?",
                (status, json.dumps(result, ensure_ascii=False), now, task_id)
            )
        else:
            cur.execute(
                "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, task_id)
            )
        conn.commit()

def get_task(task_id: str) -> dict | None:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        if row:
            return {
                "id": row[0],
                "type": row[1],
                "status": row[2],
                "result": json.loads(row[3]) if row[3] else None,
                "created_at": row[4],
                "updated_at": row[5]
            }
    return None
