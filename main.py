"""FastAPI application for AI Product Generator."""

import logging
import os
import random

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent.image import generate_poster
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

        # Get default product images
        from services.product_service import get_default_image_path
        from yandex import get_product_images_from_yandex

        # Get additional images from Yandex
        additional_images_paths = get_product_images_from_yandex(
            product_name=request.name, brand=request.brand, max_images=5
        )

        # If no images found, use default
        if not additional_images_paths:
            logger.warning(f"Yandex'da rasm topilmadi, default rasm ishlatilmoqda")
            additional_images_paths = [get_default_image_path()]

        image_for_poster = additional_images_paths[0]

        # Select random template from templates directory
        templates_dir = "templates"
        if os.path.exists(templates_dir):
            template_files = [
                f
                for f in os.listdir(templates_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
            ]
            if template_files:
                selected_template = random.choice(template_files)
                template_image_path = os.path.join(templates_dir, selected_template)
                logger.info(f"Selected template: {template_image_path}")
            else:
                logger.warning("Templates papkasida rasm topilmadi")
                template_image_path = None
        else:
            logger.warning(f"Templates papkasi topilmadi: {templates_dir}")
            template_image_path = None

        # Format product params as string for poster generation
        product_params_str = f"{product.name}\n{product.description}"

        main_image_path = generate_poster(
            template_image_path=template_image_path,
            product_image_path=image_for_poster,
            product_params=product_params_str,
        )

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
