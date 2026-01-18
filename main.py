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
from fastapi.responses import FileResponse
import pandas as pd
import json

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


# MXIK Codes CRUD Endpoints
EXCEL_FILE_PATH = "api/mxik-codes.xlsx"


@app.get("/mxik-codes-page", tags=["MXIK Management"])
async def mxik_codes_page(request: Request):
    """Render the MXIK management page."""
    return templates.TemplateResponse("mxik.html", {"request": request})


@app.get("/api/mxik-data", tags=["MXIK Management"])
async def get_mxik_data():
    """Fetch MXIK data from Excel file as JSON."""
    try:
        if not os.path.exists(EXCEL_FILE_PATH):
            raise HTTPException(status_code=404, detail="Excel file not found")

        df = pd.read_excel(EXCEL_FILE_PATH, dtype=str)
        # Ensure 'mxik code' and 'package code' columns exist
        if "mxik code" not in df.columns:
            df["mxik code"] = ""
        if "package code" not in df.columns:
            df["package code"] = ""

        # Use index as a unique ID for easier row identification
        df["row_id"] = df.index
        data = df.to_dict(orient="records")
        return data
    except Exception as e:
        logger.error(f"Error reading Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mxik-update", tags=["MXIK Management"])
async def update_mxik_data(request: Request):
    """Update rows in the MXIK Excel file."""
    try:
        body = await request.json()
        updates = body.get("updates", [])

        if not os.path.exists(EXCEL_FILE_PATH):
            raise HTTPException(status_code=404, detail="Excel file not found")

        df = pd.read_excel(EXCEL_FILE_PATH, dtype=str)

        for update in updates:
            row_id = int(update.get("row_id"))
            if 0 <= row_id < len(df):
                if "mxik_code" in update:
                    df.at[row_id, "mxik code"] = update["mxik_code"]
                if "package_code" in update:
                    df.at[row_id, "package code"] = update["package_code"]

        df.to_excel(EXCEL_FILE_PATH, index=False)
        return {"message": "Dinamik ravishda saqlandi"}
    except Exception as e:
        logger.error(f"Error updating Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/mxik-download", tags=["MXIK Management"])
async def download_mxik_excel():
    """Download the modified MXIK Excel file."""
    if not os.path.exists(EXCEL_FILE_PATH):
        raise HTTPException(status_code=404, detail="Excel file not found")

    return FileResponse(
        path=EXCEL_FILE_PATH,
        filename="mxik-codes-updated.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
