# LOYIHA STRUKTURASI VA KODI

## 1. Papka Strukturasi
```text
6valley-product-agent/
    seller.py
    .env
    main.txt
    IMPROVEMENTS.md
    requirements.txt
    main.py
    README.md
    API's.txt
    test_rasm.png
    api_models.py
    test.py
    utils/
        logging_config.py
        __init__.py
    api/
        venu_api.py
        __init__.py
    services/
        product_service.py
        __init__.py
    agent/
        __init__.py
        image_search/
            image_downloader.py
            image_search_agent.py
            __init__.py
        image/
            image_agent.py
            __init__.py
        product/
            schemas.py
            agent.py
            __init__.py
        category_brand/
            schemas.py
            agent.py
            __init__.py
    core/
        config.py
        constants.py
        __init__.py
        openai_client.py
```

## 2. Fayllar Mazmuni

### Fayl: `seller.py`
```py
import requests
import json
import logging
import os
from typing import List, Dict, Any, Optional

# Logging - jarayonni terminalda ko'rish uchun
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class VenuSellerAPI:
    BASE_URL = "https://api.venu.uz"

    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.token: Optional[str] = None

        # Standart headerlar
        self.session.headers.update(
            {
                "user-agent": "Dart/3.10 (dart:io)",
                "accept-encoding": "gzip",
                "lang": "en",
            }
        )

    def login(self) -> bool:
        """1. Login qilish va Token olish"""
        url = f"{self.BASE_URL}/api/v3/seller/auth/login"
        payload = {"email": self.email, "password": self.password}

        # Login uchun hujjatdagi maxsus vaqtinchalik bearer token
        temp_headers = {
            "authorization": "Bearer mPzVh43jap7LOAy9bX8TwGdzj2eTxNOBq4DS3xhV7U4P8McxjC"
        }

        try:
            response = self.session.post(url, json=payload, headers=temp_headers)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("token")

            # Keyingi so'rovlar uchun asosiy tokenni o'rnatamiz
            self.session.headers.update({"authorization": f"Bearer {self.token}"})
            logging.info("Muvaffaqiyatli login qilindi.")
            return True
        except Exception as e:
            logging.error(f"Login xatosi: {e}")
            return False

    def upload_image(
        self, file_path: str, image_type: str = "product"
    ) -> Optional[str]:
        """
        2. Rasmni serverga yuklash (upload-images).
        Server qaytargan fayl nomini qaytaradi.
        """
        if not os.path.exists(file_path):
            logging.error(f"Fayl topilmadi: {file_path}")
            return None

        url = f"{self.BASE_URL}/api/v3/seller/products/upload-images"

        # Multipart so'rov uchun Content-Type'ni requests o'zi belgilaydi
        headers = {
            "authorization": f"Bearer {self.token}",
            "user-agent": "Dart/3.10 (dart:io)",
        }

        try:
            with open(file_path, "rb") as img_file:
                files = [
                    ("image", (os.path.basename(file_path), img_file, "image/png"))
                ]
                # API talab qiladigan qo'shimcha form-data maydonlari
                data = {
                    "type": image_type,  # 'thumbnail' yoki 'product'
                    "colors_active": "false",
                    "color": "",
                }

                response = requests.post(url, headers=headers, files=files, data=data)
                response.raise_for_status()
                res_data = response.json()

                # API muvaffaqiyatli yuklanganda fayl nomini qaytaradi
                # Logingizdan kelib chiqib: res_data['image_name'] bo'lishi kerak
                image_name = res_data.get("image_name")
                logging.info(f"Rasm serverga yuklandi: {image_name}")
                return image_name
        except Exception as e:
            logging.error(f"Rasm yuklashda xatolik: {e}")
            return None

    def add_product(
        self,
        name: str,
        description: str,
        meta_image: str,
        meta_title: str,
        meta_description: str,
        tags: List[str],
        price: float,
        category_id: str,
        brand_id: int,
        main_image_path: str,
        additional_images_paths: List[str] = [],
        stock: int = 10,
    ) -> Dict:
        """3. Mahsulotni barcha yuklangan rasmlar bilan birga qo'shish"""

        # A. Asosiy rasmni (Thumbnail) yuklash
        thumb_name = self.upload_image(main_image_path, "thumbnail")
        if not thumb_name:
            return {"error": "Thumbnail yuklanmadi"}

        # B. Galereya rasmlarini yuklash
        gallery_images = []
        # Birinchi bo'lib thumbnailni galereyaga qo'shamiz (API talabi bo'lishi mumkin)
        gallery_images.append({"image_name": thumb_name, "storage": "public"})

        for img_path in additional_images_paths:
            img_name = self.upload_image(img_path, "product")
            if img_name:
                gallery_images.append({"image_name": img_name, "storage": "public"})

        # C. Mahsulot ma'lumotlarini yig'ish (JSON string formatida bo'lishi shart!)
        # payload = {
        #     "name": json.dumps([name]),
        #     "description": json.dumps([description]),
        #     "unit_price": price,
        #     "discount": 0,
        #     "discount_type": "flat",
        #     "tax_ids": "[]",
        #     "tax": "0", # Majburiy maydon
        #     "tax_model": "exclude",
        #     "category_id": category_id,
        #     "sub_category_id": "600", # Kerak bo'lsa to'ldiriladi
        #     "sub_sub_category_id": "601",
        #     "unit": "pc",
        #     "brand_id": brand_id,
        #     "current_stock": stock,
        #     "minimum_order_qty": 1,
        #     "code": os.urandom(3).hex().upper(), # Avtomatik random kod
        #     "product_type": "physical",
        #     "thumbnail": thumb_name, # Serverdan qaytgan nom
        #     "images": json.dumps(gallery_images), # Yuklangan rasmlar massivi
        #     "meta_image": meta_image,
        #     "meta_title": meta_title,
        #     "meta_description": meta_description,
        #     "lang": json.dumps(["ru"]), # Til
        #     "colors_active": False,
        #     "shipping_cost": 0,
        #     "multiply_qty": 0,
        #     "tags": json.dumps(tags),
        #     "meta_max_image_preview_value": "large"
        # }

        print(json.dumps([name]))

        payload = {
            "name": json.dumps([name]),
            "description": json.dumps([description]),
            "unit_price": price,
            "discount": 0,
            "discount_type": "percent",
            "tax_ids": "[]",
            "tax_model": "exclude",
            "category_id": "424",
            "unit": "pc",
            "brand_id": 7,
            "meta_title": meta_title,
            "meta_description": "",
            "lang": json.dumps(["ru"]),
            "colors": "[]",
            "images": json.dumps(gallery_images),
            "thumbnail": thumb_name,
            "colors_active": False,
            "video_url": "",
            "meta_image": meta_image,
            "current_stock": stock,
            "shipping_cost": 0.0,
            "multiply_qty": 0,
            "code": os.urandom(3).hex().upper(),
            "minimum_order_qty": 1,
            "product_type": "physical",
            "digital_product_type": "ready_after_sell",
            "digital_file_ready": "",
            "tags": json.dumps(tags),
            "publishing_house": "[]",
            "authors": "[]",
            "color_image": "[]",
            "meta_index": "1",
            "meta_no_follow": "",
            "meta_no_image_index": "0",
            "meta_no_archive": "0",
            "meta_no_snippet": "0",
            "meta_max_snippet": "0",
            "meta_max_snippet_value": None,
            "meta_max_video_preview": "0",
            "meta_max_video_preview_value": None,
            "meta_max_image_preview": "0",
            "meta_max_image_preview_value": "large",
            "sub_category_id": "600",
            "sub_sub_category_id": "601",
            "tax": "0",
        }

        url = f"{self.BASE_URL}/api/v3/seller/products/add"
        try:
            # content-type: application/json orqali yuboramiz
            response = self.session.post(url, json=payload)
            result = response.json()
            if response.status_code == 200:
                logging.info(f"Mahsulot muvaffaqiyatli qo'shildi: {name}")
            else:
                logging.error(f"Xatolik: {result}")
            return result
        except Exception as e:
            logging.error(f"Mahsulot qo'shishda xatolik: {e}")
            return {"status": "error", "message": str(e)}


# ==================== ISHLATIB KO'RISH ====================

if __name__ == "__main__":
    # 1. API klasini yaratish
    api = VenuSellerAPI(email="themodestn@venu.uz", password="Themodestn@venu3001.uz")

    if api.login():
        # Kompyuteringizda bor bo'lgan rasm yo'lini ko'rsating
        # Masalan: "C:/rasmlar/iphone.png" yoki "image.jpg"
        image_path = "test_rasm.png"

        # Agar rasm fayli mavjud bo'lsa
        if os.path.exists(image_path):
            result = api.add_product(
                name="Smartfon iPhone 15 Pro",
                description="Eng yangi model, 256GB, Titan",
                meta_image="test_rasm.png",
                meta_title="Smartfon iPhone 15 Pro",
                meta_description="Eng yangi model, 256GB, Titan",
                tags=["new", "product"],
                price=1500,
                category_id="424",  # Smartfonlar ID si
                brand_id=2,  # Apple/Iphone ID si
                main_image_path=image_path,
                additional_images_paths=[image_path],  # Qo'shimcha rasmlar bo'lsa
                stock=5,
            )
            print("\nNatija:")
            print(json.dumps(result, indent=2))
        else:
            print(
                f"Xato: {image_path} fayli topilmadi! Iltimos kompyuteringizdagi rasm yo'lini bering."
            )


# Example usage (for testing)
if __name__ == "__main__":
    import sys

    # Setup logging
    from utils.logging_config import setup_logging

    setup_logging()

    # Get credentials from environment or use defaults
    email = os.getenv("VENU_EMAIL", "themodestn@venu.uz")
    password = os.getenv("VENU_PASSWORD", "Themodestn@venu3001.uz")

    api = VenuSellerAPI(email=email, password=password)

    if api.login():
        image_path = "test_rasm.png"

        if os.path.exists(image_path):
            result = api.add_product(
                name="Smartfon iPhone 15 Pro",
                description="Eng yangi model, 256GB, Titan",
                meta_image="test_rasm.png",
                meta_title="Smartfon iPhone 15 Pro",
                meta_description="Eng yangi model, 256GB, Titan",
                tags=["new", "product"],
                price=1500.0,
                category_id="424",
                brand_id=2,
                main_image_path=image_path,
                additional_images_paths=[image_path],
                stock=5,
            )
            print("\nResult:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {image_path} file not found!")
            sys.exit(1)
    else:
        print("Login failed!")
        sys.exit(1)

```

### Fayl: `main.txt`
```txt
Salom. Men AI agen yaratmoqchiman. AI agent menga maxsulotlarni ma'lumotlarini generate qilib berishi kerak!

Kiruvchi ma'lumot:
Maxsulot nomi, Brendi, Narxi,

Chiquvchi ma'lumotlar:
name=(Qayta ishlangan, foydalanuvchig ko'proq yoqadigan maxsulot nomi)
description=(Maxsulot nomi, brendi, narxidan kelib chiqib generate qilinadigan description)
main_image_path=(Maxsulot uchun chizilgan image)
additional_images_paths=(Internetda shu maxsulot uchun rasimlarni qidirib topish va ularni manzillarini joylash)
meta_image=(SEO uchun metta image main_image_path dan meros olishi mumkin!)
meta_title=(name)
meta_description=(SEO uchun meta description, nom, brend, narx lardan generation qilinadi)
tags=(taglar)
price=(narxi)
category_id=(Categoriyalar ularni olish uchun maxsus API lar bor)
brand_id=(Categoriyalar ularni olish uchun maxsus API lar bor)
stock=(Default 5ta)

Shu ma'lumotlarni generate qilib berish uchun qaysi yo'l bilan AI yaratish yaxshi, Rasim chizish, matn generate qilish, urlarni qidirib topish
```

### Fayl: `IMPROVEMENTS.md`
```md
# Code Improvements Summary

This document summarizes all the improvements made to the 6valley-product-agent project.

## 🎯 Code Quality Improvements

### 1. Fixed Code Issues
- ✅ Fixed syntax error in `main.py` (trailing comma in function call)
- ✅ Removed schema duplication (consolidated to `agent/product/schemas.py`)
- ✅ Added comprehensive type hints throughout the codebase
- ✅ Improved error handling with proper exception types
- ✅ Added structured logging with proper log levels

### 2. Configuration Management
- ✅ Created centralized configuration in `core/config.py`
- ✅ Used Pydantic Settings for type-safe configuration
- ✅ Environment variable validation
- ✅ Support for `.env` files

### 3. Code Organization
- ✅ Separated concerns into logical modules
- ✅ Created reusable utilities
- ✅ Improved code reusability and maintainability

## 📁 Folder Structure Improvements

### New Directory Structure

```
6valley-product-agent/
├── agent/                    # AI agents (existing, improved)
│   ├── product/
│   │   ├── agent.py         # Improved with better error handling
│   │   └── schemas.py       # Single source of truth for schemas
│   └── image/
│       └── image_agent.py   # Enhanced with better error handling
├── api/                      # NEW: External API integrations
│   └── venu_api.py         # Refactored from seller.py
├── core/                     # NEW: Core utilities
│   ├── config.py           # Configuration management
│   └── openai_client.py    # OpenAI client singleton
├── utils/                    # NEW: Utility functions
│   └── logging_config.py   # Logging configuration
├── api_models.py            # NEW: FastAPI request/response models
├── main.py                  # Improved with proper models and error handling
└── requirements.txt         # Updated with pydantic-settings
```

### Key Changes

1. **Created `api/` directory**: Moved `seller.py` → `api/venu_api.py` with improvements
2. **Created `core/` directory**: Centralized configuration and shared utilities
3. **Created `utils/` directory**: Reusable utility functions
4. **Better module organization**: Clear separation of concerns

## 🔧 Specific Improvements

### Agent Module (`agent/`)

#### Product Agent (`agent/product/agent.py`)
- ✅ Removed duplicate schema definitions
- ✅ Uses schemas from `schemas.py` (single source of truth)
- ✅ Added comprehensive logging
- ✅ Improved error messages
- ✅ Uses centralized configuration
- ✅ Better retry logic with logging

#### Image Agent (`agent/image/image_agent.py`)
- ✅ Enhanced with proper error handling
- ✅ Added logging
- ✅ Support for multiple DALL-E models
- ✅ Configurable image parameters
- ✅ Uses centralized OpenAI client

#### Schemas (`agent/product/schemas.py`)
- ✅ Improved documentation
- ✅ Better field descriptions
- ✅ Single source of truth (removed duplication)

### API Integration (`api/`)

#### Venu API Client (`api/venu_api.py`)
- ✅ Refactored from `seller.py` with improvements:
  - Better error handling with custom exceptions
  - Improved type hints
  - Comprehensive logging
  - Support for environment variables
  - Better MIME type detection
  - More flexible configuration
  - Removed hardcoded credentials

### Core Utilities (`core/`)

#### Configuration (`core/config.py`)
- ✅ Type-safe configuration using Pydantic Settings
- ✅ Environment variable support
- ✅ Default values for optional settings
- ✅ Validation on startup

#### OpenAI Client (`core/openai_client.py`)
- ✅ Singleton pattern for client reuse
- ✅ Centralized client management
- ✅ Uses configuration from settings

### Utilities (`utils/`)

#### Logging Configuration (`utils/logging_config.py`)
- ✅ Centralized logging setup
- ✅ Configurable log levels
- ✅ Consistent log format across the application

### FastAPI Application (`main.py`)

- ✅ Proper request/response models (`api_models.py`)
- ✅ Comprehensive error handling
- ✅ HTTP status codes
- ✅ CORS middleware
- ✅ Health check endpoints
- ✅ API documentation tags
- ✅ Structured logging
- ✅ Type-safe endpoints

### API Models (`api_models.py`)

- ✅ Pydantic models for request/response validation
- ✅ Proper field validation
- ✅ Error response models
- ✅ Type safety

## 📦 Dependencies

### Added
- `pydantic-settings==2.6.1` - For configuration management

### Existing (maintained)
- All existing dependencies preserved
- Version compatibility maintained

## 🚀 Benefits

1. **Maintainability**: Better code organization makes it easier to maintain
2. **Type Safety**: Comprehensive type hints catch errors early
3. **Error Handling**: Better error messages and handling
4. **Configuration**: Centralized, type-safe configuration
5. **Logging**: Structured logging for better debugging
6. **API Quality**: Professional FastAPI endpoints with proper models
7. **Code Reusability**: Modular design allows code reuse
8. **Testing**: Better structure makes testing easier

## 📝 Migration Notes

### For Existing Code

1. **Imports**: Update imports if needed:
   ```python
   # Old
   from seller import VenuSellerAPI
   
   # New
   from api import VenuSellerAPI
   ```

2. **Configuration**: Use environment variables instead of hardcoded values

3. **Schemas**: All schemas are now in `agent/product/schemas.py`

4. **Logging**: Logging is now centralized - use `logging.getLogger(__name__)`

### Old Files

- `seller.py` - Can be removed (functionality moved to `api/venu_api.py`)

## ✅ Testing Checklist

- [ ] Verify all imports work correctly
- [ ] Test product generation endpoint
- [ ] Test Venu API integration
- [ ] Verify configuration loading
- [ ] Check logging output
- [ ] Test error handling

## 🎉 Summary

The codebase has been significantly improved with:
- Better folder structure
- Improved code quality
- Better error handling
- Type safety
- Professional API design
- Comprehensive logging
- Centralized configuration

All improvements maintain backward compatibility where possible while significantly enhancing code quality and maintainability.


```

### Fayl: `requirements.txt`
```txt
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.12.1
certifi==2026.1.4
charset-normalizer==3.4.4
click==8.3.1
distro==1.9.0
fastapi==0.128.0
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.11
jiter==0.12.0
openai==2.15.0
pydantic==2.12.5
pydantic_core==2.41.5
pydantic-settings==2.6.1
python-dotenv==1.2.1
Pillow==10.0.0
requests==2.32.5
sniffio==1.3.1
starlette==0.50.0
tqdm==4.67.1
typing-inspection==0.4.2
typing_extensions==4.15.0
urllib3==2.6.3
uvicorn==0.40.0

```

### Fayl: `main.py`
```py
"""FastAPI application for AI Product Generator."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from api_models import ErrorResponse, ProductGenerateRequest, ProductGenerateResponse
from core.config import settings
from core.constants import CORS_ALLOW_ORIGINS
from services.product_service import ProductService
from utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize service
product_service = ProductService()


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


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "message": "AI Product Generator API",
        "version": settings.api_version,
        "status": "running",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post(
    "/generate-product",
    response_model=ProductGenerateResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Products"],
)
async def generate_product(request: ProductGenerateRequest) -> ProductGenerateResponse:
    """
    Generate product content (name, description, meta tags) using AI.

    Args:
        request: Product generation request

    Returns:
        ProductGenerateResponse: Generated product content

    Raises:
        HTTPException: If generation fails
    """
    try:
        logger.info(f"Generating product: {request.name} ({request.brand})")

        # Generate product text content
        product = product_service.generate_product_content(
            name=request.name,
            brand=request.brand,
            price=request.price,
            stock=request.stock,
        )

        # Search and download product images from internet
        downloaded_images = product_service.search_and_download_product_images(
            product_name=request.name,
            brand=request.brand,
            max_images=5,  # Maximum 5 additional images
            use_ai_generation_fallback=True,  # Fallback to AI if search fails
        )

        # Separate main image and additional images
        if downloaded_images:
            main_image_path = downloaded_images[0]
            additional_images_paths = downloaded_images[1:]  # Rest are additional
        else:
            # Fallback: use AI generation
            main_image_path, _ = product_service.generate_product_image(
                product_name=request.name, brand=request.brand
            )
            additional_images_paths = []

        # Select category and brand
        success, error_response, category_selection = (
            product_service.select_category_and_brand(
                product_name=request.name, brand_name=request.brand
            )
        )

        # Save to shop
        shop_saved = False
        shop_response = error_response

        if success and category_selection:
            shop_saved, shop_response = product_service.save_product_to_shop(
                product=product,
                category_selection=category_selection,
                main_image_path=main_image_path,
                additional_images_paths=additional_images_paths,
            )

        # Convert to response model
        response = ProductGenerateResponse.from_schema(
            product, shop_saved=shop_saved, shop_response=shop_response
        )
        logger.info(f"Successfully generated product: {request.name}")

        return response

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

```

### Fayl: `README.md`
```md
# 6Valley Product Agent

AI-powered product content generation system for e-commerce marketplaces. Generates bilingual (Russian + Uzbek) product descriptions, meta tags, and images using OpenAI.

## Features

- 🤖 **AI Product Text Generation**: Generates product names, descriptions, and meta tags in Russian and Uzbek
- 🖼️ **Image Generation**: Creates product images using DALL-E
- 🔌 **Venu API Integration**: Seamless integration with Venu marketplace API
- 🌐 **FastAPI REST API**: Modern, type-safe API with automatic documentation
- ⚙️ **Configuration Management**: Environment-based configuration
- 📝 **Comprehensive Logging**: Structured logging throughout the application

## Project Structure

```
6valley-product-agent/
├── agent/                    # AI agents
│   ├── product/              # Product text generation
│   │   ├── agent.py         # Main generation logic
│   │   └── schemas.py       # Pydantic schemas
│   └── image/               # Image generation
│       └── image_agent.py   # DALL-E integration
├── api/                      # External API integrations
│   └── venu_api.py         # Venu Seller API client
├── core/                     # Core utilities
│   ├── config.py           # Configuration management
│   └── openai_client.py    # OpenAI client singleton
├── utils/                    # Utility functions
│   └── logging_config.py   # Logging setup
├── api_models.py            # FastAPI request/response models
├── main.py                  # FastAPI application
└── requirements.txt         # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd 6valley-product-agent
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Configure your `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
VENU_EMAIL=your_venu_email@example.com
VENU_PASSWORD=your_venu_password
```

## Usage

### Running the API Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example API Request

```bash
curl -X POST "http://localhost:8000/generate-product" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15 Pro",
    "brand": "Apple",
    "price": 1500,
    "stock": 10
  }'
```

### Using the Venu API Client

```python
from api import VenuSellerAPI

api = VenuSellerAPI(email="your@email.com", password="password")
if api.login():
    result = api.add_product(
        name="Product Name",
        description="Product Description",
        # ... other parameters
    )
```

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options.

### Key Settings

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `OPENAI_MODEL`: Model to use (default: `gpt-4o-mini`)
- `OPENAI_TEMPERATURE`: Generation temperature (default: `0.3`)
- `VENU_BASE_URL`: Venu API base URL (default: `https://api.venu.uz`)

## Development

### Code Quality

The project follows Python best practices:
- Type hints throughout
- Pydantic for data validation
- Comprehensive error handling
- Structured logging
- Modular architecture

### Adding New Features

1. Add new agents in `agent/` directory
2. Add API integrations in `api/` directory
3. Update schemas in respective `schemas.py` files
4. Add new endpoints in `main.py`

## License

[Your License Here]

## Contributing

[Contributing Guidelines Here]


