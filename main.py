"""FastAPI application for AI Product Generator."""

import logging
import os
import random

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from agent.image import generate_poster
from api_models import ErrorResponse, ProductGenerateRequest, ProductGenerateResponse
from core.config import settings
from core.constants import CORS_ALLOW_ORIGINS
from services.product_service import ProductService
from utils.logging_config import setup_logging

from fastapi.templating import Jinja2Templates


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize service
product_service = ProductService()

from core.manager import ConnectionManager
from services.bulk_upload_service import BulkUploadService
from fastapi import (
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
)

manager = ConnectionManager()
bulk_service = BulkUploadService(manager)


# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="AI-powered product content generation API",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount media directories if they exist
if os.path.exists("media"):
    app.mount("/media", StaticFiles(directory="media"), name="media")
if os.path.exists("seo-images"):
    app.mount("/seo-images", StaticFiles(directory="seo-images"), name="seo-images")

# Templates
templates = Jinja2Templates(directory="static")


@app.get("/", tags=["Root"])
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/upload-excel", tags=["Bulk Upload"])
async def upload_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    email: str = Form(...),
    password: str = Form(...),
):
    """
    Upload Excel file for bulk product generation.
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Faqat Excel fayllar qabul qilinadi (.xlsx, .xls)"
        )

    # Start processing in background
    background_tasks.add_task(
        bulk_service.process_excel, file=file, email=email, password=password
    )

    return {
        "message": "Fayl qabul qilindi. Jarayon boshlandi.",
        "filename": file.filename,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
