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
    image_search_site: str = Form(""),
    additional_search: str = Form("false"),
):
    """
    Upload Excel file for bulk product generation.
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=400, detail="Faqat Excel fayllar qabul qilinadi (.xlsx, .xls)"
        )

    # Convert additional_search string to boolean
    additional_search_bool = additional_search.lower() == "true"

    # Start processing in background
    background_tasks.add_task(
        bulk_service.process_excel,
        file=file,
        email=email,
        password=password,
        image_search_site=image_search_site if image_search_site else None,
        additional_search=additional_search_bool,
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
    """Fetch MXIK data from Excel file as JSON without headers."""
    try:
        if not os.path.exists(EXCEL_FILE_PATH):
            raise HTTPException(status_code=404, detail="Excel file not found")

        # Read without header
        df = pd.read_excel(EXCEL_FILE_PATH, header=None, dtype=str)

        # Ensure we have at least 4 columns
        while len(df.columns) < 4:
            df[len(df.columns)] = ""

        # Map indices to names for the UI
        # Excel structure: Column 0 = ID, Column 1 = Name, Column 2 = mixk, Column 3 = package
        data = []
        for idx, row in df.iterrows():
            data.append(
                {
                    "row_id": idx,
                    "category_id": row[0] if 0 in row else "",
                    "name": row[1] if 1 in row else "",
                    "mxik_code": row[2] if 2 in row else "",
                    "package_code": row[3] if 3 in row else "",
                }
            )
        return data
    except Exception as e:
        logger.error(f"Error reading Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mxik-update", tags=["MXIK Management"])
async def update_mxik_data(request: Request):
    """Update rows in the MXIK Excel file without headers."""
    try:
        body = await request.json()
        updates = body.get("updates", [])

        if not os.path.exists(EXCEL_FILE_PATH):
            raise HTTPException(status_code=404, detail="Excel file not found")

        df = pd.read_excel(EXCEL_FILE_PATH, header=None, dtype=str)

        for update in updates:
            row_id_value = update.get("row_id")
            if row_id_value is None:
                continue
            try:
                row_id = int(row_id_value)
            except (ValueError, TypeError):
                continue
            if 0 <= row_id < len(df):
                if "category_id" in update:
                    df.iloc[row_id, 0] = str(update["category_id"])
                if "name" in update:
                    df.iloc[row_id, 1] = str(update["name"])
                if "mxik_code" in update:
                    df.iloc[row_id, 2] = str(update["mxik_code"])
                if "package_code" in update:
                    df.iloc[row_id, 3] = str(update["package_code"])

        df.to_excel(EXCEL_FILE_PATH, index=False, header=False)
        return {"message": "Dinamik ravishda saqlandi"}
    except Exception as e:
        logger.error(f"Error updating Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/mxik-add", tags=["MXIK Management"])
async def add_mxik_item(request: Request):
    """Add a new row to the MXIK Excel file without headers."""
    try:
        body = await request.json()
        item = body.get("item", {})

        if not os.path.exists(EXCEL_FILE_PATH):
            raise HTTPException(status_code=404, detail="Excel file not found")

        df = pd.read_excel(EXCEL_FILE_PATH, header=None, dtype=str)

        # Construct new row list, handling None values properly
        def safe_str(value):
            """Convert value to string, handling None values."""
            return str(value) if value is not None else ""
        
        new_row = [
            safe_str(item.get("category_id")),
            safe_str(item.get("name")),
            safe_str(item.get("mxik_code")),
            safe_str(item.get("package_code")),
        ]

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_excel(EXCEL_FILE_PATH, index=False, header=False)
        return {"message": "Yangi item muvaffaqiyatli qo'shildi"}
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error(f"Error adding to Excel: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/mxik-delete/{row_id}", tags=["MXIK Management"])
async def delete_mxik_item(row_id: int):
    """Delete a row from the MXIK Excel file without headers."""
    try:
        if not os.path.exists(EXCEL_FILE_PATH):
            raise HTTPException(status_code=404, detail="Excel file not found")

        df = pd.read_excel(EXCEL_FILE_PATH, header=None, dtype=str)

        if 0 <= row_id < len(df):
            df = df.drop(df.index[row_id])
            df.to_excel(EXCEL_FILE_PATH, index=False, header=False)
            return {"message": "Item muvaffaqiyatli o'chirildi"}
        else:
            raise HTTPException(status_code=404, detail="Row not found")
    except Exception as e:
        logger.error(f"Error deleting from Excel: {e}")
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