```

### Fayl: `API's.txt`
```txt
1. login qilish token olish uchun
Method: POST
URL
https://api.venu.uz/api/v3/seller/auth/login
Headers
accept-encoding:
gzip
authorization:
Bearer mPzVh43jap7LOAy9bX8TwGdzj2eTxNOBq4DS3xhV7U4P8McxjC
content-length:
66
content-type:
application/json; charset=UTF-8
host:
api.venu.uz
user-agent:
Dart/3.10 (dart:io)

Request body:{
  "email": "themodestn@venu.uz",
  "password": "Themodestn@venu3001.uz"
}

Response Success:{
  "token": "mk8l2eh6GM5yICFv1mCrheNfbC1H8QqOJAIt8IsKN8deGUilsa"
}

================ Tovar qo'shish uchun kerak bo'ladigan ma'lumotlar ===========================
Method: GET
URL
https://api.venu.uz/api/v1/attributes
Headers
accept-encoding:
gzip
authorization:
Bearer mk8l2eh6GM5yICFv1mCrheNfbC1H8QqOJAIt8IsKN8deGUilsa
content-type:
application/json; charset=UTF-8
host:
api.venu.uz
lang:
en
user-agent:
Dart/3.10 (dart:io)

Response Success:[
  {
    "id": 10,
    "name": "Операционная система",
    "created_at": "2025-09-15T10:52:19.000000Z",
    "updated_at": "2025-09-15T10:52:19.000000Z",
    "translations": []
  },
  {
    "id": 11,
    "name": "Оперативная память",
    "created_at": "2025-09-15T10:53:46.000000Z",
    "updated_at": "2025-09-15T10:53:46.000000Z",
    "translations": []
  },
  {
    "id": 12,
    "name": "Встроенная память",
    "created_at": "2025-09-15T10:54:01.000000Z",
    "updated_at": "2025-09-15T10:54:01.000000Z",
    "translations": []
  },
  {
    "id": 14,
    "name": "Тип дисплея",
    "created_at": "2025-09-15T10:54:20.000000Z",
    "updated_at": "2025-09-15T10:54:20.000000Z",
    "translations": []
  },
  {
    "id": 15,
    "name": "Размер дисплея",
    "created_at": "2025-09-15T10:54:29.000000Z",
    "updated_at": "2025-09-15T10:54:29.000000Z",
    "translations": []
  },
  {
    "id": 17,
    "name": "Основная камера",
    "created_at": "2025-09-15T10:54:52.000000Z",
    "updated_at": "2025-09-15T10:54:52.000000Z",
    "translations": []
  },
  {
    "id": 18,
    "name": "Фронтальная камера",
    "created_at": "2025-09-15T10:54:59.000000Z",
    "updated_at": "2025-09-15T10:54:59.000000Z",
    "translations": []
  },
  {
    "id": 19,
    "name": "Емкость аккумулятора",
    "created_at": "2025-09-15T10:55:05.000000Z",
    "updated_at": "2025-09-15T10:55:05.000000Z",
    "translations": []
  },
  {
    "id": 20,
    "name": "Быстрая зарядка",
    "created_at": "2025-09-15T10:55:13.000000Z",
    "updated_at": "2025-09-15T10:55:13.000000Z",
    "translations": []
  },
  {
    "id": 21,
    "name": "Беспроводная зарядка",
    "created_at": "2025-09-15T10:55:21.000000Z",
    "updated_at": "2025-09-15T10:55:21.000000Z",
    "translations": []
  },
  {
    "id": 22,
    "name": "Сети",
    "created_at": "2025-09-15T10:55:27.000000Z",
    "updated_at": "2025-09-15T10:55:27.000000Z",
    "translations": []
  },
  {
    "id": 23,
    "name": "Количество SIM-карт",
    "created_at": "2025-09-15T10:55:37.000000Z",
    "updated_at": "2025-09-15T10:55:37.000000Z",
    "translations": []
  },
  {
    "id": 24,
    "name": "Версия Bluetooth",
    "created_at": "2025-09-15T10:55:44.000000Z",
    "updated_at": "2025-09-15T10:55:44.000000Z",
    "translations": []
  },
  {
    "id": 25,
    "name": "Стандарты Wi-Fi",
    "created_at": "2025-09-15T10:55:52.000000Z",
    "updated_at": "2025-09-15T10:55:52.000000Z",
    "translations": []
  },
  {
    "id": 26,
    "name": "NFC",
    "created_at": "2025-09-15T10:55:57.000000Z",
    "updated_at": "2025-09-15T10:55:57.000000Z",
    "translations": []
  },
  {
    "id": 27,
    "name": "Защита от воды и пыли",
    "created_at": "2025-09-15T10:56:06.000000Z",
    "updated_at": "2025-09-15T10:56:06.000000Z",
    "translations": []
  },
  {
    "id": 28,
    "name": "Размеры",
    "created_at": "2025-09-15T10:56:12.000000Z",
    "updated_at": "2025-09-15T10:56:12.000000Z",
    "translations": []
  },
  {
    "id": 32,
    "name": "Сканер отпечатка пальца",
    "created_at": "2025-09-15T10:56:45.000000Z",
    "updated_at": "2025-09-15T10:56:45.000000Z",
    "translations": []
  },
  {
    "id": 34,
    "name": "Процессор",
    "created_at": "2025-09-15T10:57:19.000000Z",
    "updated_at": "2025-09-15T10:57:19.000000Z",
    "translations": []
  },
  {
    "id": 36,
    "name": "Тип накопителя",
    "created_at": "2025-09-15T10:57:39.000000Z",
    "updated_at": "2025-09-15T10:57:39.000000Z",
    "translations": []
  },
  {
    "id": 37,
    "name": "Разрешение дисплея",
    "created_at": "2025-09-15T10:58:31.000000Z",
    "updated_at": "2025-09-15T10:58:31.000000Z",
    "translations": []
  },
  {
    "id": 38,
    "name": "Частота обновления дисплея",
    "created_at": "2025-09-15T10:58:39.000000Z",
    "updated_at": "2025-09-15T10:58:39.000000Z",
    "translations": []
  },
  {
    "id": 39,
    "name": "Сенсорный экран",
    "created_at": "2025-09-15T10:58:46.000000Z",
    "updated_at": "2025-09-15T10:58:46.000000Z",
    "translations": []
  },
  {
    "id": 41,
    "name": "Веб-камера",
    "created_at": "2025-09-15T10:59:02.000000Z",
    "updated_at": "2025-09-15T10:59:02.000000Z",
    "translations": []
  },
  {
    "id": 42,
    "name": "Подсветка клавиатуры",
    "created_at": "2025-09-15T10:59:16.000000Z",
    "updated_at": "2025-09-15T10:59:16.000000Z",
    "translations": []
  },
  {
    "id": 43,
    "name": "Время автономной работы",
    "created_at": "2025-09-15T10:59:23.000000Z",
    "updated_at": "2025-09-15T10:59:23.000000Z",
    "translations": []
  },
  {
    "id": 45,
    "name": "Цвет",
    "created_at": "2025-09-15T10:59:38.000000Z",
    "updated_at": "2025-09-15T10:59:38.000000Z",
    "translations": []
  },
  {
    "id": 46,
    "name": "Материал корпуса",
    "created_at": "2025-09-15T10:59:51.000000Z",
    "updated_at": "2025-09-15T10:59:51.000000Z",
    "translations": []
  },
  {
    "id": 47,
    "name": "Диагональ экрана",
    "created_at": "2025-09-15T11:28:27.000000Z",
    "updated_at": "2025-09-15T11:28:27.000000Z",
    "translations": []
  },
  {
    "id": 48,
    "name": "Разрешение экрана",
    "created_at": "2025-09-15T11:28:35.000000Z",
    "updated_at": "2025-09-15T11:28:35.000000Z",
    "translations": []
  },
  {
    "id": 49,
    "name": "Smart TV",
    "created_at": "2025-09-15T11:28:44.000000Z",
    "updated_at": "2025-09-15T11:28:44.000000Z",
    "translations": []
  },
  {
    "id": 50,
    "name": "Поддержка HDR",
    "created_at": "2025-09-15T11:28:52.000000Z",
    "updated_at": "2025-09-15T11:28:52.000000Z",
    "translations": []
  },
  {
    "id": 51,
    "name": "Порты",
    "created_at": "2025-09-15T11:29:11.000000Z",
    "updated_at": "2025-09-15T11:29:11.000000Z",
    "translations": []
  },
  {
    "id": 52,
    "name": "Bluetooth",
    "created_at": "2025-09-15T11:29:21.000000Z",
    "updated_at": "2025-09-15T11:29:21.000000Z",
    "translations": []
  },
  {
    "id": 53,
    "name": "Мощность звука",
    "created_at": "2025-09-15T11:29:34.000000Z",
    "updated_at": "2025-09-15T11:29:34.000000Z",
    "translations": []
  },
  {
    "id": 54,
    "name": "Габариты",
    "created_at": "2025-09-15T11:29:42.000000Z",
    "updated_at": "2025-09-15T11:29:42.000000Z",
    "translations": []
  },
  {
    "id": 55,
    "name": "Вес",
    "created_at": "2025-09-15T11:29:48.000000Z",
    "updated_at": "2025-09-15T11:29:48.000000Z",
    "translations": []
  },
  {
    "id": 56,
    "name": "Класс энергоэффективности",
    "created_at": "2025-09-15T12:19:26.000000Z",
    "updated_at": "2025-09-15T12:19:26.000000Z",
    "translations": []
  },
  {
    "id": 57,
    "name": "Объем/Загрузка",
    "created_at": "2025-09-15T12:19:37.000000Z",
    "updated_at": "2025-09-15T12:19:37.000000Z",
    "translations": []
  },
  {
    "id": 60,
    "name": "Потребление энергии",
    "created_at": "2025-09-15T12:20:57.000000Z",
    "updated_at": "2025-09-15T12:20:57.000000Z",
    "translations": []
  },
  {
    "id": 61,
    "name": "Уровень шума",
    "created_at": "2025-09-15T12:21:12.000000Z",
    "updated_at": "2025-09-15T12:21:12.000000Z",
    "translations": []
  },
  {
    "id": 62,
    "name": "Для холодильников",
    "created_at": "2025-09-15T12:21:22.000000Z",
    "updated_at": "2025-09-15T12:21:22.000000Z",
    "translations": []
  },
  {
    "id": 63,
    "name": "Для стиральных машин",
    "created_at": "2025-09-15T12:21:30.000000Z",
    "updated_at": "2025-09-15T12:21:30.000000Z",
    "translations": []
  },
  {
    "id": 64,
    "name": "Для плит",
    "created_at": "2025-09-15T12:21:38.000000Z",
    "updated_at": "2025-09-15T12:21:38.000000Z",
    "translations": []
  },
  {
    "id": 68,
    "name": "Стиль",
    "created_at": "2025-09-15T12:22:21.000000Z",
    "updated_at": "2025-09-15T12:22:21.000000Z",
    "translations": []
  },
  {
    "id": 69,
    "name": "Сборка",
    "created_at": "2025-09-15T12:22:28.000000Z",
    "updated_at": "2025-09-15T12:22:28.000000Z",
    "translations": []
  },
  {
    "id": 70,
    "name": "Дополнительные функции",
    "created_at": "2025-09-15T12:22:35.000000Z",
    "updated_at": "2025-09-15T12:22:35.000000Z",
    "translations": []
  },
  {
    "id": 71,
    "name": "Тип продукта",
    "created_at": "2025-09-15T12:22:52.000000Z",
    "updated_at": "2025-09-15T12:22:52.000000Z",
    "translations": []
  },
  {
    "id": 72,
    "name": "Материал",
    "created_at": "2025-09-15T12:22:57.000000Z",
    "updated_at": "2025-09-15T12:22:57.000000Z",
    "translations": []
  },
  {
    "id": 73,
    "name": "Объем/Диаметр",
    "created_at": "2025-09-15T12:23:04.000000Z",
    "updated_at": "2025-09-15T12:23:04.000000Z",
    "translations": []
  },
  {
    "id": 74,
    "name": "Комплект",
    "created_at": "2025-09-15T12:23:19.000000Z",
    "updated_at": "2025-09-15T12:23:19.000000Z",
    "translations": []
  },
  {
    "id": 75,
    "name": "Покрытие",
    "created_at": "2025-09-15T12:23:25.000000Z",
    "updated_at": "2025-09-15T12:23:25.000000Z",
    "translations": []
  },
  {
    "id": 76,
    "name": "Для индукционных плит",
    "created_at": "2025-09-15T12:23:35.000000Z",
    "updated_at": "2025-09-15T12:23:35.000000Z",
    "translations": []
  }
]


Categoriyalar
Method: GET
URL
https://api.venu.uz/api/v3/seller/categories
Headers
accept-encoding:
gzip
authorization:
Bearer mk8l2eh6GM5yICFv1mCrheNfbC1H8QqOJAIt8IsKN8deGUilsa
content-type:
application/json; charset=UTF-8
host:
api.venu.uz
lang:
en
user-agent:
Dart/3.10 (dart:io)

Response Success:
[
  {
    "id": 592,
    "name": "Мебель",
    "slug": "mebel",
    "icon": "2025-11-07-690db05c1169c.webp",
    "icon_storage_type": "public",
    "parent_id": 0,
    "position": 0,
    "created_at": "2025-11-07T08:39:56.000000Z",
    "updated_at": "2025-11-07T08:39:56.000000Z",
    "home_status": 1,
    "priority": null,
    "icon_full_url": {
      "key": "2025-11-07-690db05c1169c.webp",
      "path": "https://api.venu.uz/storage/category/2025-11-07-690db05c1169c.webp",
      "status": 200
    },
    "childes": [
      {
        "id": 593,
        "name": "Офисное кресло",
        "slug": "ofisnoe-kreslo",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 592,
        "position": 1,
        "created_at": "2025-11-11T06:12:28.000000Z",
        "updated_at": "2025-11-11T06:12:28.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 24,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 594,
            "name": "Кресло",
            "slug": "kreslo",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 593,
            "position": 2,
            "created_at": "2025-11-11T06:13:21.000000Z",
            "updated_at": "2025-11-11T06:13:21.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 19,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 596,
        "name": "Игравое кресло",
        "slug": "igravoe-kreslo",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 592,
        "position": 1,
        "created_at": "2025-11-13T07:27:28.000000Z",
        "updated_at": "2025-11-13T07:27:28.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 7,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 597,
            "name": "Кпесло",
            "slug": "kpeslo",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 596,
            "position": 2,
            "created_at": "2025-11-13T07:28:04.000000Z",
            "updated_at": "2025-11-13T07:28:04.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 7,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      }
    ],
    "translations": []
  },
  {
    "id": 422,
    "name": "Smartfonlar va gadjetlar",
    "slug": "smartfonlar-va-gadjetlar",
    "icon": "2025-08-19-68a4265f70026.webp",
    "icon_storage_type": "public",
    "parent_id": 0,
    "position": 0,
    "created_at": "2025-08-08T12:29:18.000000Z",
    "updated_at": "2025-09-29T05:57:30.000000Z",
    "home_status": 1,
    "priority": 0,
    "icon_full_url": {
      "key": "2025-08-19-68a4265f70026.webp",
      "path": "https://api.venu.uz/storage/category/2025-08-19-68a4265f70026.webp",
      "status": 200
    },
    "childes": [
      {
        "id": 574,
        "name": "Часы",
        "slug": "casy",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 422,
        "position": 1,
        "created_at": "2025-10-05T14:42:49.000000Z",
        "updated_at": "2025-10-05T14:42:49.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 0,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 575,
            "name": "Смарт-часы",
            "slug": "smart-casy",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 574,
            "position": 2,
            "created_at": "2025-10-05T14:43:10.000000Z",
            "updated_at": "2025-10-05T14:43:10.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 466,
        "name": "Смартфоны, мобильные телефоны",
        "slug": "smartfony-mobilnye-telefony",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 422,
        "position": 1,
        "created_at": "2025-08-28T10:49:16.000000Z",
        "updated_at": "2025-08-28T10:49:16.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 216,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 467,
            "name": "Смартфоны",
            "slug": "smartfony",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 466,
            "position": 2,
            "created_at": "2025-08-28T10:49:52.000000Z",
            "updated_at": "2025-08-28T10:49:52.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 215,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 509,
        "name": "Планшеты",
        "slug": "plansety",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 422,
        "position": 1,
        "created_at": "2025-09-16T06:54:04.000000Z",
        "updated_at": "2025-09-16T06:54:04.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 10,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 510,
            "name": "Планшеты Samsung",
            "slug": "plansety-samsung",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 509,
            "position": 2,
            "created_at": "2025-09-16T06:55:17.000000Z",
            "updated_at": "2025-09-16T06:55:17.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 3,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      }
    ],
    "translations": []
  },
  {
    "id": 423,
    "name": "Noutbuklar va kompyuterlar",
    "slug": "noutbuklar-va-kompyuterlar",
    "icon": "2025-08-19-68a42694a3ec6.webp",
    "icon_storage_type": "public",
    "parent_id": 0,
    "position": 0,
    "created_at": "2025-08-08T12:31:29.000000Z",
    "updated_at": "2025-09-12T05:41:26.000000Z",
    "home_status": 1,
    "priority": 0,
    "icon_full_url": {
      "key": "2025-08-19-68a42694a3ec6.webp",
      "path": "https://api.venu.uz/storage/category/2025-08-19-68a42694a3ec6.webp",
      "status": 200
    },
    "childes": [
      {
        "id": 528,
        "name": "Компьютерные комплектующие",
        "slug": "kompiuternye-komplektuiushhie",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 423,
        "position": 1,
        "created_at": "2025-09-19T06:21:15.000000Z",
        "updated_at": "2025-09-19T06:21:15.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 1360,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 529,
            "name": "Блоки питания",
            "slug": "bloki-pitaniia",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-09-19T06:21:38.000000Z",
            "updated_at": "2025-09-19T06:21:38.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 194,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 557,
            "name": "Жесткие диски",
            "slug": "zestkie-diski",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-10-03T10:26:41.000000Z",
            "updated_at": "2025-10-03T10:26:41.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 133,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 559,
            "name": "Компьютерные корпусы",
            "slug": "kompiuternye-korpusy",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-10-03T10:41:06.000000Z",
            "updated_at": "2025-10-03T10:41:06.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 340,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 560,
            "name": "Оперативная память",
            "slug": "operativnaia-pamiat",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-10-03T11:34:03.000000Z",
            "updated_at": "2025-10-03T11:34:03.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 148,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 566,
            "name": "Видеокарты",
            "slug": "videokarty",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-10-03T12:32:22.000000Z",
            "updated_at": "2025-10-03T12:32:22.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 160,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 567,
            "name": "SSD / HDD диск",
            "slug": "ssd-hdd-disk",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-10-03T13:23:35.000000Z",
            "updated_at": "2025-10-03T13:23:35.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 13,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 576,
            "name": "Процессоры",
            "slug": "processory",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-10-06T02:06:27.000000Z",
            "updated_at": "2025-10-06T02:06:27.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 116,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 578,
            "name": "Кулер для процессора",
            "slug": "kuler-dlia-processora",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-10-06T05:57:18.000000Z",
            "updated_at": "2025-10-06T05:57:18.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 115,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 587,
            "name": "Сетевая карта",
            "slug": "setevaia-karta",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-10-26T02:40:48.000000Z",
            "updated_at": "2025-10-26T02:40:48.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 11,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 588,
            "name": "Контроллер",
            "slug": "kontroller",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-10-26T02:42:16.000000Z",
            "updated_at": "2025-10-26T02:42:16.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 5,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 589,
            "name": "Оптические приводы",
            "slug": "opticeskie-privody",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-10-28T09:01:39.000000Z",
            "updated_at": "2025-10-28T09:01:39.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 2,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 604,
            "name": "Сенсорная панел для MAC",
            "slug": "sensornaia-panel-dlia-mac",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-11-18T08:05:04.000000Z",
            "updated_at": "2025-11-18T08:05:04.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 1,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 605,
            "name": "Подставки для ноутбука",
            "slug": "podstavki-dlia-noutbuka",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-11-19T01:03:09.000000Z",
            "updated_at": "2025-11-19T01:03:09.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 15,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 608,
            "name": "серверы",
            "slug": "servery",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 528,
            "position": 2,
            "created_at": "2025-12-18T12:53:32.000000Z",
            "updated_at": "2025-12-18T12:53:32.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 430,
        "name": "Ноутбуки",
        "slug": "noutbuki",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 423,
        "position": 1,
        "created_at": "2025-08-11T05:15:43.000000Z",
        "updated_at": "2025-08-11T05:15:43.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 251,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 435,
            "name": "Ноутбуки MSI",
            "slug": "noutbuki-msi",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 430,
            "position": 2,
            "created_at": "2025-08-11T07:07:52.000000Z",
            "updated_at": "2025-08-11T07:07:52.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 12,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 436,
            "name": "Ноутбуки HP",
            "slug": "noutbuki-hp",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 430,
            "position": 2,
            "created_at": "2025-08-11T07:08:33.000000Z",
            "updated_at": "2025-08-11T07:08:33.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 94,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 439,
            "name": "Ноутбуки ASUS",
            "slug": "noutbuki-asus",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 430,
            "position": 2,
            "created_at": "2025-08-11T07:09:35.000000Z",
            "updated_at": "2025-08-11T07:09:35.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 63,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 441,
            "name": "Ноутбуки DELL",
            "slug": "noutbuki-dell",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 430,
            "position": 2,
            "created_at": "2025-08-11T09:20:14.000000Z",
            "updated_at": "2025-08-11T09:20:14.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 5,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 442,
            "name": "Ноутбуки GIGABYTE",
            "slug": "noutbuki-gigabyte",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 430,
            "position": 2,
            "created_at": "2025-08-13T05:17:47.000000Z",
            "updated_at": "2025-08-13T05:17:47.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 4,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 437,
            "name": "Ноутбуки acer",
            "slug": "noutbuki-acer",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 430,
            "position": 2,
            "created_at": "2025-08-11T07:08:53.000000Z",
            "updated_at": "2025-08-11T08:19:27.000000Z",
            "home_status": 1,
            "priority": 0,
            "sub_sub_category_product_count": 30,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 438,
            "name": "Ноутбуки lenovo",
            "slug": "noutbuki-lenovo",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 430,
            "position": 2,
            "created_at": "2025-08-11T07:09:16.000000Z",
            "updated_at": "2025-08-11T08:20:44.000000Z",
            "home_status": 1,
            "priority": 0,
            "sub_sub_category_product_count": 43,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 431,
        "name": "Компьютеры и мониторы",
        "slug": "kompiutery-i-monitory",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 423,
        "position": 1,
        "created_at": "2025-08-11T05:16:18.000000Z",
        "updated_at": "2025-08-11T05:16:18.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 565,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 537,
            "name": "Моноблок",
            "slug": "monoblok",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 431,
            "position": 2,
            "created_at": "2025-09-24T13:15:19.000000Z",
            "updated_at": "2025-09-24T13:15:19.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 118,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 440,
            "name": "Мониторы",
            "slug": "monitory",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 431,
            "position": 2,
            "created_at": "2025-08-11T07:11:17.000000Z",
            "updated_at": "2025-08-11T07:11:17.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 345,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 443,
            "name": "Моноблок HP",
            "slug": "monoblok-hp",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 431,
            "position": 2,
            "created_at": "2025-08-13T08:09:04.000000Z",
            "updated_at": "2025-08-13T08:09:04.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 72,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 444,
            "name": "Моноблок Lenovo",
            "slug": "monoblok-lenovo",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 431,
            "position": 2,
            "created_at": "2025-08-13T08:09:53.000000Z",
            "updated_at": "2025-08-13T08:09:53.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 24,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 445,
            "name": "Моноблок acer",
            "slug": "monoblok-acer",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 431,
            "position": 2,
            "created_at": "2025-08-13T12:30:23.000000Z",
            "updated_at": "2025-08-13T12:30:23.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 2,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 446,
            "name": "Моноблок ASUS",
            "slug": "monoblok-asus",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 431,
            "position": 2,
            "created_at": "2025-08-13T12:30:51.000000Z",
            "updated_at": "2025-08-13T12:30:51.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 1,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 448,
            "name": "Моноблок Hanson",
            "slug": "monoblok-hanson",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 431,
            "position": 2,
            "created_at": "2025-08-21T05:02:32.000000Z",
            "updated_at": "2025-08-21T05:02:32.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 2,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 434,
        "name": "Игровые аксессуары",
        "slug": "igrovye-aksessuary",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 423,
        "position": 1,
        "created_at": "2025-08-11T05:19:17.000000Z",
        "updated_at": "2025-08-11T05:19:17.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 16,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 577,
            "name": "Игравой корпус",
            "slug": "igravoi-korpus",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 434,
            "position": 2,
            "created_at": "2025-10-06T02:21:12.000000Z",
            "updated_at": "2025-10-06T02:21:12.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 6,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 507,
        "name": "Периферийные устройства",
        "slug": "periferiinye-ustroistva",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 423,
        "position": 1,
        "created_at": "2025-09-16T06:49:39.000000Z",
        "updated_at": "2025-09-16T06:49:39.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 128,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 586,
            "name": "Термопринтер",
            "slug": "termoprinter",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 507,
            "position": 2,
            "created_at": "2025-10-23T06:27:20.000000Z",
            "updated_at": "2025-10-23T06:27:20.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 11,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 508,
            "name": "Принтеры",
            "slug": "printery",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 507,
            "position": 2,
            "created_at": "2025-09-16T06:51:01.000000Z",
            "updated_at": "2025-09-16T06:51:01.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 118,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      }
    ],
    "translations": []
  },
  {
    "id": 424,
    "name": "Televizorlar va raqamli TV",
    "slug": "televizorlar-va-raqamli-tv",
    "icon": "2025-08-19-68a426aded35f.webp",
    "icon_storage_type": "public",
    "parent_id": 0,
    "position": 0,
    "created_at": "2025-08-08T12:32:42.000000Z",
    "updated_at": "2025-09-12T05:41:02.000000Z",
    "home_status": 1,
    "priority": 0,
    "icon_full_url": {
      "key": "2025-08-19-68a426aded35f.webp",
      "path": "https://api.venu.uz/storage/category/2025-08-19-68a426aded35f.webp",
      "status": 200
    },
    "childes": [
      {
        "id": 516,
        "name": "Проекторы и экраны",
        "slug": "proektory-i-ekrany",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 424,
        "position": 1,
        "created_at": "2025-09-17T10:36:37.000000Z",
        "updated_at": "2025-09-17T10:36:37.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 70,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 517,
            "name": "Экраны для видеопроекторов",
            "slug": "ekrany-dlia-videoproektorov",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 516,
            "position": 2,
            "created_at": "2025-09-17T10:37:13.000000Z",
            "updated_at": "2025-09-17T10:37:13.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 58,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 600,
        "name": "USB HUB",
        "slug": "usb-hub",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 424,
        "position": 1,
        "created_at": "2025-11-14T06:24:39.000000Z",
        "updated_at": "2025-11-14T06:24:39.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 50,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 601,
            "name": "USB-концетратор",
            "slug": "usb-koncetrator",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 600,
            "position": 2,
            "created_at": "2025-11-14T06:25:36.000000Z",
            "updated_at": "2025-11-14T06:25:36.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 50,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 468,
        "name": "Телевизоры и цифровое ТВ",
        "slug": "televizory-i-cifrovoe-tv",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 424,
        "position": 1,
        "created_at": "2025-08-28T11:29:17.000000Z",
        "updated_at": "2025-08-28T11:29:17.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 196,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 583,
            "name": "Интерактивная сенсорная панель",
            "slug": "interaktivnaia-sensornaia-panel",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 468,
            "position": 2,
            "created_at": "2025-10-20T10:04:21.000000Z",
            "updated_at": "2025-10-20T10:04:21.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 52,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 469,
            "name": "Смарт-телевизоры",
            "slug": "smart-televizory",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 468,
            "position": 2,
            "created_at": "2025-08-28T11:29:55.000000Z",
            "updated_at": "2025-08-28T11:29:55.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 132,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      }
    ],
    "translations": []
  },
  {
    "id": 425,
    "name": "Audiotexnika",
    "slug": "audiotexnika",
    "icon": "2025-08-19-68a426cbeafec.webp",
    "icon_storage_type": "public",
    "parent_id": 0,
    "position": 0,
    "created_at": "2025-08-08T12:32:57.000000Z",
    "updated_at": "2025-09-12T05:40:45.000000Z",
    "home_status": 1,
    "priority": 0,
    "icon_full_url": {
      "key": "2025-08-19-68a426cbeafec.webp",
      "path": "https://api.venu.uz/storage/category/2025-08-19-68a426cbeafec.webp",
      "status": 200
    },
    "childes": [
      {
        "id": 602,
        "name": "Флешки",
        "slug": "fleski",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 425,
        "position": 1,
        "created_at": "2025-11-18T07:47:59.000000Z",
        "updated_at": "2025-11-18T07:47:59.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 121,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 603,
            "name": "Флешка",
            "slug": "fleska",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 602,
            "position": 2,
            "created_at": "2025-11-18T07:48:40.000000Z",
            "updated_at": "2025-11-18T07:48:40.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 121,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 486,
        "name": "Все наушники",
        "slug": "vse-nausniki",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 425,
        "position": 1,
        "created_at": "2025-09-08T05:23:07.000000Z",
        "updated_at": "2025-09-08T05:23:07.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 202,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 502,
            "name": "наушники",
            "slug": "nausniki",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 486,
            "position": 2,
            "created_at": "2025-09-08T05:37:06.000000Z",
            "updated_at": "2025-10-05T03:18:16.000000Z",
            "home_status": 1,
            "priority": 0,
            "sub_sub_category_product_count": 203,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 470,
        "name": "Портативное аудио",
        "slug": "portativnoe-audio",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 425,
        "position": 1,
        "created_at": "2025-08-28T11:32:20.000000Z",
        "updated_at": "2025-08-28T11:32:48.000000Z",
        "home_status": 1,
        "priority": 0,
        "sub_category_product_count": 34,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 581,
            "name": "Гарнитура",
            "slug": "garnitura",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 470,
            "position": 2,
            "created_at": "2025-10-10T11:36:32.000000Z",
            "updated_at": "2025-10-10T11:36:32.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 1,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 582,
            "name": "Колонка",
            "slug": "kolonka",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 470,
            "position": 2,
            "created_at": "2025-10-10T11:37:06.000000Z",
            "updated_at": "2025-10-10T11:37:06.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 5,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 471,
            "name": "Портативные колонки",
            "slug": "portativnye-kolonki",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 470,
            "position": 2,
            "created_at": "2025-08-28T11:33:11.000000Z",
            "updated_at": "2025-08-28T11:33:11.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 5,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 501,
            "name": "Портативные колонки",
            "slug": "portativnye-kolonki",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 470,
            "position": 2,
            "created_at": "2025-09-08T05:35:20.000000Z",
            "updated_at": "2025-09-08T05:35:20.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 23,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      }
    ],
    "translations": []
  },
  {
    "id": 427,
    "name": "Uy uchun texnika",
    "slug": "uy-uchun-texnika",
    "icon": "2025-08-19-68a426fda8453.webp",
    "icon_storage_type": "public",
    "parent_id": 0,
    "position": 0,
    "created_at": "2025-08-08T12:33:26.000000Z",
    "updated_at": "2025-09-12T05:39:53.000000Z",
    "home_status": 1,
    "priority": 0,
    "icon_full_url": {
      "key": "2025-08-19-68a426fda8453.webp",
      "path": "https://api.venu.uz/storage/category/2025-08-19-68a426fda8453.webp",
      "status": 200
    },
    "childes": [
      {
        "id": 512,
        "name": "Холодельник",
        "slug": "xolodelnik",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-09-17T10:26:57.000000Z",
        "updated_at": "2025-09-17T10:26:57.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 111,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 533,
            "name": "Морозильник",
            "slug": "morozilnik",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 512,
            "position": 2,
            "created_at": "2025-09-19T10:08:26.000000Z",
            "updated_at": "2025-09-19T10:08:26.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 10,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 513,
        "name": "Куллеры",
        "slug": "kullery",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-09-17T10:27:45.000000Z",
        "updated_at": "2025-09-17T10:27:45.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 16,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [],
        "translations": []
      },
      {
        "id": 584,
        "name": "Пожарный извещатель",
        "slug": "pozarnyi-izveshhatel",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-10-21T06:03:25.000000Z",
        "updated_at": "2025-10-21T06:03:25.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 36,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [],
        "translations": []
      },
      {
        "id": 474,
        "name": "Стиральные и сушильные машины",
        "slug": "stiralnye-i-susilnye-masiny",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-08-28T11:36:09.000000Z",
        "updated_at": "2025-08-28T11:36:09.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 205,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 475,
            "name": "Стиральные машины",
            "slug": "stiralnye-masiny",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 474,
            "position": 2,
            "created_at": "2025-08-28T11:36:36.000000Z",
            "updated_at": "2025-08-28T11:36:36.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 135,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 491,
            "name": "Стиральные машины",
            "slug": "stiralnye-masiny",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 474,
            "position": 2,
            "created_at": "2025-09-08T05:30:05.000000Z",
            "updated_at": "2025-09-08T05:30:05.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 481,
        "name": "Крупная кухонная техника",
        "slug": "krupnaia-kuxonnaia-texnika",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-09-08T05:03:42.000000Z",
        "updated_at": "2025-09-08T05:03:42.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 467,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 542,
            "name": "Вытяжки",
            "slug": "vytiazki",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 481,
            "position": 2,
            "created_at": "2025-09-29T06:00:08.000000Z",
            "updated_at": "2025-09-29T06:00:08.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 28,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 544,
            "name": "Посудомоечные машины",
            "slug": "posudomoecnye-masiny",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 481,
            "position": 2,
            "created_at": "2025-10-02T13:33:00.000000Z",
            "updated_at": "2025-10-02T13:33:00.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 489,
            "name": "Холодильники",
            "slug": "xolodilniki",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 481,
            "position": 2,
            "created_at": "2025-09-08T05:28:33.000000Z",
            "updated_at": "2025-09-08T05:28:33.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 164,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 490,
            "name": "Плиты",
            "slug": "plity",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 481,
            "position": 2,
            "created_at": "2025-09-08T05:29:21.000000Z",
            "updated_at": "2025-09-08T05:29:21.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 43,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 497,
            "name": "Кулеры для воды",
            "slug": "kulery-dlia-vody",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 481,
            "position": 2,
            "created_at": "2025-09-08T05:33:05.000000Z",
            "updated_at": "2025-09-08T05:33:05.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 2,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 498,
            "name": "Плиты газовые и комбинированные",
            "slug": "plity-gazovye-i-kombinirovannye",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 481,
            "position": 2,
            "created_at": "2025-09-08T05:33:35.000000Z",
            "updated_at": "2025-09-08T05:33:35.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 177,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 482,
        "name": "Приготовление пищи",
        "slug": "prigotovlenie-pishhi",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-09-08T05:05:27.000000Z",
        "updated_at": "2025-09-08T05:05:27.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 80,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 499,
            "name": "Микроволновые печи",
            "slug": "mikrovolnovye-peci",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 482,
            "position": 2,
            "created_at": "2025-09-08T05:34:02.000000Z",
            "updated_at": "2025-09-08T05:34:02.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 78,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 484,
        "name": "Мелкая кухонная техника",
        "slug": "melkaia-kuxonnaia-texnika",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-09-08T05:06:49.000000Z",
        "updated_at": "2025-09-08T05:06:49.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 27,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 500,
            "name": "Мини-печи",
            "slug": "mini-peci",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 484,
            "position": 2,
            "created_at": "2025-09-08T05:34:24.000000Z",
            "updated_at": "2025-09-08T05:34:24.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 25,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 485,
        "name": "Встраиваемая техника",
        "slug": "vstraivaemaia-texnika",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-09-08T05:07:16.000000Z",
        "updated_at": "2025-09-08T05:07:16.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 0,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [],
        "translations": []
      },
      {
        "id": 487,
        "name": "Пылесосы",
        "slug": "pylesosy",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-09-08T05:26:54.000000Z",
        "updated_at": "2025-09-08T05:26:54.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 96,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 492,
            "name": "Все пылесосы",
            "slug": "vse-pylesosy",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 487,
            "position": 2,
            "created_at": "2025-09-08T05:30:53.000000Z",
            "updated_at": "2025-09-08T05:30:53.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 59,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 488,
        "name": "Климатическая техника",
        "slug": "klimaticeskaia-texnika",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-09-08T05:27:18.000000Z",
        "updated_at": "2025-09-08T05:27:18.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 248,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 543,
            "name": "Аристон",
            "slug": "ariston",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 488,
            "position": 2,
            "created_at": "2025-09-29T07:05:09.000000Z",
            "updated_at": "2025-09-29T07:05:09.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 15,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 493,
            "name": "Кондиционеры",
            "slug": "kondicionery",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 488,
            "position": 2,
            "created_at": "2025-09-08T05:31:19.000000Z",
            "updated_at": "2025-09-08T05:31:19.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 158,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 494,
            "name": "Водонагреватели",
            "slug": "vodonagrevateli",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 488,
            "position": 2,
            "created_at": "2025-09-08T05:31:45.000000Z",
            "updated_at": "2025-09-08T05:31:45.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 16,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 495,
            "name": "Увлажнители воздуха",
            "slug": "uvlazniteli-vozduxa",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 488,
            "position": 2,
            "created_at": "2025-09-08T05:32:09.000000Z",
            "updated_at": "2025-09-08T05:32:09.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 496,
            "name": "Очистители воздуха",
            "slug": "ocistiteli-vozduxa",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 488,
            "position": 2,
            "created_at": "2025-09-08T05:32:32.000000Z",
            "updated_at": "2025-09-08T05:32:32.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 38,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 546,
        "name": "Электрические машинки для стрижки волос",
        "slug": "elektriceskie-masinki-dlia-strizki-volos",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 427,
        "position": 1,
        "created_at": "2025-10-03T05:59:09.000000Z",
        "updated_at": "2025-10-03T05:59:40.000000Z",
        "home_status": 1,
        "priority": 6,
        "sub_category_product_count": 11,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [],
        "translations": []
      }
    ],
    "translations": []
  },
  {
    "id": 428,
    "name": "O'yinlar va dasturiy ta'minot",
    "slug": "oyinlar-va-dasturiy-taminot",
    "icon": "2025-08-19-68a4272b76903.webp",
    "icon_storage_type": "public",
    "parent_id": 0,
    "position": 0,
    "created_at": "2025-08-08T12:33:43.000000Z",
    "updated_at": "2025-09-12T05:39:24.000000Z",
    "home_status": 1,
    "priority": 0,
    "icon_full_url": {
      "key": "2025-08-19-68a4272b76903.webp",
      "path": "https://api.venu.uz/storage/category/2025-08-19-68a4272b76903.webp",
      "status": 200
    },
    "childes": [
      {
        "id": 555,
        "name": "Видеокарта",
        "slug": "videokarta",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 428,
        "position": 1,
        "created_at": "2025-10-03T10:06:54.000000Z",
        "updated_at": "2025-10-03T10:06:54.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 5,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [],
        "translations": []
      },
      {
        "id": 561,
        "name": "PC",
        "slug": "pc",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 428,
        "position": 1,
        "created_at": "2025-10-03T11:58:43.000000Z",
        "updated_at": "2025-10-03T11:58:43.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 249,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 562,
            "name": "Игровые ноутбуки",
            "slug": "igrovye-noutbuki",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 561,
            "position": 2,
            "created_at": "2025-10-03T12:07:48.000000Z",
            "updated_at": "2025-10-03T12:07:48.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 563,
            "name": "Клавиатуры, мыши и гарнитуры",
            "slug": "klaviatury-mysi-i-garnitury",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 561,
            "position": 2,
            "created_at": "2025-10-03T12:08:33.000000Z",
            "updated_at": "2025-10-03T12:08:33.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 189,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 564,
            "name": "Игровые Кресло",
            "slug": "igrovye-kreslo",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 561,
            "position": 2,
            "created_at": "2025-10-03T12:09:53.000000Z",
            "updated_at": "2025-10-03T12:09:53.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 41,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 565,
            "name": "Игровые системные блоки",
            "slug": "igrovye-sistemnye-bloki",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 561,
            "position": 2,
            "created_at": "2025-10-03T12:15:33.000000Z",
            "updated_at": "2025-10-03T12:15:33.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 2,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 579,
            "name": "игравой наушники",
            "slug": "igravoi-nausniki",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 561,
            "position": 2,
            "created_at": "2025-10-06T06:24:56.000000Z",
            "updated_at": "2025-10-06T06:24:56.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 11,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 580,
            "name": "Монитор PROGAMING",
            "slug": "monitor-progaming",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 561,
            "position": 2,
            "created_at": "2025-10-09T06:30:26.000000Z",
            "updated_at": "2025-10-09T06:30:26.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 6,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 476,
        "name": "PlayStation",
        "slug": "playstation",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 428,
        "position": 1,
        "created_at": "2025-08-28T11:38:21.000000Z",
        "updated_at": "2025-08-28T13:30:28.000000Z",
        "home_status": 1,
        "priority": 0,
        "sub_category_product_count": 5,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 477,
            "name": "Консоли PlayStation 5",
            "slug": "konsoli-playstation-5",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 476,
            "position": 2,
            "created_at": "2025-08-28T11:38:51.000000Z",
            "updated_at": "2025-08-28T13:32:08.000000Z",
            "home_status": 1,
            "priority": 0,
            "sub_sub_category_product_count": 4,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      }
    ],
    "translations": []
  },
  {
    "id": 503,
    "name": "Aqilli uy",
    "slug": "aqilli-uy",
    "icon": "2025-09-17-68caae1a6cae9.webp",
    "icon_storage_type": "public",
    "parent_id": 0,
    "position": 0,
    "created_at": "2025-09-10T11:28:13.000000Z",
    "updated_at": "2025-09-17T12:48:26.000000Z",
    "home_status": 1,
    "priority": 0,
    "icon_full_url": {
      "key": "2025-09-17-68caae1a6cae9.webp",
      "path": "https://api.venu.uz/storage/category/2025-09-17-68caae1a6cae9.webp",
      "status": 200
    },
    "childes": [
      {
        "id": 538,
        "name": "Экосистемы",
        "slug": "ekosistemy",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 503,
        "position": 1,
        "created_at": "2025-09-26T10:04:08.000000Z",
        "updated_at": "2025-09-26T10:04:08.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 0,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 539,
            "name": "Яндекс",
            "slug": "iandeks",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 538,
            "position": 2,
            "created_at": "2025-09-26T10:04:53.000000Z",
            "updated_at": "2025-09-26T10:04:53.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 540,
        "name": "Устройства для умного дома",
        "slug": "ustroistva-dlia-umnogo-doma",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 503,
        "position": 1,
        "created_at": "2025-09-26T10:05:51.000000Z",
        "updated_at": "2025-09-26T10:05:51.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 109,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 541,
            "name": "IP-камеры",
            "slug": "ip-kamery",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 540,
            "position": 2,
            "created_at": "2025-09-26T10:06:15.000000Z",
            "updated_at": "2025-09-26T10:06:15.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 109,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 550,
        "name": "Сетевое оборудование",
        "slug": "setevoe-oborudovanie",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 503,
        "position": 1,
        "created_at": "2025-10-03T07:08:53.000000Z",
        "updated_at": "2025-10-03T07:08:53.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 848,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 551,
            "name": "Переключатели, переходники, модули",
            "slug": "perekliucateli-perexodniki-moduli",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 550,
            "position": 2,
            "created_at": "2025-10-03T07:09:57.000000Z",
            "updated_at": "2025-10-03T07:09:57.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 124,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 552,
            "name": "Коммутаторы",
            "slug": "kommutatory",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 550,
            "position": 2,
            "created_at": "2025-10-03T08:22:17.000000Z",
            "updated_at": "2025-10-03T08:22:17.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 49,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 553,
            "name": "Маршрутизаторы",
            "slug": "marsrutizatory",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 550,
            "position": 2,
            "created_at": "2025-10-03T09:31:49.000000Z",
            "updated_at": "2025-10-03T09:31:49.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 582,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 554,
            "name": "Wi-Fi Точки доступа",
            "slug": "wi-fi-tocki-dostupa",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 550,
            "position": 2,
            "created_at": "2025-10-03T09:33:29.000000Z",
            "updated_at": "2025-10-03T09:33:29.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 81,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 568,
        "name": "Видеонаблюдение",
        "slug": "videonabliudenie",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 503,
        "position": 1,
        "created_at": "2025-10-04T05:09:16.000000Z",
        "updated_at": "2025-10-04T05:09:16.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 3,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 569,
            "name": "Камеры",
            "slug": "kamery",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 568,
            "position": 2,
            "created_at": "2025-10-04T05:09:35.000000Z",
            "updated_at": "2025-10-04T05:09:35.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 2,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 570,
            "name": "Видеорегистратор",
            "slug": "videoregistrator",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 568,
            "position": 2,
            "created_at": "2025-10-04T05:28:44.000000Z",
            "updated_at": "2025-10-04T05:28:44.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 1,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      }
    ],
    "translations": []
  },
  {
    "id": 504,
    "name": "Foto va video",
    "slug": "foto-va-video",
    "icon": "2025-09-10-68c16133d4136.webp",
    "icon_storage_type": "public",
    "parent_id": 0,
    "position": 0,
    "created_at": "2025-09-10T11:29:55.000000Z",
    "updated_at": "2025-09-12T05:38:34.000000Z",
    "home_status": 1,
    "priority": 0,
    "icon_full_url": {
      "key": "2025-09-10-68c16133d4136.webp",
      "path": "https://api.venu.uz/storage/category/2025-09-10-68c16133d4136.webp",
      "status": 200
    },
    "childes": [
      {
        "id": 514,
        "name": "Проэкторы",
        "slug": "proektory",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 504,
        "position": 1,
        "created_at": "2025-09-17T10:28:52.000000Z",
        "updated_at": "2025-09-17T10:28:52.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 10,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 515,
            "name": "Проэкторы телефона",
            "slug": "proektory-telefona",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 514,
            "position": 2,
            "created_at": "2025-09-17T10:29:30.000000Z",
            "updated_at": "2025-09-17T10:29:30.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 1,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 606,
        "name": "Камера",
        "slug": "kamera",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 504,
        "position": 1,
        "created_at": "2025-12-11T11:13:59.000000Z",
        "updated_at": "2025-12-11T11:13:59.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 15,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 607,
            "name": "Автомобильная камера",
            "slug": "avtomobilnaia-kamera",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 606,
            "position": 2,
            "created_at": "2025-12-11T11:16:30.000000Z",
            "updated_at": "2025-12-11T11:16:30.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 15,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      }
    ],
    "translations": []
  },
  {
    "id": 429,
    "name": "Aksessuarlar",
    "slug": "aksessuarlar",
    "icon": "2025-08-19-68a4273f72726.webp",
    "icon_storage_type": "public",
    "parent_id": 0,
    "position": 0,
    "created_at": "2025-08-08T12:33:53.000000Z",
    "updated_at": "2025-09-12T05:38:59.000000Z",
    "home_status": 1,
    "priority": 1,
    "icon_full_url": {
      "key": "2025-08-19-68a4273f72726.webp",
      "path": "https://api.venu.uz/storage/category/2025-08-19-68a4273f72726.webp",
      "status": 200
    },
    "childes": [
      {
        "id": 518,
        "name": "Компьютерные аксессуары",
        "slug": "kompiuternye-aksessuary",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 429,
        "position": 1,
        "created_at": "2025-09-19T06:10:02.000000Z",
        "updated_at": "2025-09-19T06:10:02.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 1115,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 523,
            "name": "Клавиатуры и мыши",
            "slug": "klaviatury-i-mysi",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 518,
            "position": 2,
            "created_at": "2025-09-19T06:12:15.000000Z",
            "updated_at": "2025-09-19T06:12:15.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 366,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 524,
            "name": "Внешние жёсткие диски",
            "slug": "vnesnie-zestkie-diski",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 518,
            "position": 2,
            "created_at": "2025-09-19T06:12:50.000000Z",
            "updated_at": "2025-09-19T06:12:50.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 526,
            "name": "Флеш-накопители",
            "slug": "fles-nakopiteli",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 518,
            "position": 2,
            "created_at": "2025-09-19T06:14:02.000000Z",
            "updated_at": "2025-09-19T06:14:02.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 527,
            "name": "Роутеры и сетевое оборудование",
            "slug": "routery-i-setevoe-oborudovanie",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 518,
            "position": 2,
            "created_at": "2025-09-19T06:14:47.000000Z",
            "updated_at": "2025-09-19T06:14:47.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 3,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 519,
        "name": "Аксессуары для домашней техники",
        "slug": "aksessuary-dlia-domasnei-texniki",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 429,
        "position": 1,
        "created_at": "2025-09-19T06:10:33.000000Z",
        "updated_at": "2025-09-19T06:10:33.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 49,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 521,
            "name": "Аксессуары для стиральных машин",
            "slug": "aksessuary-dlia-stiralnyx-masin",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 519,
            "position": 2,
            "created_at": "2025-09-19T06:11:24.000000Z",
            "updated_at": "2025-09-19T06:11:24.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 522,
            "name": "Аксессуары для пылесосов",
            "slug": "aksessuary-dlia-pylesosov",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 519,
            "position": 2,
            "created_at": "2025-09-19T06:11:45.000000Z",
            "updated_at": "2025-09-19T06:11:45.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 525,
            "name": "Компьютерные колонки",
            "slug": "kompiuternye-kolonki",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 519,
            "position": 2,
            "created_at": "2025-09-19T06:13:08.000000Z",
            "updated_at": "2025-09-19T06:13:08.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 590,
            "name": "Машинка для стрижки волос",
            "slug": "masinka-dlia-strizki-volos",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 519,
            "position": 2,
            "created_at": "2025-10-29T11:07:12.000000Z",
            "updated_at": "2025-10-29T11:07:12.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 44,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 520,
        "name": "Аксессуары для кухонной техники",
        "slug": "aksessuary-dlia-kuxonnoi-texniki",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 429,
        "position": 1,
        "created_at": "2025-09-19T06:10:52.000000Z",
        "updated_at": "2025-09-19T06:10:52.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 153,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 591,
            "name": "Кулер для корпуса",
            "slug": "kuler-dlia-korpusa",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 520,
            "position": 2,
            "created_at": "2025-11-07T05:34:20.000000Z",
            "updated_at": "2025-11-07T05:34:20.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 153,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 530,
        "name": "Источники бесперебойного питания",
        "slug": "istocniki-bespereboinogo-pitaniia",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 429,
        "position": 1,
        "created_at": "2025-09-19T09:15:41.000000Z",
        "updated_at": "2025-09-19T09:15:41.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 68,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 532,
            "name": "Линейно-интерактивные ИБП",
            "slug": "lineino-interaktivnye-ibp",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 530,
            "position": 2,
            "created_at": "2025-09-19T09:23:33.000000Z",
            "updated_at": "2025-09-19T09:23:33.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 68,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 534,
        "name": "Аксессуары для телевизоров",
        "slug": "aksessuary-dlia-televizorov",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 429,
        "position": 1,
        "created_at": "2025-09-19T13:28:55.000000Z",
        "updated_at": "2025-09-19T13:28:55.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 33,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 535,
            "name": "Кронштейны для телевизоров",
            "slug": "kronsteiny-dlia-televizorov",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 534,
            "position": 2,
            "created_at": "2025-09-19T13:30:04.000000Z",
            "updated_at": "2025-09-19T13:30:04.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 24,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 548,
            "name": "Кабель",
            "slug": "kabel",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 534,
            "position": 2,
            "created_at": "2025-10-03T06:04:07.000000Z",
            "updated_at": "2025-10-03T06:04:07.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 549,
            "name": "Приставки Smart TV и приемники DVB-T2",
            "slug": "pristavki-smart-tv-i-priemniki-dvb-t2",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 534,
            "position": 2,
            "created_at": "2025-10-03T06:12:37.000000Z",
            "updated_at": "2025-10-03T06:12:37.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 4,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 609,
        "name": "Аксессуары для умного дома",
        "slug": "aksessuary-dlia-umnogo-doma",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 429,
        "position": 1,
        "created_at": "2025-12-22T06:57:24.000000Z",
        "updated_at": "2025-12-22T06:57:24.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 3,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 610,
            "name": "Розетка",
            "slug": "rozetka",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 609,
            "position": 2,
            "created_at": "2025-12-22T06:59:27.000000Z",
            "updated_at": "2025-12-22T06:59:27.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 3,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 478,
        "name": "Аксессуары для смартфон",
        "slug": "aksessuary-dlia-smartfon",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 429,
        "position": 1,
        "created_at": "2025-08-29T06:31:11.000000Z",
        "updated_at": "2025-08-29T06:31:11.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 11,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 571,
            "name": "Стекло",
            "slug": "steklo",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 478,
            "position": 2,
            "created_at": "2025-10-05T03:28:35.000000Z",
            "updated_at": "2025-10-05T03:28:35.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 2,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 572,
            "name": "батарейка",
            "slug": "batareika",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 478,
            "position": 2,
            "created_at": "2025-10-05T03:34:07.000000Z",
            "updated_at": "2025-10-05T03:34:07.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 4,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 479,
            "name": "Зарядные устройства",
            "slug": "zariadnye-ustroistva",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 478,
            "position": 2,
            "created_at": "2025-08-29T06:33:11.000000Z",
            "updated_at": "2025-08-29T06:33:11.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 4,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 480,
            "name": "Карты памяти",
            "slug": "karty-pamiati",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 478,
            "position": 2,
            "created_at": "2025-08-29T06:33:50.000000Z",
            "updated_at": "2025-08-29T06:33:50.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 505,
        "name": "Компьютерные аксессуары",
        "slug": "kompiuternye-aksessuary",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 429,
        "position": 1,
        "created_at": "2025-09-15T15:35:20.000000Z",
        "updated_at": "2025-09-15T15:35:20.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 350,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [
          {
            "id": 545,
            "name": "Роутеры и сетевое оборудование",
            "slug": "routery-i-setevoe-oborudovanie",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 505,
            "position": 2,
            "created_at": "2025-10-03T05:55:42.000000Z",
            "updated_at": "2025-10-03T05:55:42.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 2,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 556,
            "name": "Флеш-накопители",
            "slug": "fles-nakopiteli",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 505,
            "position": 2,
            "created_at": "2025-10-03T10:18:45.000000Z",
            "updated_at": "2025-10-03T10:18:45.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 0,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 598,
            "name": "сумка",
            "slug": "sumka",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 505,
            "position": 2,
            "created_at": "2025-11-13T09:08:08.000000Z",
            "updated_at": "2025-11-13T09:08:08.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 108,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 599,
            "name": "Аккумулятор для ноутбука",
            "slug": "akkumuliator-dlia-noutbuka",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 505,
            "position": 2,
            "created_at": "2025-11-14T04:50:15.000000Z",
            "updated_at": "2025-11-14T04:50:15.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 305,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          },
          {
            "id": 506,
            "name": "Роутеры и сетевое оборудование",
            "slug": "routery-i-setevoe-oborudovanie",
            "icon": "def.png",
            "icon_storage_type": null,
            "parent_id": 505,
            "position": 2,
            "created_at": "2025-09-15T15:36:25.000000Z",
            "updated_at": "2025-09-15T15:36:25.000000Z",
            "home_status": 1,
            "priority": null,
            "sub_sub_category_product_count": 18,
            "icon_full_url": {
              "key": "def.png",
              "path": null,
              "status": 404
            },
            "translations": []
          }
        ],
        "translations": []
      },
      {
        "id": 511,
        "name": "Аксессуары для фото и видеотехники",
        "slug": "aksessuary-dlia-foto-i-videotexniki",
        "icon": "def.png",
        "icon_storage_type": null,
        "parent_id": 429,
        "position": 1,
        "created_at": "2025-09-17T10:19:53.000000Z",
        "updated_at": "2025-09-17T10:19:53.000000Z",
        "home_status": 1,
        "priority": null,
        "sub_category_product_count": 1,
        "icon_full_url": {
          "key": "def.png",
          "path": null,
          "status": 404
        },
        "childes": [],
        "translations": []
      }
    ],
    "translations": []
  }
]



Brendlar
Method: GET
URL
https://api.venu.uz/api/v3/seller/brands
Headers
accept-encoding:
gzip
authorization:
Bearer mk8l2eh6GM5yICFv1mCrheNfbC1H8QqOJAIt8IsKN8deGUilsa
content-type:
application/json; charset=UTF-8
host:
api.venu.uz
lang:
en
user-agent:
Dart/3.10 (dart:io)

[
  {
    "id": 1,
    "name": "Nokia",
    "image": "2025-09-12-68c4096b7f77a.webp",
    "image_storage_type": "public",
    "image_alt_text": "nokia",
    "status": 1,
    "created_at": "2025-07-03T20:27:22.000000Z",
    "updated_at": "2025-09-12T11:57:20.000000Z",
    "image_full_url": {
      "key": "2025-09-12-68c4096b7f77a.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-12-68c4096b7f77a.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 2,
    "name": "Iphone",
    "image": "2025-09-11-68c2c3b746b66.webp",
    "image_storage_type": "public",
    "image_alt_text": "Iphone",
    "status": 1,
    "created_at": "2025-07-03T21:32:08.000000Z",
    "updated_at": "2025-09-11T12:42:31.000000Z",
    "image_full_url": {
      "key": "2025-09-11-68c2c3b746b66.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-11-68c2c3b746b66.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 3,
    "name": "artel",
    "image": "2025-08-07-68943c68d5a40.webp",
    "image_storage_type": "public",
    "image_alt_text": "artel",
    "status": 1,
    "created_at": "2025-07-16T18:12:20.000000Z",
    "updated_at": "2025-08-11T07:47:00.000000Z",
    "image_full_url": {
      "key": "2025-08-07-68943c68d5a40.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-07-68943c68d5a40.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 4,
    "name": "DELL",
    "image": "2025-07-29-6888af33a848c.webp",
    "image_storage_type": "public",
    "image_alt_text": "Dell Vostro",
    "status": 1,
    "created_at": "2025-07-29T11:23:31.000000Z",
    "updated_at": "2025-08-11T06:30:14.000000Z",
    "image_full_url": {
      "key": "2025-07-29-6888af33a848c.webp",
      "path": "https://api.venu.uz/storage/brand/2025-07-29-6888af33a848c.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 6,
    "name": "lenovo",
    "image": "2025-07-29-6888bfd544613.webp",
    "image_storage_type": "public",
    "image_alt_text": "lenovo",
    "status": 1,
    "created_at": "2025-07-29T12:34:29.000000Z",
    "updated_at": "2025-08-11T07:46:29.000000Z",
    "image_full_url": {
      "key": "2025-07-29-6888bfd544613.webp",
      "path": "https://api.venu.uz/storage/brand/2025-07-29-6888bfd544613.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 7,
    "name": "acer",
    "image": "2025-07-29-6888c00c87473.webp",
    "image_storage_type": "public",
    "image_alt_text": "acer",
    "status": 1,
    "created_at": "2025-07-29T12:35:24.000000Z",
    "updated_at": "2025-08-11T07:46:04.000000Z",
    "image_full_url": {
      "key": "2025-07-29-6888c00c87473.webp",
      "path": "https://api.venu.uz/storage/brand/2025-07-29-6888c00c87473.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 8,
    "name": "ASUS",
    "image": "2025-07-29-6888c06859f5c.webp",
    "image_storage_type": "public",
    "image_alt_text": "ASUS VIVABOOK",
    "status": 1,
    "created_at": "2025-07-29T12:36:56.000000Z",
    "updated_at": "2025-08-26T02:06:14.000000Z",
    "image_full_url": {
      "key": "2025-07-29-6888c06859f5c.webp",
      "path": "https://api.venu.uz/storage/brand/2025-07-29-6888c06859f5c.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 9,
    "name": "GIGABYTE",
    "image": "2025-07-30-68891c5352961.webp",
    "image_storage_type": "public",
    "image_alt_text": "GIGABYTE",
    "status": 1,
    "created_at": "2025-07-29T19:09:07.000000Z",
    "updated_at": "2025-07-29T19:09:07.000000Z",
    "image_full_url": {
      "key": "2025-07-30-68891c5352961.webp",
      "path": "https://api.venu.uz/storage/brand/2025-07-30-68891c5352961.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 10,
    "name": "Msi",
    "image": "2025-07-30-68891ca73fe0f.webp",
    "image_storage_type": "public",
    "image_alt_text": "msi",
    "status": 1,
    "created_at": "2025-07-29T19:10:31.000000Z",
    "updated_at": "2025-10-28T07:29:50.000000Z",
    "image_full_url": {
      "key": "2025-07-30-68891ca73fe0f.webp",
      "path": "https://api.venu.uz/storage/brand/2025-07-30-68891ca73fe0f.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 11,
    "name": "HP",
    "image": "2025-08-09-6897383b28d2c.webp",
    "image_storage_type": "public",
    "image_alt_text": "HP",
    "status": 1,
    "created_at": "2025-07-29T19:13:16.000000Z",
    "updated_at": "2025-08-09T11:59:55.000000Z",
    "image_full_url": {
      "key": "2025-08-09-6897383b28d2c.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-09-6897383b28d2c.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 12,
    "name": "Hanson",
    "image": "2025-08-01-688c81913c415.webp",
    "image_storage_type": "public",
    "image_alt_text": "Hanson",
    "status": 1,
    "created_at": "2025-08-01T08:57:53.000000Z",
    "updated_at": "2025-08-11T07:43:20.000000Z",
    "image_full_url": {
      "key": "2025-08-01-688c81913c415.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-01-688c81913c415.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 14,
    "name": "SAMSUNG",
    "image": "2025-08-08-6895ec822b96c.webp",
    "image_storage_type": "public",
    "image_alt_text": "SAMSUNG",
    "status": 1,
    "created_at": "2025-08-07T05:38:23.000000Z",
    "updated_at": "2025-08-11T07:42:39.000000Z",
    "image_full_url": {
      "key": "2025-08-08-6895ec822b96c.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-08-6895ec822b96c.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 15,
    "name": "SHIVAKI",
    "image": "2025-09-25-68d4ea69230ba.webp",
    "image_storage_type": "public",
    "image_alt_text": "SHIVAKI",
    "status": 1,
    "created_at": "2025-08-07T05:38:46.000000Z",
    "updated_at": "2025-09-25T07:08:25.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4ea69230ba.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4ea69230ba.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 16,
    "name": "avalon",
    "image": "2025-08-07-68943da9ea93b.webp",
    "image_storage_type": "public",
    "image_alt_text": "avalon",
    "status": 1,
    "created_at": "2025-08-07T05:46:17.000000Z",
    "updated_at": "2025-08-11T07:41:45.000000Z",
    "image_full_url": {
      "key": "2025-08-07-68943da9ea93b.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-07-68943da9ea93b.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 17,
    "name": "crucial",
    "image": "2025-08-08-68959972d1580.webp",
    "image_storage_type": "public",
    "image_alt_text": "crucial",
    "status": 1,
    "created_at": "2025-08-08T06:30:10.000000Z",
    "updated_at": "2025-08-11T07:40:15.000000Z",
    "image_full_url": {
      "key": "2025-08-08-68959972d1580.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-08-68959972d1580.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 18,
    "name": "Kingston",
    "image": "2025-08-08-689599bb204ba.webp",
    "image_storage_type": "public",
    "image_alt_text": "Kingston",
    "status": 1,
    "created_at": "2025-08-08T06:31:23.000000Z",
    "updated_at": "2025-08-11T07:36:58.000000Z",
    "image_full_url": {
      "key": "2025-08-08-689599bb204ba.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-08-689599bb204ba.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 19,
    "name": "Lexar",
    "image": "2025-08-08-68959a08b499b.webp",
    "image_storage_type": "public",
    "image_alt_text": "Lexar",
    "status": 1,
    "created_at": "2025-08-08T06:32:40.000000Z",
    "updated_at": "2025-08-11T07:35:09.000000Z",
    "image_full_url": {
      "key": "2025-08-08-68959a08b499b.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-08-68959a08b499b.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 20,
    "name": "TEAMGROUP",
    "image": "2025-09-25-68d4ebc43d15d.webp",
    "image_storage_type": "public",
    "image_alt_text": "TeamGroup",
    "status": 1,
    "created_at": "2025-08-08T06:34:23.000000Z",
    "updated_at": "2025-09-25T07:14:12.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4ebc43d15d.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4ebc43d15d.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 21,
    "name": "MONTECH",
    "image": "2025-08-13-689c234219d8f.webp",
    "image_storage_type": "public",
    "image_alt_text": "MONTECH",
    "status": 1,
    "created_at": "2025-08-13T05:31:46.000000Z",
    "updated_at": "2025-08-13T05:31:46.000000Z",
    "image_full_url": {
      "key": "2025-08-13-689c234219d8f.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-13-689c234219d8f.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 22,
    "name": "defender",
    "image": "2025-08-13-689c2b4d9fdfa.webp",
    "image_storage_type": "public",
    "image_alt_text": "defender",
    "status": 1,
    "created_at": "2025-08-13T06:06:05.000000Z",
    "updated_at": "2025-08-13T06:06:05.000000Z",
    "image_full_url": {
      "key": "2025-08-13-689c2b4d9fdfa.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-13-689c2b4d9fdfa.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 23,
    "name": "FSP",
    "image": "2025-08-14-689d7ffaa288e.webp",
    "image_storage_type": "public",
    "image_alt_text": "FSP",
    "status": 1,
    "created_at": "2025-08-14T05:39:54.000000Z",
    "updated_at": "2025-08-14T06:19:38.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689d7ffaa288e.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689d7ffaa288e.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 24,
    "name": "GALAX",
    "image": "2025-08-14-689d7f990a8ac.webp",
    "image_storage_type": "public",
    "image_alt_text": "GALAX",
    "status": 1,
    "created_at": "2025-08-14T06:18:01.000000Z",
    "updated_at": "2025-08-14T06:18:01.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689d7f990a8ac.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689d7f990a8ac.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 25,
    "name": "POWERCASE",
    "image": "2025-08-14-689d94de08362.webp",
    "image_storage_type": "public",
    "image_alt_text": "POWERCASE",
    "status": 1,
    "created_at": "2025-08-14T07:48:46.000000Z",
    "updated_at": "2025-08-14T07:48:46.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689d94de08362.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689d94de08362.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 26,
    "name": "intel",
    "image": "2025-08-14-689dd9b078e51.webp",
    "image_storage_type": "public",
    "image_alt_text": "intel",
    "status": 1,
    "created_at": "2025-08-14T12:42:24.000000Z",
    "updated_at": "2025-08-14T12:42:34.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689dd9b078e51.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689dd9b078e51.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 27,
    "name": "AULA",
    "image": "2025-08-14-689dda37d49a1.webp",
    "image_storage_type": "public",
    "image_alt_text": "AULA",
    "status": 1,
    "created_at": "2025-08-14T12:44:39.000000Z",
    "updated_at": "2025-08-14T12:44:39.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689dda37d49a1.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689dda37d49a1.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 28,
    "name": "thermoltake",
    "image": "2025-09-25-68d4ea5381c72.webp",
    "image_storage_type": "public",
    "image_alt_text": "thermoltake",
    "status": 1,
    "created_at": "2025-08-14T12:47:49.000000Z",
    "updated_at": "2025-09-25T07:08:03.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4ea5381c72.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4ea5381c72.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 29,
    "name": "jonsbo",
    "image": "2025-08-14-689ddcaf0f8df.webp",
    "image_storage_type": "public",
    "image_alt_text": "jonsbo",
    "status": 1,
    "created_at": "2025-08-14T12:55:11.000000Z",
    "updated_at": "2025-08-14T12:55:11.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689ddcaf0f8df.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689ddcaf0f8df.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 30,
    "name": "MeeTion",
    "image": "2025-08-14-689dde0a64cbe.webp",
    "image_storage_type": "public",
    "image_alt_text": "MeeTion",
    "status": 1,
    "created_at": "2025-08-14T13:00:58.000000Z",
    "updated_at": "2025-08-14T13:00:58.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689dde0a64cbe.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689dde0a64cbe.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 31,
    "name": "DXRacer",
    "image": "2025-08-14-689ddf206f8e0.webp",
    "image_storage_type": "public",
    "image_alt_text": "DXRacer",
    "status": 1,
    "created_at": "2025-08-14T13:05:36.000000Z",
    "updated_at": "2025-08-14T13:05:36.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689ddf206f8e0.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689ddf206f8e0.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 32,
    "name": "CoolerMaster",
    "image": "2025-08-14-689ddfcb51711.webp",
    "image_storage_type": "public",
    "image_alt_text": "CoolerMaster",
    "status": 1,
    "created_at": "2025-08-14T13:08:27.000000Z",
    "updated_at": "2025-08-14T13:08:27.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689ddfcb51711.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689ddfcb51711.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 33,
    "name": "REDRAGON",
    "image": "2025-08-14-689de04db3a8d.webp",
    "image_storage_type": "public",
    "image_alt_text": "REDRAGON",
    "status": 1,
    "created_at": "2025-08-14T13:10:37.000000Z",
    "updated_at": "2025-08-14T13:10:37.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689de04db3a8d.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689de04db3a8d.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 34,
    "name": "Sharkoon",
    "image": "2025-09-25-68d4eadcb2b0a.webp",
    "image_storage_type": "public",
    "image_alt_text": "Sharkoon",
    "status": 1,
    "created_at": "2025-08-14T13:15:05.000000Z",
    "updated_at": "2025-09-25T07:10:20.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4eadcb2b0a.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4eadcb2b0a.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 35,
    "name": "FENDA",
    "image": "2025-08-14-689de298d9c23.webp",
    "image_storage_type": "public",
    "image_alt_text": "FENDA",
    "status": 1,
    "created_at": "2025-08-14T13:20:24.000000Z",
    "updated_at": "2025-08-14T13:20:24.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689de298d9c23.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689de298d9c23.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 36,
    "name": "EDIFIER",
    "image": "2025-08-14-689de375082ac.webp",
    "image_storage_type": "public",
    "image_alt_text": "EDIFIER",
    "status": 1,
    "created_at": "2025-08-14T13:24:05.000000Z",
    "updated_at": "2025-08-14T13:24:05.000000Z",
    "image_full_url": {
      "key": "2025-08-14-689de375082ac.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-14-689de375082ac.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 37,
    "name": "KOSS",
    "image": "2025-08-19-68a4212728b60.webp",
    "image_storage_type": "public",
    "image_alt_text": "KOSS",
    "status": 1,
    "created_at": "2025-08-19T07:00:55.000000Z",
    "updated_at": "2025-08-19T07:00:55.000000Z",
    "image_full_url": {
      "key": "2025-08-19-68a4212728b60.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-19-68a4212728b60.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 38,
    "name": "audio-technica",
    "image": "2025-08-19-68a42793121b3.webp",
    "image_storage_type": "public",
    "image_alt_text": "audio-technica",
    "status": 1,
    "created_at": "2025-08-19T07:28:19.000000Z",
    "updated_at": "2025-08-19T07:28:19.000000Z",
    "image_full_url": {
      "key": "2025-08-19-68a42793121b3.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-19-68a42793121b3.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 39,
    "name": "Gembird",
    "image": "2025-08-19-68a451c8a1bd3.webp",
    "image_storage_type": "public",
    "image_alt_text": "Gembird",
    "status": 1,
    "created_at": "2025-08-19T10:28:24.000000Z",
    "updated_at": "2025-08-19T10:28:24.000000Z",
    "image_full_url": {
      "key": "2025-08-19-68a451c8a1bd3.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-19-68a451c8a1bd3.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 40,
    "name": "Gamdias",
    "image": "2025-08-19-68a454022e56c.webp",
    "image_storage_type": "public",
    "image_alt_text": "Gamdias",
    "status": 1,
    "created_at": "2025-08-19T10:37:54.000000Z",
    "updated_at": "2025-08-19T10:37:54.000000Z",
    "image_full_url": {
      "key": "2025-08-19-68a454022e56c.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-19-68a454022e56c.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 41,
    "name": "DeepCool",
    "image": "2025-08-19-68a454b2a4586.webp",
    "image_storage_type": "public",
    "image_alt_text": "DeepCool",
    "status": 1,
    "created_at": "2025-08-19T10:40:50.000000Z",
    "updated_at": "2025-08-19T10:40:50.000000Z",
    "image_full_url": {
      "key": "2025-08-19-68a454b2a4586.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-19-68a454b2a4586.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 42,
    "name": "e-SURF",
    "image": "2025-08-19-68a4623deb6db.webp",
    "image_storage_type": "public",
    "image_alt_text": "e-SURF",
    "status": 1,
    "created_at": "2025-08-19T11:38:37.000000Z",
    "updated_at": "2025-08-19T11:38:37.000000Z",
    "image_full_url": {
      "key": "2025-08-19-68a4623deb6db.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-19-68a4623deb6db.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 43,
    "name": "Vissonic",
    "image": "2025-09-25-68d4eba2eb5bd.webp",
    "image_storage_type": "public",
    "image_alt_text": "Vissonic",
    "status": 1,
    "created_at": "2025-08-19T23:28:39.000000Z",
    "updated_at": "2025-09-25T07:13:38.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4eba2eb5bd.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4eba2eb5bd.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 44,
    "name": "ID Cooling",
    "image": "2025-08-20-68a50d325a1eb.webp",
    "image_storage_type": "public",
    "image_alt_text": "ID Cooling",
    "status": 1,
    "created_at": "2025-08-19T23:48:02.000000Z",
    "updated_at": "2025-08-19T23:48:02.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a50d325a1eb.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a50d325a1eb.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 45,
    "name": "Genius",
    "image": "2025-08-20-68a50dc82a217.webp",
    "image_storage_type": "public",
    "image_alt_text": "Genius",
    "status": 1,
    "created_at": "2025-08-19T23:50:32.000000Z",
    "updated_at": "2025-08-19T23:50:32.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a50dc82a217.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a50dc82a217.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 46,
    "name": "Lian li",
    "image": "2025-08-20-68a514951f562.webp",
    "image_storage_type": "public",
    "image_alt_text": "Lian li",
    "status": 1,
    "created_at": "2025-08-20T00:19:33.000000Z",
    "updated_at": "2025-08-20T00:19:33.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a514951f562.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a514951f562.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 47,
    "name": "ion",
    "image": "2025-08-20-68a51540a7652.webp",
    "image_storage_type": "public",
    "image_alt_text": "ion",
    "status": 1,
    "created_at": "2025-08-20T00:22:24.000000Z",
    "updated_at": "2025-08-20T00:22:45.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a51540a7652.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a51540a7652.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 49,
    "name": "Transcend",
    "image": "2025-09-25-68d4eb2a67270.webp",
    "image_storage_type": "public",
    "image_alt_text": "Transcend",
    "status": 1,
    "created_at": "2025-08-20T00:25:58.000000Z",
    "updated_at": "2025-09-25T07:11:38.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4eb2a67270.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4eb2a67270.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 50,
    "name": "TOSHIBA",
    "image": "2025-09-25-68d4ea7bb2948.webp",
    "image_storage_type": "public",
    "image_alt_text": "TOSHIBA",
    "status": 1,
    "created_at": "2025-08-20T00:28:01.000000Z",
    "updated_at": "2025-09-25T07:08:43.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4ea7bb2948.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4ea7bb2948.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 51,
    "name": "Seagate",
    "image": "2025-08-20-68a516dc34965.webp",
    "image_storage_type": "public",
    "image_alt_text": "Seagate",
    "status": 1,
    "created_at": "2025-08-20T00:29:16.000000Z",
    "updated_at": "2025-08-20T00:29:16.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a516dc34965.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a516dc34965.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 52,
    "name": "OSCOO",
    "image": "2025-08-20-68a5172aed560.webp",
    "image_storage_type": "public",
    "image_alt_text": "OSCOO",
    "status": 1,
    "created_at": "2025-08-20T00:30:34.000000Z",
    "updated_at": "2025-08-20T00:30:34.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a5172aed560.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a5172aed560.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 53,
    "name": "Walram",
    "image": "2025-09-25-68d4e9f07b5e2.webp",
    "image_storage_type": "public",
    "image_alt_text": "Walram",
    "status": 1,
    "created_at": "2025-08-20T00:39:50.000000Z",
    "updated_at": "2025-09-25T07:06:24.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4e9f07b5e2.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4e9f07b5e2.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 54,
    "name": "KingFast",
    "image": "2025-08-20-68a519b3e6755.webp",
    "image_storage_type": "public",
    "image_alt_text": "KingFast",
    "status": 1,
    "created_at": "2025-08-20T00:41:23.000000Z",
    "updated_at": "2025-08-20T00:41:23.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a519b3e6755.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a519b3e6755.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 55,
    "name": "GoldenMemory",
    "image": "2025-08-20-68a51e58cf728.webp",
    "image_storage_type": "public",
    "image_alt_text": "GoldenMemory",
    "status": 1,
    "created_at": "2025-08-20T01:01:12.000000Z",
    "updated_at": "2025-08-20T01:01:12.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a51e58cf728.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a51e58cf728.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 56,
    "name": "Zotac",
    "image": "2025-09-25-68d4ea231b651.webp",
    "image_storage_type": "public",
    "image_alt_text": "Zotac",
    "status": 1,
    "created_at": "2025-08-20T01:04:41.000000Z",
    "updated_at": "2025-09-25T07:07:15.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4ea231b651.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4ea231b651.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 57,
    "name": "Ryzen",
    "image": "2025-08-20-68a52278a0bc3.webp",
    "image_storage_type": "public",
    "image_alt_text": "Ryzen",
    "status": 1,
    "created_at": "2025-08-20T01:18:48.000000Z",
    "updated_at": "2025-08-20T01:18:48.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a52278a0bc3.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a52278a0bc3.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 58,
    "name": "EPSON",
    "image": "2025-08-20-68a525faa97c9.webp",
    "image_storage_type": "public",
    "image_alt_text": "EPSON",
    "status": 1,
    "created_at": "2025-08-20T01:33:46.000000Z",
    "updated_at": "2025-08-20T01:33:46.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a525faa97c9.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a525faa97c9.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 59,
    "name": "Pantum",
    "image": "2025-08-20-68a531cbf0bf2.webp",
    "image_storage_type": "public",
    "image_alt_text": "Pantum",
    "status": 1,
    "created_at": "2025-08-20T02:24:11.000000Z",
    "updated_at": "2025-08-20T02:24:11.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a531cbf0bf2.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a531cbf0bf2.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 60,
    "name": "Canon",
    "image": "2025-08-20-68a5326b415f0.webp",
    "image_storage_type": "public",
    "image_alt_text": "Canon",
    "status": 1,
    "created_at": "2025-08-20T02:26:51.000000Z",
    "updated_at": "2025-08-20T02:26:51.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a5326b415f0.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a5326b415f0.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 61,
    "name": "Sapphire",
    "image": "2025-08-20-68a532e4ae822.webp",
    "image_storage_type": "public",
    "image_alt_text": "Sapphire",
    "status": 1,
    "created_at": "2025-08-20T02:28:52.000000Z",
    "updated_at": "2025-08-20T02:28:52.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a532e4ae822.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a532e4ae822.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 62,
    "name": "Inno",
    "image": "2025-08-20-68a533203248a.webp",
    "image_storage_type": "public",
    "image_alt_text": "Inno",
    "status": 1,
    "created_at": "2025-08-20T02:29:52.000000Z",
    "updated_at": "2025-08-20T02:29:52.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a533203248a.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a533203248a.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 63,
    "name": "PNY",
    "image": "2025-08-20-68a5339d3bb17.webp",
    "image_storage_type": "public",
    "image_alt_text": "PNY",
    "status": 1,
    "created_at": "2025-08-20T02:31:57.000000Z",
    "updated_at": "2025-08-20T02:31:57.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a5339d3bb17.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a5339d3bb17.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 64,
    "name": "Arktek",
    "image": "2025-08-20-68a533dc00fa5.webp",
    "image_storage_type": "public",
    "image_alt_text": "Arktek",
    "status": 1,
    "created_at": "2025-08-20T02:33:00.000000Z",
    "updated_at": "2025-08-20T02:33:00.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a533dc00fa5.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a533dc00fa5.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 65,
    "name": "Axle",
    "image": "2025-08-20-68a5345d7861b.webp",
    "image_storage_type": "public",
    "image_alt_text": "Axle",
    "status": 1,
    "created_at": "2025-08-20T02:35:09.000000Z",
    "updated_at": "2025-08-20T02:35:09.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a5345d7861b.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a5345d7861b.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 66,
    "name": "Ezviz",
    "image": "2025-08-20-68a605e1e4f55.webp",
    "image_storage_type": "public",
    "image_alt_text": "Ezviz",
    "status": 1,
    "created_at": "2025-08-20T17:29:05.000000Z",
    "updated_at": "2025-08-20T17:29:05.000000Z",
    "image_full_url": {
      "key": "2025-08-20-68a605e1e4f55.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-20-68a605e1e4f55.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 67,
    "name": "LG",
    "image": "2025-08-28-68b0552d4ac6e.webp",
    "image_storage_type": "public",
    "image_alt_text": "LG",
    "status": 1,
    "created_at": "2025-08-28T13:10:05.000000Z",
    "updated_at": "2025-08-28T13:10:05.000000Z",
    "image_full_url": {
      "key": "2025-08-28-68b0552d4ac6e.webp",
      "path": "https://api.venu.uz/storage/brand/2025-08-28-68b0552d4ac6e.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 68,
    "name": "SONY",
    "image": "2025-09-25-68d4ea8bd08b2.webp",
    "image_storage_type": "public",
    "image_alt_text": "Sony",
    "status": 1,
    "created_at": "2025-08-28T13:52:23.000000Z",
    "updated_at": "2025-09-25T07:08:59.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4ea8bd08b2.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4ea8bd08b2.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 69,
    "name": "Engenius",
    "image": "2025-09-05-68bab093a5864.webp",
    "image_storage_type": "public",
    "image_alt_text": "Engenius",
    "status": 1,
    "created_at": "2025-09-05T09:42:43.000000Z",
    "updated_at": "2025-09-05T09:42:43.000000Z",
    "image_full_url": {
      "key": "2025-09-05-68bab093a5864.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-05-68bab093a5864.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 70,
    "name": "Aruba",
    "image": "2025-09-05-68bab10489757.webp",
    "image_storage_type": "public",
    "image_alt_text": "Aruba",
    "status": 1,
    "created_at": "2025-09-05T09:44:36.000000Z",
    "updated_at": "2025-09-05T09:44:36.000000Z",
    "image_full_url": {
      "key": "2025-09-05-68bab10489757.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-05-68bab10489757.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 71,
    "name": "TECNO",
    "image": "2025-09-25-68d4eac4e60fa.webp",
    "image_storage_type": "public",
    "image_alt_text": "TECNO",
    "status": 1,
    "created_at": "2025-09-05T11:00:48.000000Z",
    "updated_at": "2025-09-25T07:09:56.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4eac4e60fa.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4eac4e60fa.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 72,
    "name": "Eset",
    "image": "2025-09-08-68be864e9f87c.webp",
    "image_storage_type": "public",
    "image_alt_text": "Eset",
    "status": 1,
    "created_at": "2025-09-08T06:56:56.000000Z",
    "updated_at": "2025-09-08T07:31:26.000000Z",
    "image_full_url": {
      "key": "2025-09-08-68be864e9f87c.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-08-68be864e9f87c.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 73,
    "name": "AGL",
    "image": "2025-09-08-68be9be8e6192.webp",
    "image_storage_type": "public",
    "image_alt_text": "AGL",
    "status": 1,
    "created_at": "2025-09-08T08:49:38.000000Z",
    "updated_at": "2025-09-08T09:03:36.000000Z",
    "image_full_url": {
      "key": "2025-09-08-68be9be8e6192.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-08-68be9be8e6192.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 74,
    "name": "Synology",
    "image": "2025-09-25-68d4eaf5043b3.webp",
    "image_storage_type": "public",
    "image_alt_text": "Synology",
    "status": 1,
    "created_at": "2025-09-08T09:04:41.000000Z",
    "updated_at": "2025-09-25T07:10:45.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4eaf5043b3.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4eaf5043b3.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 75,
    "name": "Avonik",
    "image": "2025-09-08-68bea4ec4d024.webp",
    "image_storage_type": "public",
    "image_alt_text": "Avonik",
    "status": 1,
    "created_at": "2025-09-08T09:42:04.000000Z",
    "updated_at": "2025-09-08T09:42:04.000000Z",
    "image_full_url": {
      "key": "2025-09-08-68bea4ec4d024.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-08-68bea4ec4d024.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 76,
    "name": "Logitech",
    "image": "2025-09-08-68bea5a424a73.webp",
    "image_storage_type": "public",
    "image_alt_text": "Logitech",
    "status": 1,
    "created_at": "2025-09-08T09:45:08.000000Z",
    "updated_at": "2025-09-08T09:45:08.000000Z",
    "image_full_url": {
      "key": "2025-09-08-68bea5a424a73.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-08-68bea5a424a73.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 77,
    "name": "BenQ",
    "image": "2025-09-09-68bff81c176cd.webp",
    "image_storage_type": "public",
    "image_alt_text": "BenQ",
    "status": 1,
    "created_at": "2025-09-09T09:49:16.000000Z",
    "updated_at": "2025-09-09T09:49:16.000000Z",
    "image_full_url": {
      "key": "2025-09-09-68bff81c176cd.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-09-68bff81c176cd.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 78,
    "name": "Optoma",
    "image": "2025-09-09-68bff8af9fad7.webp",
    "image_storage_type": "public",
    "image_alt_text": "Optoma",
    "status": 1,
    "created_at": "2025-09-09T09:51:43.000000Z",
    "updated_at": "2025-09-09T09:51:43.000000Z",
    "image_full_url": {
      "key": "2025-09-09-68bff8af9fad7.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-09-68bff8af9fad7.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 79,
    "name": "Xiomi",
    "image": "2025-09-25-68d4ea0cc350c.webp",
    "image_storage_type": "public",
    "image_alt_text": "Xiomi",
    "status": 1,
    "created_at": "2025-09-09T09:57:35.000000Z",
    "updated_at": "2025-09-25T07:06:52.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4ea0cc350c.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4ea0cc350c.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 80,
    "name": "Atria",
    "image": "2025-09-10-68c12e4d55c45.webp",
    "image_storage_type": "public",
    "image_alt_text": "Atria",
    "status": 1,
    "created_at": "2025-09-10T07:52:45.000000Z",
    "updated_at": "2025-09-10T07:52:45.000000Z",
    "image_full_url": {
      "key": "2025-09-10-68c12e4d55c45.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-10-68c12e4d55c45.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 81,
    "name": "CZUR",
    "image": "2025-09-10-68c137b0c7291.webp",
    "image_storage_type": "public",
    "image_alt_text": "CZUR",
    "status": 1,
    "created_at": "2025-09-10T08:32:48.000000Z",
    "updated_at": "2025-09-10T08:32:48.000000Z",
    "image_full_url": {
      "key": "2025-09-10-68c137b0c7291.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-10-68c137b0c7291.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 82,
    "name": "Panasonic",
    "image": "2025-09-10-68c13cb66f284.webp",
    "image_storage_type": "public",
    "image_alt_text": "Panasonic",
    "status": 1,
    "created_at": "2025-09-10T08:54:14.000000Z",
    "updated_at": "2025-09-10T08:54:14.000000Z",
    "image_full_url": {
      "key": "2025-09-10-68c13cb66f284.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-10-68c13cb66f284.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 83,
    "name": "POWER TOUCH",
    "image": "2025-09-12-68c3dfdb65653.webp",
    "image_storage_type": "public",
    "image_alt_text": "POWER TOUCH",
    "status": 1,
    "created_at": "2025-09-10T10:29:19.000000Z",
    "updated_at": "2025-09-12T08:54:51.000000Z",
    "image_full_url": {
      "key": "2025-09-12-68c3dfdb65653.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-12-68c3dfdb65653.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 84,
    "name": "ViewBoard",
    "image": "2025-09-25-68d4eb3ddd6c7.webp",
    "image_storage_type": "public",
    "image_alt_text": "ViewBoard",
    "status": 1,
    "created_at": "2025-09-10T10:44:38.000000Z",
    "updated_at": "2025-09-25T07:11:57.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4eb3ddd6c7.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4eb3ddd6c7.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 85,
    "name": "E-Board",
    "image": "2025-09-10-68c158a2c12a8.webp",
    "image_storage_type": "public",
    "image_alt_text": "E-Board",
    "status": 1,
    "created_at": "2025-09-10T10:53:22.000000Z",
    "updated_at": "2025-09-10T10:53:22.000000Z",
    "image_full_url": {
      "key": "2025-09-10-68c158a2c12a8.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-10-68c158a2c12a8.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 86,
    "name": "HONOR",
    "image": "2025-09-15-68c7b79de92fa.webp",
    "image_storage_type": "public",
    "image_alt_text": "HONOR",
    "status": 1,
    "created_at": "2025-09-11T13:09:45.000000Z",
    "updated_at": "2025-09-15T06:52:13.000000Z",
    "image_full_url": {
      "key": "2025-09-15-68c7b79de92fa.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-15-68c7b79de92fa.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 87,
    "name": "Vivo",
    "image": "2025-09-25-68d4ebb659c2d.webp",
    "image_storage_type": "public",
    "image_alt_text": "Vivo",
    "status": 1,
    "created_at": "2025-09-11T16:10:11.000000Z",
    "updated_at": "2025-09-25T07:13:58.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4ebb659c2d.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4ebb659c2d.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 88,
    "name": "Tab",
    "image": "2025-09-25-68d4eb057813e.webp",
    "image_storage_type": "public",
    "image_alt_text": "Tab",
    "status": 1,
    "created_at": "2025-09-11T16:28:49.000000Z",
    "updated_at": "2025-09-25T07:11:01.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4eb057813e.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4eb057813e.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 89,
    "name": "POCO",
    "image": "2025-09-12-68c40bb7a780b.webp",
    "image_storage_type": "public",
    "image_alt_text": "POCO",
    "status": 1,
    "created_at": "2025-09-12T12:01:59.000000Z",
    "updated_at": "2025-09-12T12:01:59.000000Z",
    "image_full_url": {
      "key": "2025-09-12-68c40bb7a780b.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-12-68c40bb7a780b.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 90,
    "name": "ZTE BLADE",
    "image": "2025-09-25-68d4ea3bac5bb.webp",
    "image_storage_type": "public",
    "image_alt_text": "ZTE BLADE",
    "status": 1,
    "created_at": "2025-09-12T12:20:21.000000Z",
    "updated_at": "2025-09-25T07:07:39.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4ea3bac5bb.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4ea3bac5bb.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 91,
    "name": "OPPO",
    "image": "2025-09-15-68c7b744620e7.webp",
    "image_storage_type": "public",
    "image_alt_text": "OPPO",
    "status": 1,
    "created_at": "2025-09-12T12:23:00.000000Z",
    "updated_at": "2025-09-15T06:50:44.000000Z",
    "image_full_url": {
      "key": "2025-09-15-68c7b744620e7.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-15-68c7b744620e7.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 92,
    "name": "Tiandy",
    "image": "2025-09-25-68d4ea9fa0684.webp",
    "image_storage_type": "public",
    "image_alt_text": "Tiandy",
    "status": 1,
    "created_at": "2025-09-24T05:36:22.000000Z",
    "updated_at": "2025-09-25T07:09:19.000000Z",
    "image_full_url": {
      "key": "2025-09-25-68d4ea9fa0684.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-25-68d4ea9fa0684.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 93,
    "name": "VGR",
    "image": "2025-09-26-68d66e550000f.webp",
    "image_storage_type": "public",
    "image_alt_text": "VGR",
    "status": 1,
    "created_at": "2025-09-26T10:43:33.000000Z",
    "updated_at": "2025-09-26T10:43:33.000000Z",
    "image_full_url": {
      "key": "2025-09-26-68d66e550000f.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-26-68d66e550000f.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 94,
    "name": "Hikvision",
    "image": "2025-09-27-68d77e452c61f.webp",
    "image_storage_type": "public",
    "image_alt_text": "Hikvision",
    "status": 1,
    "created_at": "2025-09-27T06:03:49.000000Z",
    "updated_at": "2025-09-27T06:03:49.000000Z",
    "image_full_url": {
      "key": "2025-09-27-68d77e452c61f.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-27-68d77e452c61f.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 95,
    "name": "dahua",
    "image": "2025-09-27-68d77ef0b303a.webp",
    "image_storage_type": "public",
    "image_alt_text": "dahua",
    "status": 1,
    "created_at": "2025-09-27T06:06:40.000000Z",
    "updated_at": "2025-09-27T06:06:40.000000Z",
    "image_full_url": {
      "key": "2025-09-27-68d77ef0b303a.webp",
      "path": "https://api.venu.uz/storage/brand/2025-09-27-68d77ef0b303a.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 96,
    "name": "LB-LINK",
    "image": "2025-10-03-68df390e3b4b5.webp",
    "image_storage_type": "public",
    "image_alt_text": "LB-LINK",
    "status": 1,
    "created_at": "2025-10-03T02:46:38.000000Z",
    "updated_at": "2025-10-03T02:46:38.000000Z",
    "image_full_url": {
      "key": "2025-10-03-68df390e3b4b5.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-03-68df390e3b4b5.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 97,
    "name": "RTX",
    "image": "2025-10-03-68df3a22f1dc1.webp",
    "image_storage_type": "public",
    "image_alt_text": "RTX",
    "status": 1,
    "created_at": "2025-10-03T02:51:14.000000Z",
    "updated_at": "2025-10-03T02:51:14.000000Z",
    "image_full_url": {
      "key": "2025-10-03-68df3a22f1dc1.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-03-68df3a22f1dc1.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 98,
    "name": "ProLAN",
    "image": "2025-10-03-68df6e4f94c5e.webp",
    "image_storage_type": "public",
    "image_alt_text": "ProLAN",
    "status": 1,
    "created_at": "2025-10-03T06:33:51.000000Z",
    "updated_at": "2025-10-03T06:33:51.000000Z",
    "image_full_url": {
      "key": "2025-10-03-68df6e4f94c5e.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-03-68df6e4f94c5e.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 99,
    "name": "Ubiquiti",
    "image": "2025-10-03-68df84f0cd5d4.webp",
    "image_storage_type": "public",
    "image_alt_text": "Ubiquiti",
    "status": 1,
    "created_at": "2025-10-03T08:10:24.000000Z",
    "updated_at": "2025-10-03T08:10:24.000000Z",
    "image_full_url": {
      "key": "2025-10-03-68df84f0cd5d4.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-03-68df84f0cd5d4.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 100,
    "name": "Reyee",
    "image": "2025-10-03-68df8a8b808a1.webp",
    "image_storage_type": "public",
    "image_alt_text": "Reyee",
    "status": 1,
    "created_at": "2025-10-03T08:34:19.000000Z",
    "updated_at": "2025-10-03T08:34:19.000000Z",
    "image_full_url": {
      "key": "2025-10-03-68df8a8b808a1.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-03-68df8a8b808a1.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 101,
    "name": "MYPRO",
    "image": "2025-10-09-68e74bf8af172.webp",
    "image_storage_type": "public",
    "image_alt_text": "MYPRO",
    "status": 1,
    "created_at": "2025-10-09T05:45:28.000000Z",
    "updated_at": "2025-10-09T05:45:28.000000Z",
    "image_full_url": {
      "key": "2025-10-09-68e74bf8af172.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-09-68e74bf8af172.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 102,
    "name": "PROGAMING",
    "image": "2025-10-09-68e7559806e70.webp",
    "image_storage_type": "public",
    "image_alt_text": "PROGAMING",
    "status": 1,
    "created_at": "2025-10-09T06:26:32.000000Z",
    "updated_at": "2025-10-09T06:26:32.000000Z",
    "image_full_url": {
      "key": "2025-10-09-68e7559806e70.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-09-68e7559806e70.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 103,
    "name": "Plantronics",
    "image": "2025-10-10-68e8ebb503ac2.webp",
    "image_storage_type": "public",
    "image_alt_text": "Plantronics",
    "status": 1,
    "created_at": "2025-10-10T11:19:17.000000Z",
    "updated_at": "2025-10-10T11:19:17.000000Z",
    "image_full_url": {
      "key": "2025-10-10-68e8ebb503ac2.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-10-68e8ebb503ac2.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 104,
    "name": "Jabra",
    "image": "2025-10-10-68e8ef5e489a0.webp",
    "image_storage_type": "public",
    "image_alt_text": "Jabra",
    "status": 1,
    "created_at": "2025-10-10T11:34:54.000000Z",
    "updated_at": "2025-10-10T11:34:54.000000Z",
    "image_full_url": {
      "key": "2025-10-10-68e8ef5e489a0.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-10-68e8ef5e489a0.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 105,
    "name": "3KOM",
    "image": "2025-10-20-68f6032229d22.webp",
    "image_storage_type": "public",
    "image_alt_text": "3KOM",
    "status": 1,
    "created_at": "2025-10-20T09:38:42.000000Z",
    "updated_at": "2025-10-20T09:38:42.000000Z",
    "image_full_url": {
      "key": "2025-10-20-68f6032229d22.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-20-68f6032229d22.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 106,
    "name": "Fujitsu",
    "image": "2025-10-20-68f613a885b68.webp",
    "image_storage_type": "public",
    "image_alt_text": "Fujitsu",
    "status": 1,
    "created_at": "2025-10-20T10:49:12.000000Z",
    "updated_at": "2025-10-20T10:49:12.000000Z",
    "image_full_url": {
      "key": "2025-10-20-68f613a885b68.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-20-68f613a885b68.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 107,
    "name": "UPS",
    "image": "2025-10-20-68f624586b35e.webp",
    "image_storage_type": "public",
    "image_alt_text": "UPS",
    "status": 1,
    "created_at": "2025-10-20T12:00:24.000000Z",
    "updated_at": "2025-10-20T12:00:24.000000Z",
    "image_full_url": {
      "key": "2025-10-20-68f624586b35e.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-20-68f624586b35e.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 108,
    "name": "COFEM",
    "image": "2025-10-21-68f71e1d70cb9.webp",
    "image_storage_type": "public",
    "image_alt_text": "COFEM",
    "status": 1,
    "created_at": "2025-10-21T05:46:05.000000Z",
    "updated_at": "2025-10-21T05:46:05.000000Z",
    "image_full_url": {
      "key": "2025-10-21-68f71e1d70cb9.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-21-68f71e1d70cb9.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 109,
    "name": "KEMEI",
    "image": "2025-10-23-68f9c3285d204.webp",
    "image_storage_type": "public",
    "image_alt_text": "KEMEI",
    "status": 1,
    "created_at": "2025-10-23T05:54:48.000000Z",
    "updated_at": "2025-10-23T05:54:48.000000Z",
    "image_full_url": {
      "key": "2025-10-23-68f9c3285d204.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-23-68f9c3285d204.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 110,
    "name": "Demix",
    "image": "2025-10-23-68f9cf5b76777.webp",
    "image_storage_type": "public",
    "image_alt_text": "Demix",
    "status": 1,
    "created_at": "2025-10-23T06:46:51.000000Z",
    "updated_at": "2025-10-23T06:46:51.000000Z",
    "image_full_url": {
      "key": "2025-10-23-68f9cf5b76777.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-23-68f9cf5b76777.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 111,
    "name": "AOC",
    "image": "2025-10-23-68fa01dd85402.webp",
    "image_storage_type": "public",
    "image_alt_text": "AOC",
    "status": 1,
    "created_at": "2025-10-23T10:22:21.000000Z",
    "updated_at": "2025-10-23T10:22:21.000000Z",
    "image_full_url": {
      "key": "2025-10-23-68fa01dd85402.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-23-68fa01dd85402.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 112,
    "name": "AVTECH",
    "image": "2025-10-23-68fa02a3b3e9f.webp",
    "image_storage_type": "public",
    "image_alt_text": "AVTECH",
    "status": 1,
    "created_at": "2025-10-23T10:25:39.000000Z",
    "updated_at": "2025-10-23T10:25:39.000000Z",
    "image_full_url": {
      "key": "2025-10-23-68fa02a3b3e9f.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-23-68fa02a3b3e9f.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 113,
    "name": "Viewsonic",
    "image": "2025-10-23-68fa04419b402.webp",
    "image_storage_type": "public",
    "image_alt_text": "Viewsonic",
    "status": 1,
    "created_at": "2025-10-23T10:32:33.000000Z",
    "updated_at": "2025-10-23T10:32:33.000000Z",
    "image_full_url": {
      "key": "2025-10-23-68fa04419b402.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-23-68fa04419b402.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 114,
    "name": "Philips",
    "image": "2025-10-23-68fa04a763cdc.webp",
    "image_storage_type": "public",
    "image_alt_text": "Philips",
    "status": 1,
    "created_at": "2025-10-23T10:34:15.000000Z",
    "updated_at": "2025-10-23T10:34:15.000000Z",
    "image_full_url": {
      "key": "2025-10-23-68fa04a763cdc.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-23-68fa04a763cdc.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 115,
    "name": "Vesta",
    "image": "2025-10-23-68fa05be1f0e8.webp",
    "image_storage_type": "public",
    "image_alt_text": "vesta",
    "status": 1,
    "created_at": "2025-10-23T10:38:54.000000Z",
    "updated_at": "2025-10-23T10:38:54.000000Z",
    "image_full_url": {
      "key": "2025-10-23-68fa05be1f0e8.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-23-68fa05be1f0e8.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 116,
    "name": "Immer",
    "image": "2025-10-23-68fa0645c852d.webp",
    "image_storage_type": "public",
    "image_alt_text": "Immer",
    "status": 1,
    "created_at": "2025-10-23T10:41:09.000000Z",
    "updated_at": "2025-10-23T10:41:09.000000Z",
    "image_full_url": {
      "key": "2025-10-23-68fa0645c852d.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-23-68fa0645c852d.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 117,
    "name": "AMD",
    "image": "2025-10-26-68fd863fb0518.webp",
    "image_storage_type": "public",
    "image_alt_text": "AMD",
    "status": 1,
    "created_at": "2025-10-26T02:23:59.000000Z",
    "updated_at": "2025-10-26T02:23:59.000000Z",
    "image_full_url": {
      "key": "2025-10-26-68fd863fb0518.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-26-68fd863fb0518.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 118,
    "name": "HPE",
    "image": "2025-10-26-68fd86c4439b5.webp",
    "image_storage_type": "public",
    "image_alt_text": "HPE",
    "status": 1,
    "created_at": "2025-10-26T02:26:12.000000Z",
    "updated_at": "2025-10-26T02:26:12.000000Z",
    "image_full_url": {
      "key": "2025-10-26-68fd86c4439b5.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-26-68fd86c4439b5.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 119,
    "name": "Micron",
    "image": "2025-10-26-68fd879169dcf.webp",
    "image_storage_type": "public",
    "image_alt_text": "Micron",
    "status": 1,
    "created_at": "2025-10-26T02:29:37.000000Z",
    "updated_at": "2025-10-26T02:29:37.000000Z",
    "image_full_url": {
      "key": "2025-10-26-68fd879169dcf.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-26-68fd879169dcf.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 120,
    "name": "QNAP",
    "image": "2025-10-27-68fece1858743.webp",
    "image_storage_type": "public",
    "image_alt_text": "QNAP",
    "status": 1,
    "created_at": "2025-10-27T01:42:48.000000Z",
    "updated_at": "2025-10-27T01:42:48.000000Z",
    "image_full_url": {
      "key": "2025-10-27-68fece1858743.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-27-68fece1858743.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 121,
    "name": "Apacer",
    "image": "2025-10-27-68fece5722d84.webp",
    "image_storage_type": "public",
    "image_alt_text": "Apacer",
    "status": 1,
    "created_at": "2025-10-27T01:43:51.000000Z",
    "updated_at": "2025-10-27T01:43:51.000000Z",
    "image_full_url": {
      "key": "2025-10-27-68fece5722d84.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-27-68fece5722d84.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 122,
    "name": "Ballistix",
    "image": "2025-10-27-68fecf5a02c35.gif",
    "image_storage_type": "public",
    "image_alt_text": "Ballistix",
    "status": 1,
    "created_at": "2025-10-27T01:48:10.000000Z",
    "updated_at": "2025-10-27T01:48:10.000000Z",
    "image_full_url": {
      "key": "2025-10-27-68fecf5a02c35.gif",
      "path": "https://api.venu.uz/storage/brand/2025-10-27-68fecf5a02c35.gif",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 123,
    "name": "HyperX",
    "image": "2025-10-27-68fed04ec0afb.webp",
    "image_storage_type": "public",
    "image_alt_text": "HyperX",
    "status": 1,
    "created_at": "2025-10-27T01:52:14.000000Z",
    "updated_at": "2025-10-27T01:52:14.000000Z",
    "image_full_url": {
      "key": "2025-10-27-68fed04ec0afb.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-27-68fed04ec0afb.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 124,
    "name": "CORSAIR",
    "image": "2025-10-27-68fed0e388cfe.webp",
    "image_storage_type": "public",
    "image_alt_text": "CORSAIR",
    "status": 1,
    "created_at": "2025-10-27T01:54:43.000000Z",
    "updated_at": "2025-10-27T01:54:43.000000Z",
    "image_full_url": {
      "key": "2025-10-27-68fed0e388cfe.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-27-68fed0e388cfe.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 125,
    "name": "Palit",
    "image": "2025-10-28-6900734b4bb2c.webp",
    "image_storage_type": "public",
    "image_alt_text": "Palit",
    "status": 1,
    "created_at": "2025-10-28T07:39:55.000000Z",
    "updated_at": "2025-10-28T07:39:55.000000Z",
    "image_full_url": {
      "key": "2025-10-28-6900734b4bb2c.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-28-6900734b4bb2c.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 126,
    "name": "COUGAR",
    "image": "2025-10-28-690099ef94ad7.webp",
    "image_storage_type": "public",
    "image_alt_text": "COUGAR",
    "status": 1,
    "created_at": "2025-10-28T10:24:47.000000Z",
    "updated_at": "2025-10-28T10:24:47.000000Z",
    "image_full_url": {
      "key": "2025-10-28-690099ef94ad7.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-28-690099ef94ad7.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 127,
    "name": "HuntKey",
    "image": "2025-10-28-69009a3488fd0.webp",
    "image_storage_type": "public",
    "image_alt_text": "HuntKey",
    "status": 1,
    "created_at": "2025-10-28T10:25:56.000000Z",
    "updated_at": "2025-10-28T10:25:56.000000Z",
    "image_full_url": {
      "key": "2025-10-28-69009a3488fd0.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-28-69009a3488fd0.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 128,
    "name": "Aerocool",
    "image": "2025-10-28-69009ad51cac6.webp",
    "image_storage_type": "public",
    "image_alt_text": "Aerocool",
    "status": 1,
    "created_at": "2025-10-28T10:28:37.000000Z",
    "updated_at": "2025-10-28T10:28:37.000000Z",
    "image_full_url": {
      "key": "2025-10-28-69009ad51cac6.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-28-69009ad51cac6.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 129,
    "name": "Gamemax",
    "image": "2025-10-28-69009c041a252.webp",
    "image_storage_type": "public",
    "image_alt_text": "Gamemax",
    "status": 1,
    "created_at": "2025-10-28T10:33:40.000000Z",
    "updated_at": "2025-10-28T10:33:40.000000Z",
    "image_full_url": {
      "key": "2025-10-28-69009c041a252.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-28-69009c041a252.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 130,
    "name": "Zalman",
    "image": "2025-10-28-69009c7462010.webp",
    "image_storage_type": "public",
    "image_alt_text": "Zalman",
    "status": 1,
    "created_at": "2025-10-28T10:35:32.000000Z",
    "updated_at": "2025-10-28T10:35:32.000000Z",
    "image_full_url": {
      "key": "2025-10-28-69009c7462010.webp",
      "path": "https://api.venu.uz/storage/brand/2025-10-28-69009c7462010.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 131,
    "name": "AORUS",
    "image": "2025-11-06-690c34bfb3354.webp",
    "image_storage_type": "public",
    "image_alt_text": "AORUS",
    "status": 1,
    "created_at": "2025-11-06T05:40:15.000000Z",
    "updated_at": "2025-11-06T05:40:15.000000Z",
    "image_full_url": {
      "key": "2025-11-06-690c34bfb3354.webp",
      "path": "https://api.venu.uz/storage/brand/2025-11-06-690c34bfb3354.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 132,
    "name": "PREMIER",
    "image": "2025-11-07-690d9dfea6388.webp",
    "image_storage_type": "public",
    "image_alt_text": "PREMIER",
    "status": 1,
    "created_at": "2025-11-07T07:21:34.000000Z",
    "updated_at": "2025-11-07T07:21:34.000000Z",
    "image_full_url": {
      "key": "2025-11-07-690d9dfea6388.webp",
      "path": "https://api.venu.uz/storage/brand/2025-11-07-690d9dfea6388.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 133,
    "name": "CHAIRMAN",
    "image": "2025-11-11-6912cdff463ca.webp",
    "image_storage_type": "public",
    "image_alt_text": "CHAIRMAN",
    "status": 1,
    "created_at": "2025-11-11T05:47:43.000000Z",
    "updated_at": "2025-11-11T05:47:43.000000Z",
    "image_full_url": {
      "key": "2025-11-11-6912cdff463ca.webp",
      "path": "https://api.venu.uz/storage/brand/2025-11-11-6912cdff463ca.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 134,
    "name": "TP-LINK",
    "image": "2025-11-12-69141c297cc75.webp",
    "image_storage_type": "public",
    "image_alt_text": "TP-LINK",
    "status": 1,
    "created_at": "2025-11-12T05:33:29.000000Z",
    "updated_at": "2025-11-12T05:33:29.000000Z",
    "image_full_url": {
      "key": "2025-11-12-69141c297cc75.webp",
      "path": "https://api.venu.uz/storage/brand/2025-11-12-69141c297cc75.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 135,
    "name": "RXGAMER",
    "image": "2025-11-13-691586bae2981.webp",
    "image_storage_type": "public",
    "image_alt_text": "RXGAMER",
    "status": 1,
    "created_at": "2025-11-13T07:20:26.000000Z",
    "updated_at": "2025-11-13T07:20:26.000000Z",
    "image_full_url": {
      "key": "2025-11-13-691586bae2981.webp",
      "path": "https://api.venu.uz/storage/brand/2025-11-13-691586bae2981.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 136,
    "name": "Zebra",
    "image": "2025-12-03-692ff251313fc.webp",
    "image_storage_type": "public",
    "image_alt_text": "Zebra",
    "status": 1,
    "created_at": "2025-12-03T08:18:25.000000Z",
    "updated_at": "2025-12-03T08:18:25.000000Z",
    "image_full_url": {
      "key": "2025-12-03-692ff251313fc.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-03-692ff251313fc.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 137,
    "name": "CADDY",
    "image": "2025-12-03-69301131a0f3e.webp",
    "image_storage_type": "public",
    "image_alt_text": "CADDY",
    "status": 1,
    "created_at": "2025-12-03T10:30:09.000000Z",
    "updated_at": "2025-12-03T10:30:09.000000Z",
    "image_full_url": {
      "key": "2025-12-03-69301131a0f3e.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-03-69301131a0f3e.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 138,
    "name": "mytech",
    "image": "2025-12-05-69327262d4048.webp",
    "image_storage_type": "public",
    "image_alt_text": "mytech",
    "status": 1,
    "created_at": "2025-12-05T05:49:22.000000Z",
    "updated_at": "2025-12-05T05:49:22.000000Z",
    "image_full_url": {
      "key": "2025-12-05-69327262d4048.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-05-69327262d4048.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 139,
    "name": "Fanvil",
    "image": "2025-12-11-693a6a2eaab21.webp",
    "image_storage_type": "public",
    "image_alt_text": "Fanvil",
    "status": 1,
    "created_at": "2025-12-11T06:52:30.000000Z",
    "updated_at": "2025-12-11T06:52:30.000000Z",
    "image_full_url": {
      "key": "2025-12-11-693a6a2eaab21.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-11-693a6a2eaab21.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 140,
    "name": "MikroTik",
    "image": "2025-12-11-693aa5fc690bd.webp",
    "image_storage_type": "public",
    "image_alt_text": "MikroTik",
    "status": 1,
    "created_at": "2025-12-11T11:07:40.000000Z",
    "updated_at": "2025-12-11T11:07:40.000000Z",
    "image_full_url": {
      "key": "2025-12-11-693aa5fc690bd.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-11-693aa5fc690bd.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 141,
    "name": "Mercusys",
    "image": "2025-12-18-6943bb7c947d0.webp",
    "image_storage_type": "public",
    "image_alt_text": "Mercusys",
    "status": 1,
    "created_at": "2025-12-18T08:29:48.000000Z",
    "updated_at": "2025-12-18T08:29:48.000000Z",
    "image_full_url": {
      "key": "2025-12-18-6943bb7c947d0.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-18-6943bb7c947d0.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 142,
    "name": "Belkin",
    "image": "2025-12-18-6943c37b2e269.webp",
    "image_storage_type": "public",
    "image_alt_text": "Belkin",
    "status": 1,
    "created_at": "2025-12-18T09:03:55.000000Z",
    "updated_at": "2025-12-18T09:03:55.000000Z",
    "image_full_url": {
      "key": "2025-12-18-6943c37b2e269.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-18-6943c37b2e269.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 143,
    "name": "Tenda",
    "image": "2025-12-18-6943c4f07860e.webp",
    "image_storage_type": "public",
    "image_alt_text": "Tenda",
    "status": 1,
    "created_at": "2025-12-18T09:10:08.000000Z",
    "updated_at": "2025-12-18T09:10:08.000000Z",
    "image_full_url": {
      "key": "2025-12-18-6943c4f07860e.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-18-6943c4f07860e.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 144,
    "name": "Zyxel",
    "image": "2025-12-18-6943c627c6cec.webp",
    "image_storage_type": "public",
    "image_alt_text": "Zyxel",
    "status": 1,
    "created_at": "2025-12-18T09:15:19.000000Z",
    "updated_at": "2025-12-18T09:15:19.000000Z",
    "image_full_url": {
      "key": "2025-12-18-6943c627c6cec.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-18-6943c627c6cec.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 145,
    "name": "SNR",
    "image": "2025-12-18-6943dfa01b900.webp",
    "image_storage_type": "public",
    "image_alt_text": "SNR",
    "status": 1,
    "created_at": "2025-12-18T11:04:00.000000Z",
    "updated_at": "2025-12-18T11:04:00.000000Z",
    "image_full_url": {
      "key": "2025-12-18-6943dfa01b900.webp",
      "path": null,
      "status": 404
    },
    "translations": []
  },
  {
    "id": 146,
    "name": "Max Power",
    "image": "2025-12-19-6944fb2ac0245.webp",
    "image_storage_type": "public",
    "image_alt_text": "Max Power",
    "status": 1,
    "created_at": "2025-12-19T07:13:46.000000Z",
    "updated_at": "2025-12-19T07:13:46.000000Z",
    "image_full_url": {
      "key": "2025-12-19-6944fb2ac0245.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-19-6944fb2ac0245.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 147,
    "name": "FP Mark",
    "image": "2025-12-19-69453456de3de.webp",
    "image_storage_type": "public",
    "image_alt_text": "FP Mark",
    "status": 1,
    "created_at": "2025-12-19T11:17:42.000000Z",
    "updated_at": "2025-12-19T11:17:42.000000Z",
    "image_full_url": {
      "key": "2025-12-19-69453456de3de.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-19-69453456de3de.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 148,
    "name": "Eurolan",
    "image": "2025-12-22-6948da7b96a48.webp",
    "image_storage_type": "public",
    "image_alt_text": "Eurolan",
    "status": 1,
    "created_at": "2025-12-22T05:43:23.000000Z",
    "updated_at": "2025-12-22T05:43:23.000000Z",
    "image_full_url": {
      "key": "2025-12-22-6948da7b96a48.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-22-6948da7b96a48.webp",
      "status": 200
    },
    "translations": []
  },
  {
    "id": 149,
    "name": "SONOFF",
    "image": "2025-12-22-6948efec78220.webp",
    "image_storage_type": "public",
    "image_alt_text": "SONOFF",
    "status": 1,
    "created_at": "2025-12-22T07:14:52.000000Z",
    "updated_at": "2025-12-22T07:14:52.000000Z",
    "image_full_url": {
      "key": "2025-12-22-6948efec78220.webp",
      "path": "https://api.venu.uz/storage/brand/2025-12-22-6948efec78220.webp",
      "status": 200
    },
    "translations": []
  }
]


============ Tayyor ma'lumotlarni bazaga yuborish =====================
1. Rasimlarni yuklash
Method: POST
URL
https://api.venu.uz/api/v3/seller/products/upload-images
Headers
accept-encoding:
gzip
authorization:
Bearer mk8l2eh6GM5yICFv1mCrheNfbC1H8QqOJAIt8IsKN8deGUilsa
content-length:
4341
content-type:
multipart/form-data; boundary=dart-http-boundary-dwbGPJCk059.JTr-col-DnArMTLzo9Ds2CwlJ7FcPKLcVYZ0H.i
host:
api.venu.uz
user-agent:
Dart/3.10 (dart:io)

Request Body
--dart-http-boundary-dwbGPJCk059.JTr-col-DnArMTLzo9Ds2CwlJ7FcPKLcVYZ0H.icontent-disposition: form-data;name="type"thumbnail--dart-http-boundary-dwbGPJCk059.JTr-col-DnArMTLzo9Ds2CwlJ7FcPKLcVYZ0H.icontent-disposition: form-data;name="color"content-type: text/plain;charset=utf-8content-transfer-encoding: binary--dart-http-boundary-dwbGPJCk059.JTr-col-DnArMTLzo9Ds2CwlJ7FcPKLcVYZ0H.icontent-disposition: form-data;name="colors_active"
false--dart-http-boundary-dwbGPJCk059.JTr-col-DnArMTLzo9Ds2CwlJ7FcPKLcVYZ0H.icontent-type: application/octet-streamcontent-disposition: form-data;name="image";filename="yn.png"�PNG

1. product joylash
Method: POST
URL
https://api.venu.uz/api/v3/seller/products/add
Headers
accept-encoding:
gzip
authorization:
Bearer mk8l2eh6GM5yICFv1mCrheNfbC1H8QqOJAIt8IsKN8deGUilsa
content-length:
1116
content-type:
application/json; charset=UTF-8
host:
api.venu.uz
user-agent:
Dart/3.10 (dart:io)

Request Body:
{
  "name": "[\"testttt\"]",
  "description": "[\"test\"]",
  "unit_price": 0.007874015748031496,
  "discount": 12.0,
  "discount_type": "percent",
  "tax_ids": "[]",
  "tax_model": "exclude",
  "category_id": "424",
  "unit": "pc",
  "brand_id": 7,
  "meta_title": "testttt",
  "meta_description": "",
  "lang": "[\"ru\"]",
  "colors": "[]",
  "images": "[{\"image_name\":\"2026-01-12-6964bf91929c1.webp\",\"storage\":\"public\"}]",
  "thumbnail": "2026-01-12-6964bf90339e6.webp",
  "colors_active": false,
  "video_url": "",
  "meta_image": "2026-01-12-6964bf90d58e9.webp",
  "current_stock": 10,
  "shipping_cost": 0.0,
  "multiply_qty": 0,
  "code": "TYDKVR",
  "minimum_order_qty": 1,
  "product_type": "physical",
  "digital_product_type": "ready_after_sell",
  "digital_file_ready": "",
  "tags": "[\"tag\",\"name\"]",
  "publishing_house": "[]",
  "authors": "[]",
  "color_image": "[]",
  "meta_index": "1",
  "meta_no_follow": "",
  "meta_no_image_index": "0",
  "meta_no_archive": "0",
  "meta_no_snippet": "0",
  "meta_max_snippet": "0",
  "meta_max_snippet_value": null,
  "meta_max_video_preview": "0",
  "meta_max_video_preview_value": null,
  "meta_max_image_preview": "0",
  "meta_max_image_preview_value": "large",
  "sub_category_id": "600",
  "sub_sub_category_id": "601",
  "tax": "0"
}
Response Success:
{"message":"Successfully product added!","request":{"name":"[\"test p\"]","description":"[\"description\"]","unit_price":0.007874015748031496,"discount":12,"discount_type":"percent","tax_ids":"[]","tax_model":"exclude","category_id":"592","unit":"pc","brand_id":6,"meta_title":"test p","meta_description":"cdcsd","lang":"[\"ru\"]","colors":"[]","images":"[{\"image_name\":\"2026-01-12-69649cbb37b30.webp\",\"storage\":\"public\"}]","thumbnail":"2026-01-12-69649cb95e0f0.webp","colors_active":false,"video_url":null,"meta_image":"2026-01-12-69649cba41cc5.webp","current_stock":1,"shipping_cost":0,"multiply_qty":0,"code":"0PI8KA","minimum_order_qty":1,"product_type":"physical","digital_product_type":"ready_after_sell","digital_file_ready":null,"tags":"[\"tag\",\"name\"]","publishing_house":"[]","authors":"[]","color_image":"[]","meta_index":"1","meta_no_follow":null,"meta_no_image_index":"0","meta_no_archive":"0","meta_no_snippet":"0","meta_max_snippet":"0","tax":"0","meta_max_snippet_value":null,"meta_max_video_preview":"0","meta_max_video_preview_value":null,"meta_max_image_preview":"0","meta_max_image_preview_value":"large","sub_category_id":"593","sub_sub_category_id":"594","seller":{"id":35,"f_name":"dewqrghfwjs","l_name":"e3rgtewr","phone":"+998930836787","image":"2026-01-11-6963a50c299f5.webp","email":"themodestn@venu.uz","password":"$2y$10$iDMPPG4hVt\/7QSwb8srxCeXZbfepiEgWJLfIwNVQj7ssOhNx3W1Yy","status":"approved","remember_token":null,"created_at":"2026-01-11T13:26:36.000000Z","updated_at":"2026-01-12T09:27:08.000000Z","bank_name":null,"branch":null,"account_no":null,"holder_name":null,"auth_token":"mk8l2eh6GM5yICFv1mCrheNfbC1H8QqOJAIt8IsKN8deGUilsa","sales_commission_percentage":null,"gst":null,"cm_firebase_token":"eZoQaGlYRsSs1Lhwpo-W5v:APA91bHksCWO0GrglijcbRWRLEFheZ0qD6wM8Riy-d3bltqOAdcZTT_a-tvpAYG4h5Zio85yVW7POQzVLdCTtC51fVfBzbBsvGnQSrCy0H2whLVcftTxaro","pos_status":0,"minimum_order_amount":0,"free_delivery_status":0,"free_delivery_over_amount":0,"app_language":"en","vat_percent":12,"inn":0,"image_full_url":{"key":"2026-01-11-6963a50c299f5.webp","path":"https:\/\/api.venu.uz\/storage\/seller\/2026-01-11-6963a50c299f5.webp","status":200},"storage":[{"id":7613,"data_type":"App\\Models\\Seller","data_id":"35","key":"image","value":"public","created_at":"2026-01-11T13:26:36.000000Z","updated_at":"2026-01-11T13:26:36.000000Z"}]}}}

Response error:{
  "errors": [
    {
      "code": "tax",
      "message": "The tax field is required."
    }
  ]
}

```

