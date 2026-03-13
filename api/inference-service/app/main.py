from fastapi import FastAPI, Request
import logging
from fastapi.middleware.cors import CORSMiddleware
from app.api.speech import router as speech_router
from app.api.diagnosis import router as diagnosis_router
from app.api.markers import router as markers_router
from app.database import init_db
import os

from fastapi.staticfiles import StaticFiles

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.WARN)

logger = logging.getLogger(__name__)

if not os.path.exists("tasks.db"):
    init_db()

root_path = os.getenv("INFERENCE_ROOT_PATH", "")  # Default to empty string if not set
#root_path = ""
# === API v1 ===
api_v1 = FastAPI(
    title="Speech Dyslexia Screening API",
    description="RESTful API for dyslexia screening via speech analysis",
    version="1.0.0",
#    servers=[
#        {"url": "/v1", "description": "Local development (mounted at /v1)"}
#    ],
    openapi_url="/openapi.json",   # /v1/openapi.json
    docs_url="/docs",              # /v1/docs
    redoc_url="/redoc"             # /v1/redoc
#    root_path=root_path
)

api_v1.include_router(speech_router)
api_v1.include_router(diagnosis_router)
api_v1.include_router(markers_router)

# === Main app ===
app = FastAPI(
    title="Main Application",
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
    root_path=root_path
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_incoming_request(request: Request, call_next):
    logger.debug(f"Incoming Request: {request.method} {request.url}, root_path = {root_path}")
    logger.debug(f"DEBUG: Method={request.method}, Scope Path={request.scope.get('path')}, Root Path={request.scope.get('root_path')}")
    # Optional: Log headers (be careful with sensitive information)
    # logger.debug(f"Headers: {request.headers}")
    response = await call_next(request)
    logger.debug(f"Outgoing Response Status: {response.status_code}")
    return response

app.mount("/v1", api_v1)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

#@app.get("/app")
#def read_main(request: Request):
#    return {"message": "Hello World", "root_path": request.scope.get("root_path")}