### Fayl: `api_models.py`
```py
"""FastAPI request/response models."""

from typing import List, Optional

from pydantic import BaseModel, Field

from agent.product.schemas import ProductGenSchema


class ProductGenerateRequest(BaseModel):
    """Request model for product generation."""

    name: str = Field(..., description="Product name (in Russian)", min_length=1)
    brand: str = Field(..., description="Product brand", min_length=1)
    price: int = Field(..., ge=0, description="Product price")
    stock: Optional[int] = Field(default=5, ge=0, description="Product stock quantity")
    # Note: Images are automatically generated by AI agent, not requested from user


class ProductGenerateResponse(BaseModel):
    """Response model for product generation."""

    name: str = Field(..., description="Product name in Russian")
    description: str = Field(..., description="Product description in Russian")
    meta_title: str = Field(..., description="Meta title in Russian")
    meta_description: str = Field(..., description="Meta description in Russian")
    tags: List[str]
    price: int
    stock: int
    shop_saved: Optional[bool] = Field(
        default=None, description="Do'konga saqlanganmi?"
    )
    shop_response: Optional[dict] = Field(default=None, description="Do'kon API javobi")

    @classmethod
    def from_schema(
        cls,
        schema: ProductGenSchema,
        shop_saved: Optional[bool] = None,
        shop_response: Optional[dict] = None,
    ) -> "ProductGenerateResponse":
        """Create response from ProductGenSchema."""
        return cls(
            name=schema.name,
            description=schema.description,
            meta_title=schema.meta_title,
            meta_description=schema.meta_description,
            tags=schema.tags,
            price=schema.price,
            stock=schema.stock,
            shop_saved=shop_saved,
            shop_response=shop_response,
        )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")

```

### Fayl: `test.py`
```py

```

### Fayl: `utils/logging_config.py`
```py
"""Logging configuration."""
import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    format_string: Optional[str] = None,
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True,  # Override any existing configuration
    )


```

### Fayl: `utils/__init__.py`
```py
"""Utility functions."""
from utils.logging_config import setup_logging

__all__ = ["setup_logging"]


```

### Fayl: `api/venu_api.py`
```py
"""Venu Seller API client."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from core.config import settings
from core.constants import (
    DEFAULT_DISCOUNT,
    DEFAULT_DISCOUNT_TYPE,
    DEFAULT_SUB_CATEGORY_ID,
    DEFAULT_SUB_SUB_CATEGORY_ID,
    DEFAULT_UNIT,
)

logger = logging.getLogger(__name__)


class VenuAPIError(Exception):
    """Base exception for Venu API errors."""

    pass


class VenuSellerAPI:
    """Client for Venu Seller API."""

    BASE_URL = settings.venu_base_url

    def __init__(self, email: str, password: str):
        """
        Initialize Venu Seller API client.

        Args:
            email: Seller email
            password: Seller password
        """
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.token: Optional[str] = None

        # Standard headers
        self.session.headers.update(
            {
                "user-agent": "Dart/3.10 (dart:io)",
                "accept-encoding": "gzip",
                "lang": "en",
            }
        )

    def login(self) -> bool:
        """
        Authenticate and obtain access token.

        Returns:
            bool: True if login successful, False otherwise
        """
        url = f"{self.BASE_URL}/api/v3/seller/auth/login"
        payload = {"email": self.email, "password": self.password}

        # Temporary bearer token for login (from API documentation)
        # Default token should be moved to constants or environment variable
        default_temp_token = "mPzVh43jap7LOAy9bX8TwGdzj2eTxNOBq4DS3xhV7U4P8McxjC"
        temp_token = settings.venu_temp_token or default_temp_token
        temp_headers = {"authorization": f"Bearer {temp_token}"}

        try:
            response = self.session.post(url, json=payload, headers=temp_headers)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("token")

            if not self.token:
                logger.error("Login successful but no token received")
                return False

            # Set token for subsequent requests
            self.session.headers.update({"authorization": f"Bearer {self.token}"})
            logger.info("Successfully logged in to Venu API")
            return True
        except requests.exceptions.HTTPError as e:
            logger.error(f"Login HTTP error (status {e.response.status_code}): {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Login request error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected login error: {e}", exc_info=True)
            return False

    def upload_image(
        self, file_path: str, image_type: str = "product"
    ) -> Optional[str]:
        """
        Upload image to server.

        Args:
            file_path: Path to image file
            image_type: Type of image ('thumbnail' or 'product')

        Returns:
            Optional[str]: Image name returned by server, or None if failed
        """
        if not self.token:
            logger.error("Not authenticated. Please login first.")
            return None

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            logger.error(f"File not found: {file_path}")
            return None

        url = f"{self.BASE_URL}/api/v3/seller/products/upload-images"

        headers = {
            "authorization": f"Bearer {self.token}",
            "user-agent": "Dart/3.10 (dart:io)",
        }

        try:
            # Determine MIME type
            mime_type = self._get_mime_type(file_path_obj.suffix)

            with open(file_path, "rb") as img_file:
                files = [("image", (file_path_obj.name, img_file, mime_type))]
                data = {"type": image_type, "colors_active": "false", "color": ""}

                response = requests.post(url, headers=headers, files=files, data=data)
                response.raise_for_status()
                res_data = response.json()

                image_name = res_data.get("image_name")
                if image_name:
                    logger.info(f"Image uploaded successfully: {image_name}")
                else:
                    logger.warning(
                        f"Upload successful but no image_name in response: {res_data}"
                    )
                return image_name
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Image upload HTTP error (status {e.response.status_code}): {e}"
            )
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Image upload request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected image upload error: {e}", exc_info=True)
            return None

    @staticmethod
    def _get_mime_type(file_extension: str) -> str:
        """
        Get MIME type from file extension.

        Args:
            file_extension: File extension (e.g., '.png', '.jpg')

        Returns:
            str: MIME type
        """
        extension_lower = file_extension.lower()
        if extension_lower in [".jpg", ".jpeg"]:
            return "image/jpeg"
        elif extension_lower == ".webp":
            return "image/webp"
        else:
            return "image/png"

    def get_categories(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all categories with subcategories.

        Returns:
            Optional[List[Dict]]: List of categories with nested structure, or None if failed
        """
        if not self.token:
            logger.error("Not authenticated. Please login first.")
            return None

        url = f"{self.BASE_URL}/api/v3/seller/categories"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            categories = response.json()
            logger.info(f"Successfully fetched {len(categories)} categories")
            return categories
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error fetching categories (status {e.response.status_code}): {e}"
            )
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching categories: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching categories: {e}", exc_info=True)
            return None

    def get_brands(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get all brands.

        Returns:
            Optional[List[Dict]]: List of brands, or None if failed
        """
        if not self.token:
            logger.error("Not authenticated. Please login first.")
            return None

        url = f"{self.BASE_URL}/api/v3/seller/brands"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            brands = response.json()
            logger.info(f"Successfully fetched {len(brands)} brands")
            return brands
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error fetching brands (status {e.response.status_code}): {e}"
            )
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching brands: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching brands: {e}", exc_info=True)
            return None

    def add_product(
        self,
        name: str,
        description: str,
        meta_image: str,
        meta_title: str,
        meta_description: str,
        tags: List[str],
        price: float,
        category_id: str,
        brand_id: int,
        main_image_path: str,
        additional_images_paths: List[str] = None,
        stock: int = 10,
        sub_category_id: Optional[str] = None,
        sub_sub_category_id: Optional[str] = None,
        unit: str = DEFAULT_UNIT,
        discount: float = DEFAULT_DISCOUNT,
        discount_type: str = DEFAULT_DISCOUNT_TYPE,
    ) -> Dict[str, Any]:
        """
        Add product with uploaded images.

        Args:
            name: Product name
            description: Product description
            meta_image: Meta image path/name
            meta_title: Meta title
            meta_description: Meta description
            tags: List of tags
            price: Product price
            category_id: Category ID
            brand_id: Brand ID
            main_image_path: Path to main/thumbnail image
            additional_images_paths: List of additional image paths
            stock: Stock quantity
            sub_category_id: Sub-category ID (default: from constants)
            sub_sub_category_id: Sub-sub-category ID (default: from constants)
            unit: Product unit (default: from constants)
            discount: Discount amount (default: from constants)
            discount_type: Discount type (default: from constants)

        Returns:
            Dict: API response
        """
        if not self.token:
            logger.error("Not authenticated. Please login first.")
            return {"status": "error", "message": "Not authenticated"}

        if additional_images_paths is None:
            additional_images_paths = []

        # A. Upload thumbnail
        thumb_name = self.upload_image(main_image_path, "thumbnail")
        if not thumb_name:
            return {"status": "error", "message": "Failed to upload thumbnail"}

        # B. Upload gallery images
        gallery_images = []
        # Add thumbnail to gallery first (API requirement)
        gallery_images.append({"image_name": thumb_name, "storage": "public"})

        for img_path in additional_images_paths:
            img_name = self.upload_image(img_path, "product")
            if img_name:
                gallery_images.append({"image_name": img_name, "storage": "public"})

        payload = {
            "name": json.dumps([name]),
            "description": json.dumps([description]),
            "unit_price": price,
            "discount": discount,
            "discount_type": discount_type,
            "tax_ids": "[]",
            "tax_model": "exclude",
            "category_id": category_id,
            "unit": unit,
            "brand_id": brand_id,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "lang": json.dumps(["ru"]),
            "colors": "[]",
            "images": json.dumps(gallery_images),
            "thumbnail": thumb_name,
            "colors_active": False,
            "video_url": "",
            "meta_image": meta_image,
            "current_stock": stock,
            "shipping_cost": 0.0,
            "multiply_qty": 0,
            "code": os.urandom(3).hex().upper(),
            "minimum_order_qty": 1,
            "product_type": "physical",
            "digital_product_type": "ready_after_sell",
            "digital_file_ready": "",
            "tags": json.dumps(tags),
            "publishing_house": "[]",
            "authors": "[]",
            "color_image": "[]",
            "meta_index": "1",
            "meta_no_follow": "",
            "meta_no_image_index": "0",
            "meta_no_archive": "0",
            "meta_no_snippet": "0",
            "meta_max_snippet": "0",
            "meta_max_snippet_value": None,
            "meta_max_video_preview": "0",
            "meta_max_video_preview_value": None,
            "meta_max_image_preview": "0",
            "meta_max_image_preview_value": "large",
            "sub_category_id": sub_category_id or DEFAULT_SUB_CATEGORY_ID,
            "sub_sub_category_id": sub_sub_category_id or DEFAULT_SUB_SUB_CATEGORY_ID,
            "tax": "0",
        }

        url = f"{self.BASE_URL}/api/v3/seller/products/add"
        try:
            response = self.session.post(url, json=payload)
            result = response.json()

            if response.status_code == 200:
                logger.info(f"Product added successfully: {name}")
            else:
                logger.error(
                    f"Product add error (status {response.status_code}): {result}"
                )

            return result
        except requests.exceptions.HTTPError as e:
            error_msg = f"Product add HTTP error (status {e.response.status_code}): {e}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        except requests.exceptions.RequestException as e:
            error_msg = f"Product add request error: {e}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        except Exception as e:
            error_msg = f"Unexpected product add error: {e}"
            logger.error(error_msg, exc_info=True)
            return {"status": "error", "message": error_msg}

```

### Fayl: `api/__init__.py`
```py
"""API integrations."""
from api.venu_api import VenuSellerAPI

__all__ = ["VenuSellerAPI"]


```

### Fayl: `services/product_service.py`
```py
"""Product generation service layer."""

import logging
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

import requests

from agent import generate_main_image, generate_product_text, select_category_brand
from agent.category_brand.schemas import CategoryBrandSelectionSchema
from agent.image_search import search_product_images
from agent.image_search.image_downloader import (
    download_image,
    download_multiple_images,
    ImageDownloadError,
)
from agent.product.schemas import ProductGenSchema
from api import VenuSellerAPI
from core.config import settings
from core.constants import (
    DEFAULT_FALLBACK_IMAGE,
    IMAGE_DOWNLOAD_TIMEOUT,
    IMAGE_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)


class ProductServiceError(Exception):
    """Base exception for product service errors."""

    pass


class ImageDownloadError(ProductServiceError):
    """Raised when image download fails."""

    pass


class ImageGenerationError(ProductServiceError):
    """Raised when image generation fails."""

    pass


class ShopSaveError(ProductServiceError):
    """Raised when saving to shop fails."""

    pass


def download_image_from_url(image_url: str, save_path: str) -> str:
    """
    Download image from URL and save to local file.

    Args:
        image_url: URL of the image to download
        save_path: Local path where image will be saved

    Returns:
        str: Path to saved image file

    Raises:
        ImageDownloadError: If download fails
    """
    try:
        logger.info(f"Downloading image from URL: {image_url}")
        response = requests.get(image_url, timeout=IMAGE_DOWNLOAD_TIMEOUT)
        response.raise_for_status()

        # Ensure directory exists
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        # Save image
        with open(save_path, "wb") as f:
            f.write(response.content)

        logger.info(f"Image saved to: {save_path}")
        return save_path
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image: {e}")
        raise ImageDownloadError(f"Failed to download image: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error downloading image: {e}")
        raise ImageDownloadError(f"Failed to download image: {e}") from e


def generate_product_image_path(product_name: str, brand: str) -> str:
    """
    Generate product image using AI and save to temporary file.

    Args:
        product_name: Name of the product
        brand: Brand of the product

    Returns:
        str: Path to saved image file

    Raises:
        ImageGenerationError: If image generation or download fails
    """
    prompt = IMAGE_PROMPT_TEMPLATE.format(
        product_name=product_name, brand=brand
    )

    try:
        logger.info(f"Generating AI image for: {product_name} ({brand})")
        image_url = generate_main_image(prompt=prompt)

        # Create temporary file for image
        temp_dir = tempfile.gettempdir()
        safe_name = product_name.replace(" ", "_").replace("/", "_")[:50]
        random_suffix = os.urandom(4).hex()
        image_filename = f"product_{safe_name}_{random_suffix}.png"
        image_path = os.path.join(temp_dir, image_filename)

        # Download and save image
        saved_path = download_image_from_url(image_url, image_path)
        return saved_path

    except Exception as e:
        logger.error(f"Failed to generate product image: {e}")
        raise ImageGenerationError(f"Failed to generate product image: {e}") from e


def get_fallback_image_path() -> Optional[str]:
    """
    Get fallback image path if it exists.

    Returns:
        Optional[str]: Path to fallback image or None if not found
    """
    if os.path.exists(DEFAULT_FALLBACK_IMAGE):
        return DEFAULT_FALLBACK_IMAGE
    logger.warning(f"Fallback image {DEFAULT_FALLBACK_IMAGE} does not exist")
    return None


class ProductService:
    """Service for product generation and shop integration."""

    def __init__(self):
        """Initialize product service."""
        self._venu_api: Optional[VenuSellerAPI] = None

    def _get_venu_api(self) -> VenuSellerAPI:
        """
        Get or create Venu API client.

        Returns:
            VenuSellerAPI: Authenticated API client

        Raises:
            ShopSaveError: If credentials are missing or login fails
        """
        if not settings.venu_email or not settings.venu_password:
            raise ShopSaveError(
                "VENU_EMAIL yoki VENU_PASSWORD sozlanganmagan. "
                "Do'konga saqlash o'tkazib yuborildi."
            )

        if self._venu_api is None:
            self._venu_api = VenuSellerAPI(
                email=settings.venu_email, password=settings.venu_password
            )

            if not self._venu_api.login():
                raise ShopSaveError("Venu API ga login qilishda xatolik")

        return self._venu_api

    def generate_product_content(
        self, name: str, brand: str, price: int, stock: int
    ) -> ProductGenSchema:
        """
        Generate product text content using AI.

        Args:
            name: Product name
            brand: Product brand
            price: Product price
            stock: Product stock

        Returns:
            ProductGenSchema: Generated product content
        """
        logger.info(f"Generating product content: {name} ({brand})")
        return generate_product_text(name=name, brand=brand, price=price, stock=stock)

    def generate_product_image(
        self, product_name: str, brand: str
    ) -> Tuple[str, bool]:
        """
        Generate product image with fallback handling.

        Args:
            product_name: Name of the product
            brand: Brand of the product

        Returns:
            Tuple[str, bool]: (image_path, is_generated) - path and whether it was generated
        """
        try:
            image_path = generate_product_image_path(
                product_name=product_name, brand=brand
            )
            logger.info(f"Successfully generated product image: {image_path}")
            return image_path, True
        except ImageGenerationError as e:
            logger.error(f"Image generation failed, using fallback: {e}")
            fallback_path = get_fallback_image_path()
            if fallback_path:
                return fallback_path, False
            raise

    def search_and_download_product_images(
        self,
        product_name: str,
        brand: str,
        max_images: int = 5,
        use_ai_generation_fallback: bool = True,
    ) -> List[str]:
        """
        Search for product images from internet and download them.

        Args:
            product_name: Name of the product
            brand: Brand of the product
            max_images: Maximum number of images to download
            use_ai_generation_fallback: If True, fallback to AI generation if search fails

        Returns:
            List[str]: List of paths to downloaded image files
        """
        logger.info(
            f"Searching and downloading images for: {product_name} ({brand})"
        )

        try:
            # Step 1: Search for images using AI agent
            image_urls = search_product_images(
                product_name=product_name, brand=brand, max_results=max_images
            )

            if not image_urls:
                logger.warning("No images found from search, trying fallback...")
                if use_ai_generation_fallback:
                    # Fallback to AI generation
                    main_image_path, _ = self.generate_product_image(
                        product_name=product_name, brand=brand
                    )
                    return [main_image_path]
                return []

            # Step 2: Download images
            downloaded_paths = download_multiple_images(
                image_urls=image_urls, max_images=max_images, validate=True
            )

            if not downloaded_paths and use_ai_generation_fallback:
                logger.warning(
                    "Failed to download images, using AI generation fallback..."
                )
                main_image_path, _ = self.generate_product_image(
                    product_name=product_name, brand=brand
                )
                return [main_image_path]

            logger.info(
                f"Successfully downloaded {len(downloaded_paths)} images for {product_name}"
            )
            return downloaded_paths

        except Exception as e:
            logger.error(f"Error in search and download: {e}", exc_info=True)
            if use_ai_generation_fallback:
                try:
                    main_image_path, _ = self.generate_product_image(
                        product_name=product_name, brand=brand
                    )
                    return [main_image_path]
                except Exception:
                    pass
            return []

    def save_product_to_shop(
        self,
        product: ProductGenSchema,
        category_selection: CategoryBrandSelectionSchema,
        main_image_path: str,
        additional_images_paths: list,
    ) -> Tuple[bool, dict]:
        """
        Save product to shop via Venu API.

        Args:
            product: ProductGenSchema instance
            category_selection: CategoryBrandSelectionSchema instance
            main_image_path: Path to main image
            additional_images_paths: List of additional image paths

        Returns:
            Tuple[bool, dict]: (success, response) - success status and API response
        """
        try:
            venu_api = self._get_venu_api()

            logger.info("Do'konga mahsulotni saqlash boshlandi...")

            # Add product to shop
            result = venu_api.add_product(
                name=product.name,
                description=product.description,
                meta_image=main_image_path,
                meta_title=product.meta_title,
                meta_description=product.meta_description,
                tags=product.tags,
                price=float(product.price),
                category_id=category_selection.category_id,
                brand_id=category_selection.brand_id,
                main_image_path=main_image_path,
                additional_images_paths=additional_images_paths,
                stock=product.stock,
                sub_category_id=category_selection.sub_category_id,
                sub_sub_category_id=category_selection.sub_sub_category_id,
            )

            # Check result
            if result.get("status") == "error" or result.get("error"):
                logger.error(f"Do'konga saqlashda xatolik: {result}")
                return False, result

            logger.info(f"Mahsulot muvaffaqiyatli do'konga saqlandi: {product.name}")
            return True, result

        except ShopSaveError as e:
            logger.error(f"Do'konga saqlashda xatolik: {e}")
            return False, {"error": str(e)}
        except Exception as e:
            logger.error(
                f"Do'konga saqlashda kutilmagan xatolik: {e}", exc_info=True
            )
            return False, {"error": str(e)}

    def select_category_and_brand(
        self, product_name: str, brand_name: str
    ) -> Tuple[bool, Optional[dict], Optional[CategoryBrandSelectionSchema]]:
        """
        Select category and brand using AI.

        Args:
            product_name: Product name
            brand_name: Brand name

        Returns:
            Tuple[bool, Optional[dict], Optional]: (success, error_dict, category_selection)
        """
        try:
            venu_api = self._get_venu_api()

            # Get categories and brands
            logger.info("Kategoriya va brendlarni yuklayapman...")
            categories = venu_api.get_categories()
            brands = venu_api.get_brands()

            if not categories or not brands:
                error_msg = "Kategoriya yoki brendlar yuklanmadi"
                logger.error(error_msg)
                return False, {"error": error_msg}, None

            # AI yordamida kategoriya va brand ni aniqlash
            logger.info(
                f"AI yordamida kategoriya va brand ni aniqlayapman: "
                f"{product_name} ({brand_name})"
            )
            category_selection = select_category_brand(
                product_name=product_name,
                brand_name=brand_name,
                categories=categories,
                brands=brands,
            )

            logger.info(
                f"Aniqlangan: category_id={category_selection.category_id}, "
                f"sub_category_id={category_selection.sub_category_id}, "
                f"sub_sub_category_id={category_selection.sub_sub_category_id}, "
                f"brand_id={category_selection.brand_id}"
            )

            return True, None, category_selection

        except ShopSaveError as e:
            logger.error(f"Kategoriya va brand aniqlashda xatolik: {e}")
            return False, {"error": str(e)}, None
        except Exception as e:
            logger.error(
                f"Kategoriya va brand aniqlashda kutilmagan xatolik: {e}", exc_info=True
            )
            return False, {"error": str(e)}, None


```

### Fayl: `services/__init__.py`
```py
"""Service layer for business logic."""

from services.product_service import ProductService

__all__ = ["ProductService"]


```

### Fayl: `agent/__init__.py`
```py
"""Agent modules for product and image generation."""
from agent.category_brand import select_category_brand
from agent.image import generate_main_image
from agent.product import generate_product_text

__all__ = ["generate_product_text", "generate_main_image", "select_category_brand"]
```

### Fayl: `agent/image_search/image_downloader.py`
```py
"""Image downloader utilities."""

import logging
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from PIL import Image
from io import BytesIO

from core.constants import IMAGE_DOWNLOAD_TIMEOUT

logger = logging.getLogger(__name__)


class ImageDownloadError(Exception):
    """Raised when image download fails."""

    pass


class ImageValidationError(Exception):
    """Raised when image validation fails."""

    pass


def validate_image_url(url: str) -> bool:
    """
    Validate if URL is a valid image URL.

    Args:
        url: Image URL to validate

    Returns:
        bool: True if URL looks like an image URL
    """
    if not url or not isinstance(url, str):
        return False

    url_lower = url.lower()
    valid_extensions = [".jpg", ".jpeg", ".png", ".webp", ".gif"]
    valid_domains = ["http://", "https://"]

    # Check if URL starts with http/https
    if not any(url_lower.startswith(domain) for domain in valid_domains):
        return False

    # Check if URL contains image extension or common image hosting patterns
    has_extension = any(ext in url_lower for ext in valid_extensions)
    has_image_pattern = any(
        pattern in url_lower
        for pattern in ["/image", "/img", "image=", "img=", "photo", "picture"]
    )

    return has_extension or has_image_pattern


def validate_image_content(image_data: bytes) -> Tuple[bool, Optional[str]]:
    """
    Validate image content by trying to open it with PIL.

    Args:
        image_data: Image binary data

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    try:
        img = Image.open(BytesIO(image_data))
        img.verify()

        # Check minimum size (e.g., at least 100x100)
        img = Image.open(BytesIO(image_data))  # Reopen after verify
        width, height = img.size
        if width < 100 or height < 100:
            return False, f"Image too small: {width}x{height}"

        # Check maximum size (e.g., max 10MB)
        if len(image_data) > 10 * 1024 * 1024:
            return False, "Image too large (max 10MB)"

        return True, None
    except Exception as e:
        return False, f"Invalid image format: {str(e)}"


def download_image(
    image_url: str, save_path: Optional[str] = None, validate: bool = True
) -> str:
    """
    Download image from URL and save to local file.

    Args:
        image_url: URL of the image to download
        save_path: Local path where image will be saved (optional, auto-generated if None)
        validate: Whether to validate image content

    Returns:
        str: Path to saved image file

    Raises:
        ImageDownloadError: If download or validation fails
    """
    if not validate_image_url(image_url):
        raise ImageDownloadError(f"Invalid image URL: {image_url}")

    try:
        logger.info(f"Downloading image from URL: {image_url[:100]}...")

        # Download image
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(
            image_url, timeout=IMAGE_DOWNLOAD_TIMEOUT, headers=headers, stream=True
        )
        response.raise_for_status()

        # Check content type
        content_type = response.headers.get("content-type", "").lower()
        if not content_type.startswith("image/"):
            logger.warning(
                f"Unexpected content type: {content_type}, proceeding anyway..."
            )

        # Read image data
        image_data = response.content

        # Validate image content
        if validate:
            is_valid, error_msg = validate_image_content(image_data)
            if not is_valid:
                raise ImageDownloadError(
                    f"Image validation failed: {error_msg or 'Unknown error'}"
                )

        # Generate save path if not provided
        if save_path is None:
            temp_dir = tempfile.gettempdir()
            # Extract extension from URL or content type
            ext = ".jpg"
            if ".png" in image_url.lower():
                ext = ".png"
            elif ".webp" in image_url.lower():
                ext = ".webp"
            elif "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"

            filename = f"product_image_{os.urandom(4).hex()}{ext}"
            save_path = os.path.join(temp_dir, filename)

        # Ensure directory exists
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        # Save image
        with open(save_path, "wb") as f:
            f.write(image_data)

        logger.info(f"Image saved to: {save_path}")
        return save_path

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image: {e}")
        raise ImageDownloadError(f"Failed to download image: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error downloading image: {e}")
        raise ImageDownloadError(f"Failed to download image: {e}") from e


def download_multiple_images(
    image_urls: List[str], max_images: int = 5, validate: bool = True
) -> List[str]:
    """
    Download multiple images from URLs.

    Args:
        image_urls: List of image URLs to download
        max_images: Maximum number of images to download
        validate: Whether to validate image content

    Returns:
        List[str]: List of paths to saved image files
    """
    downloaded_paths = []
    failed_count = 0

    for i, url in enumerate(image_urls[:max_images]):
        try:
            image_path = download_image(url, validate=validate)
            downloaded_paths.append(image_path)
            logger.info(f"Downloaded image {i + 1}/{min(len(image_urls), max_images)}")
        except ImageDownloadError as e:
            failed_count += 1
            logger.warning(f"Failed to download image {i + 1}: {e}")
            if failed_count >= 3:  # Stop after 3 consecutive failures
                logger.warning("Too many download failures, stopping...")
                break

    logger.info(f"Downloaded {len(downloaded_paths)}/{len(image_urls[:max_images])} images")
    return downloaded_paths


```

### Fayl: `agent/image_search/image_search_agent.py`
```py
"""AI agent for searching product images from the internet."""

import logging
from typing import List, Optional

# TODO: Bu yerda sizning AI agentingizni yozasiz
# Bu funksiya mahsulot nomi va brendiga asoslanib internetdan rasm URLlarini qaytarishi kerak

logger = logging.getLogger(__name__)


def search_product_images(
    product_name: str, brand: str, max_results: int = 5, **kwargs
) -> List[str]:
    """
    Search for product images from the internet using AI.

    Args:
        product_name: Name of the product
        brand: Brand of the product
        max_results: Maximum number of image URLs to return
        **kwargs: Additional parameters for AI agent

    Returns:
        List[str]: List of image URLs found on the internet

    Example:
        >>> urls = search_product_images("iPhone 15", "Apple", max_results=3)
        >>> print(urls)
        ['https://example.com/iphone15-1.jpg', 'https://example.com/iphone15-2.jpg', ...]

    TODO: Bu funksiyani to'ldiring:
    1. AI agent yordamida mahsulot rasmlarini qidirish
    2. Internetdan topilgan rasm URLlarini qaytarish
    3. Rasm URLlarini validatsiya qilish
    4. Eng yaxshi rasmlarni tanlash (quality, relevance, etc.)

    Hozircha placeholder - faqat bo'sh list qaytaradi.
    """
    logger.info(f"Searching images for: {product_name} ({brand})")

    # TODO: AI agent logikasini yozing
    # Masalan:
    # - OpenAI yoki boshqa AI API dan foydalanish
    # - Web search API dan foydalanish (Google Custom Search, Bing, etc.)
    # - Image search API dan foydalanish
    # - Scraping (legal va etik bo'lsa)

    # Placeholder - hozircha bo'sh list qaytaradi
    image_urls: List[str] = []

    # Example structure (o'chirib tashlang va o'zingiz yozing):
    # try:
    #     # AI agent yordamida qidirish
    #     search_query = f"{product_name} {brand} product image"
    #     # ... AI agent logikasi ...
    #     image_urls = [...]  # Topilgan URLlar
    # except Exception as e:
    #     logger.error(f"Image search failed: {e}")
    #     return []

    logger.info(f"Found {len(image_urls)} image URLs")
    return image_urls


def filter_best_images(
    image_urls: List[str], product_name: str, brand: str, max_results: int = 5
) -> List[str]:
    """
    Filter and rank images to get the best ones.

    Args:
        image_urls: List of image URLs
        product_name: Product name for relevance checking
        brand: Brand name for relevance checking
        max_results: Maximum number of images to return

    Returns:
        List[str]: Filtered and ranked image URLs

    TODO: Bu funksiyani to'ldiring:
    1. Rasm URLlarini validatsiya qilish
    2. Rasm sifatini baholash
    3. Relevancelikni tekshirish
    4. Eng yaxshi rasmlarni tanlash va tartiblash
    """
    logger.info(f"Filtering {len(image_urls)} images to get best {max_results}")

    # TODO: Filtering logikasini yozing
    # Masalan:
    # - URL validatsiya
    # - Image quality scoring
    # - Relevance scoring
    # - Ranking va selection

    # Placeholder - hozircha barcha URLlarni qaytaradi
    return image_urls[:max_results]

```

### Fayl: `agent/image_search/__init__.py`
```py
"""Image search agent for finding product images from the internet."""

from agent.image_search.image_search_agent import search_product_images

__all__ = ["search_product_images"]


```

### Fayl: `agent/image/image_agent.py`
```py
"""Image generation agent using OpenAI DALL-E."""

import logging
from typing import Optional

from core.config import settings
from core.constants import (
    DEFAULT_IMAGE_MODEL,
    DEFAULT_IMAGE_QUALITY,
    DEFAULT_IMAGE_SIZE,
)
from core.openai_client import get_openai_client

logger = logging.getLogger(__name__)

# Get OpenAI client
client = get_openai_client()


def generate_main_image(
    prompt: str,
    model: Optional[str] = None,
    size: Optional[str] = None,
    quality: Optional[str] = None,
    n: int = 1,
) -> str:
    """
    Generate product image using OpenAI DALL-E.

    Args:
        prompt: Image generation prompt
        model: Model to use (dall-e-2 or dall-e-3)
        size: Image size (1024x1024, 512x512, etc.)
        quality: Image quality (standard or hd for dall-e-3)
        n: Number of images to generate (1 for dall-e-3)

    Returns:
        str: URL of the generated image

    Raises:
        ValueError: If image generation fails
    """
    model = model or DEFAULT_IMAGE_MODEL
    size = size or DEFAULT_IMAGE_SIZE
    quality = quality or DEFAULT_IMAGE_QUALITY

    logger.info(f"Generating image with prompt: {prompt[:100]}...")

    try:
        if model == "dall-e-3":
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,  # dall-e-3 only supports n=1
            )
        else:  # dall-e-2
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                n=n,
            )

        image_url = response.data[0].url
        logger.info("Image generated successfully")
        return image_url
    except Exception as e:
        logger.error(f"Image generation failed: {e}", exc_info=True)
        raise ValueError(f"Failed to generate image: {e}") from e

```

### Fayl: `agent/image/__init__.py`
```py
"""Image generation agent."""
from agent.image.image_agent import generate_main_image

__all__ = ["generate_main_image"]
```

### Fayl: `agent/product/schemas.py`
```py
"""Product schemas - single source of truth for product data structures."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field, ConfigDict, conint, constr


class ProductGenSchema(BaseModel):
    """AI agent generated product JSON schema (Russian only)."""

    model_config = ConfigDict(extra="forbid")

    name: constr(min_length=1) = Field(..., description="Product name in Russian")
    description: constr(min_length=1) = Field(
        ..., description="Product description in Russian"
    )
    meta_title: constr(min_length=1) = Field(..., description="Meta title in Russian")
    meta_description: constr(min_length=1) = Field(
        ..., description="Meta description in Russian"
    )

    # Tags are a simple list
    tags: List[constr(min_length=1)] = Field(
        default_factory=list, description="5-10 lowercase tags, no duplicates"
    )

    price: conint(ge=0) = Field(..., description="Price in smallest currency unit")
    stock: conint(ge=0) = Field(default=5, description="Available stock quantity")

```

### Fayl: `agent/product/agent.py`
```py
"""Product text generation agent using OpenAI."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from openai import OpenAI
from pydantic import ValidationError

from agent.product.schemas import ProductGenSchema
from core.config import settings
from core.openai_client import get_openai_client

logger = logging.getLogger(__name__)

# Cyrillic detection regex
CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")


# Get OpenAI client from core
client = get_openai_client()


# ---------------------------
# Prompts
# ---------------------------

SYSTEM_PROMPT = """
You are a product content generation AI for an e-commerce marketplace.

Return ONLY valid JSON. No markdown. No explanations. No extra text.
The JSON must match the required structure exactly (no extra keys).

Language:
- All content must be in Russian (ru)

Quality rules:
- Marketplace-ready, clear, natural, commercial tone
- Yes emojis
- Avoid unrealistic claims
""".strip()


def _required_output_template() -> Dict[str, Any]:
    # This is NOT a JSON Schema spec; it's a strict example structure the model must match.
    return {
        "name": "string",
        "description": "string",
        "meta_title": "string",
        "meta_description": "string",
        "tags": ["string"],
        "price": 0,
        "stock": 5,
    }


def _build_user_prompt(name: str, brand: str, price: int, stock: int) -> str:
    template = _required_output_template()

    return f"""
Generate product data for the following product.

Product info:
- Name: {name}
- Brand: {brand}
- Price: {price}
- Stock: {stock}

Hard requirements:
1) Output MUST be STRICT VALID JSON (no trailing commas).
2) Output JSON MUST match this structure exactly (same keys, no extra keys):
{json.dumps(template, ensure_ascii=False, indent=2)}

3) Description length:
- 3–5 full sentences in Russian

4) Meta title:
- max 60 characters in Russian

5) Meta description:
- max 160 characters in Russian

6) Tags:
- 5–10 relevant keywords
- lowercase
- no duplicates
- avoid brand spam (brand can appear at most once)

7) Use the provided price and stock EXACTLY.
""".strip()


# ---------------------------
# Helpers
# ---------------------------


def _coerce_tags(value: Any) -> List[str]:
    """
    Accepts:
    - ["a","b"]
    - "a, b, c"
    - {"ru": [...], "uz": [...]}  (legacy)
    - {"ru": "a,b", "uz": "c,d"}  (legacy)
    """
    if value is None:
        return []

    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]

    if isinstance(value, str):
        # split by commas
        parts = [p.strip() for p in value.split(",")]
        return [p for p in parts if p]

    if isinstance(value, dict):
        merged: List[str] = []
        for k in ("ru", "uz"):
            v = value.get(k)
            merged.extend(_coerce_tags(v))
        return merged

    return [str(value).strip()] if str(value).strip() else []


def _normalize_product_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    # If AI accidentally returns localized tags, normalize to list
    if "tags" in data:
        data["tags"] = _coerce_tags(data["tags"])

    # Ensure stock exists (fallback)
    if "stock" not in data or data["stock"] is None:
        data["stock"] = 5

    return data


def _assert_russian_only(product: ProductGenSchema) -> None:
    # Soft guardrail: All text should be in Russian (Cyrillic)
    fields = [
        product.name,
        product.description,
        product.meta_title,
        product.meta_description,
    ]
    # Check that at least some Cyrillic characters are present
    if not any(CYRILLIC_RE.search(t or "") for t in fields):
        logger.warning(
            "Warning: Generated text may not contain Russian (Cyrillic) characters"
        )


def _cleanup_tags(tags: List[str], max_len: int = 10) -> List[str]:
    cleaned = []
    seen = set()
    for t in tags:
        tt = t.strip().lower()
        if not tt:
            continue
        if tt in seen:
            continue
        seen.add(tt)
        cleaned.append(tt)
        if len(cleaned) >= max_len:
            break
    return cleaned


# ---------------------------
# Public API
# ---------------------------


def generate_product_text(
    name: str,
    brand: str,
    price: int,
    stock: int = 5,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_retries: Optional[int] = None,
) -> ProductGenSchema:
    """
    Generates Russian-only product JSON and validates it with Pydantic.

    Args:
        name: Product name (in Russian)
        brand: Product brand
        price: Product price
        stock: Product stock quantity (default: 5)
        model: OpenAI model to use (default: from settings)
        temperature: Temperature for generation (default: from settings)
        max_retries: Maximum retry attempts (default: from settings)

    Returns:
        ProductGenSchema: Validated product schema

    Raises:
        ValueError: If generation fails after all retries
    """
    model = model or settings.openai_model
    temperature = (
        temperature if temperature is not None else settings.openai_temperature
    )
    max_retries = (
        max_retries if max_retries is not None else settings.openai_max_retries
    )

    user_prompt = _build_user_prompt(name=name, brand=brand, price=price, stock=stock)
    last_error: Optional[Exception] = None

    logger.info(f"Generating product text for: {name} ({brand})")

    for attempt in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as e:
            logger.error(
                f"OpenAI API error (attempt {attempt + 1}/{max_retries + 1}): {e}",
                exc_info=True,
            )
            last_error = e
            if attempt < max_retries:
                continue
            raise

        content = (resp.choices[0].message.content or "").strip()

        # 1) Parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(
                f"Invalid JSON response (attempt {attempt + 1}): {content[:300]}"
            )
            last_error = ValueError(f"AI valid JSON qaytarmadi (attempt={attempt + 1})")
            user_prompt += (
                "\n\nIMPORTANT: Output ONLY strict JSON. No text. No markdown."
            )
            continue

        # 2) Normalize (tags etc.)
        try:
            data = _normalize_product_dict(data)
        except Exception as e:
            logger.warning(f"Normalization error (attempt {attempt + 1}): {e}")
            last_error = e
            user_prompt += "\n\nYour previous JSON structure was wrong. Fix it and output ONLY JSON."
            continue

        # 3) Validate schema
        try:
            product = ProductGenSchema(**data)
            _assert_russian_only(product)
            product.tags = _cleanup_tags(product.tags)
            # Keep price/stock exact (hard rule)
            product.price = price
            product.stock = stock
            logger.info(f"Successfully generated product text for: {name}")
            return product
        except (ValidationError, ValueError) as e:
            logger.warning(f"Validation error (attempt {attempt + 1}): {e}")
            last_error = e
            user_prompt = (
                user_prompt
                + "\n\nYour previous JSON did not validate. Fix it and output ONLY corrected JSON.\n"
                + f"Validation error summary: {str(e)[:900]}"
            )
            continue

    error_msg = f"Failed to generate valid product JSON after {max_retries + 1} attempts. Last error: {last_error}"
    logger.error(error_msg)
    raise ValueError(error_msg)

```

### Fayl: `agent/product/__init__.py`
```py
"""Product text generation agent."""

from agent.product.agent import generate_product_text
from agent.product.schemas import ProductGenSchema

__all__ = ["generate_product_text", "ProductGenSchema"]

```

### Fayl: `agent/category_brand/schemas.py`
```py
"""Category and Brand selection schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class CategoryBrandSelectionSchema(BaseModel):
    """Schema for category and brand selection by AI."""

    category_id: str = Field(..., description="Selected category ID")
    sub_category_id: Optional[str] = Field(
        None, description="Selected sub-category ID"
    )
    sub_sub_category_id: Optional[str] = Field(
        None, description="Selected sub-sub-category ID"
    )
    brand_id: int = Field(..., description="Selected brand ID")


```

### Fayl: `agent/category_brand/agent.py`
```py
"""Category and Brand selection agent using OpenAI."""

import json
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI
from pydantic import ValidationError

from agent.category_brand.schemas import CategoryBrandSelectionSchema
from core.config import settings
from core.openai_client import get_openai_client

logger = logging.getLogger(__name__)

# Get OpenAI client from core
client = get_openai_client()


def _build_categories_tree(categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build a simplified tree structure for categories."""
    result = []
    for cat in categories:
        cat_info = {
            "id": str(cat["id"]),
            "name": cat["name"],
            "sub_categories": [],
        }
        for sub_cat in cat.get("childes", []):
            sub_cat_info = {
                "id": str(sub_cat["id"]),
                "name": sub_cat["name"],
                "sub_sub_categories": [],
            }
            for sub_sub_cat in sub_cat.get("childes", []):
                sub_sub_cat_info = {
                    "id": str(sub_sub_cat["id"]),
                    "name": sub_sub_cat["name"],
                }
                sub_cat_info["sub_sub_categories"].append(sub_sub_cat_info)
            cat_info["sub_categories"].append(sub_cat_info)
        result.append(cat_info)
    return result


def _build_brands_list(brands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build a simplified list of brands."""
    return [{"id": brand["id"], "name": brand["name"]} for brand in brands]


def select_category_brand(
    product_name: str,
    brand_name: str,
    categories: List[Dict[str, Any]],
    brands: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_retries: Optional[int] = None,
) -> CategoryBrandSelectionSchema:
    """
    Select category and brand IDs using AI based on product name and brand.

    Args:
        product_name: Product name
        brand_name: Brand name
        categories: List of categories from API
        brands: List of brands from API
        model: OpenAI model to use (default: from settings)
        temperature: Temperature for generation (default: from settings)
        max_retries: Maximum retry attempts (default: from settings)

    Returns:
        CategoryBrandSelectionSchema: Selected category and brand IDs

    Raises:
        ValueError: If selection fails after all retries
    """
    model = model or settings.openai_model
    temperature = (
        temperature if temperature is not None else settings.openai_temperature
    )
    max_retries = (
        max_retries if max_retries is not None else settings.openai_max_retries
    )

    # Build simplified structures
    categories_tree = _build_categories_tree(categories)
    brands_list = _build_brands_list(brands)

    system_prompt = """
You are a category and brand selection assistant for an e-commerce platform.
Your task is to select the most appropriate category and brand IDs based on the product name and brand name.

Return ONLY valid JSON. No markdown. No explanations. No extra text.
The JSON must match this structure exactly:
{
  "category_id": "string",
  "sub_category_id": "string or null",
  "sub_sub_category_id": "string or null",
  "brand_id": integer
}

Rules:
1. Select the most specific category that matches the product (prefer sub_sub_category_id if available, then sub_category_id, then category_id)
2. Match the brand name as closely as possible (case-insensitive, handle variations)
3. If exact match not found, select the closest match
4. category_id is always required (string)
5. brand_id is always required (integer)
6. sub_category_id and sub_sub_category_id can be null if not available
""".strip()

    user_prompt = f"""
Product name: {product_name}
Brand name: {brand_name}

Available categories:
{json.dumps(categories_tree, ensure_ascii=False, indent=2)}

Available brands:
{json.dumps(brands_list, ensure_ascii=False, indent=2)}

Select the most appropriate category and brand IDs. Return ONLY valid JSON matching the required structure.
""".strip()

    last_error: Optional[Exception] = None

    logger.info(f"Selecting category and brand for: {product_name} ({brand_name})")

    for attempt in range(max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
        except Exception as e:
            logger.error(f"OpenAI API error (attempt {attempt + 1}): {e}")
            last_error = e
            if attempt < max_retries:
                continue
            raise

        content = (resp.choices[0].message.content or "").strip()

        # Parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.warning(
                f"Invalid JSON response (attempt {attempt + 1}): {content[:300]}"
            )
            last_error = ValueError(
                f"AI valid JSON qaytarmadi (attempt={attempt + 1})"
            )
            user_prompt += (
                "\n\nIMPORTANT: Output ONLY strict JSON. No text. No markdown."
            )
            continue

        # Validate schema
        try:
            selection = CategoryBrandSelectionSchema(**data)
            logger.info(
                f"Successfully selected category_id={selection.category_id}, brand_id={selection.brand_id}"
            )
            return selection
        except ValidationError as e:
            logger.warning(f"Validation error (attempt {attempt + 1}): {e}")
            last_error = e
            user_prompt = (
                user_prompt
                + "\n\nYour previous JSON did not validate. Fix it and output ONLY corrected JSON.\n"
                + f"Validation error summary: {str(e)[:900]}"
            )
            continue

    error_msg = f"Failed to select valid category/brand after {max_retries + 1} attempts. Last error: {last_error}"
    logger.error(error_msg)
    raise ValueError(error_msg)


```

### Fayl: `agent/category_brand/__init__.py`
```py
"""Category and Brand selection agent."""
from agent.category_brand.agent import select_category_brand

__all__ = ["select_category_brand"]


```

### Fayl: `core/config.py`
```py
"""Application configuration management."""

from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str

    # API Configuration
    api_title: str = "AI Product Generator"
    api_version: str = "1.0.0"

    # OpenAI Model Configuration
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.3
    openai_max_retries: int = 2

    # Venu API Configuration
    venu_base_url: str = "https://api.venu.uz"
    venu_temp_token: Optional[str] = None
    venu_email: Optional[str] = None
    venu_password: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, extra="ignore"
    )


# Global settings instance
settings = Settings()

# Validate required settings
if not settings.openai_api_key:
    raise RuntimeError("OPENAI_API_KEY not found. Please add it to .env file.")

```

### Fayl: `core/constants.py`
```py
"""Application constants."""

# Image generation constants
DEFAULT_IMAGE_MODEL = "dall-e-3"
DEFAULT_IMAGE_SIZE = "1080x1440"
DEFAULT_IMAGE_QUALITY = "standard"
DEFAULT_FALLBACK_IMAGE = "test_rasm.png"

# Image download constants
IMAGE_DOWNLOAD_TIMEOUT = 30

# Product constants
DEFAULT_STOCK = 5
DEFAULT_UNIT = "pc"
DEFAULT_DISCOUNT = 0.0
DEFAULT_DISCOUNT_TYPE = "flat"
DEFAULT_SUB_CATEGORY_ID = "600"
DEFAULT_SUB_SUB_CATEGORY_ID = "601"

# API constants
CORS_ALLOW_ORIGINS = ["*"]  # Configure appropriately for production

# Image prompt template
IMAGE_PROMPT_TEMPLATE = "Professional product photo of {product_name} by {brand}, high quality, white background, e-commerce style"


```

### Fayl: `core/__init__.py`
```py
"""Core utilities and configuration."""
from core.config import settings
from core.openai_client import get_openai_client

__all__ = ["settings", "get_openai_client"]


```

### Fayl: `core/openai_client.py`
```py
"""OpenAI client singleton."""
from typing import Optional

from openai import OpenAI

from core.config import settings

_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    """Get or create OpenAI client instance."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


```

