"""Product generation service layer."""

import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple

from agent import generate_product_text, select_category_brand
from agent.category_brand.schemas import CategoryBrandSelectionSchema
from agent.product.schemas import ProductGenSchema
from api import VenuSellerAPI
from core.config import settings
from core.constants import DEFAULT_FALLBACK_IMAGE

logger = logging.getLogger(__name__)


class ProductServiceError(Exception):
    """Base exception for product service errors."""

    pass


class ShopSaveError(ProductServiceError):
    """Raised when saving to shop fails."""

    pass


def get_default_image_path() -> str:
    """
    Get default image path for products.

    Returns:
        str: Path to default image file
    """
    if os.path.exists(DEFAULT_FALLBACK_IMAGE):
        return DEFAULT_FALLBACK_IMAGE

    # Create media/products directory if it doesn't exist
    media_dir = Path("media/products")
    media_dir.mkdir(parents=True, exist_ok=True)

    # Return default path (will be created if needed)
    default_path = str(media_dir / "default_product.png")
    logger.info(f"Using default image path: {default_path}")
    return default_path


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

    def get_product_images(
        self,
        product_name: str,
        brand: str,
        max_images: int = 5,
    ) -> List[str]:
        """
        Get default product images.

        Args:
            product_name: Name of the product
            brand: Brand of the product
            max_images: Maximum number of images to return (max 5)

        Returns:
            List[str]: List of paths to default image files
        """
        logger.info(f"Using default images for: {product_name} ({brand})")
        default_image = get_default_image_path()
        return [default_image] * min(max_images, 5)

    def save_product_to_shop(
        self,
        product: ProductGenSchema,
        category_selection: CategoryBrandSelectionSchema,
        main_image_path: str,
        additional_images_paths: List[str],
        api_client: Optional[VenuSellerAPI] = None,
    ) -> Tuple[bool, dict]:
        """
        Save product to shop via Venu API.

        Args:
            product: ProductGenSchema instance
            category_selection: CategoryBrandSelectionSchema instance
            main_image_path: Path to main image
            additional_images_paths: List of additional image paths
            api_client: Optional VenuSellerAPI client (overrides default)

        Returns:
            Tuple[bool, dict]: (success, response) - success status and API response
        """
        try:
            venu_api = api_client if api_client else self._get_venu_api()

            logger.info("Do'konga mahsulotni saqlash boshlandi...")

            

            # Add product to shop
            result = venu_api.add_product(
                name=product.name,
                description=product.description,
                meta_image=main_image_path,
                meta_title=product.meta_title,
                meta_description=product.meta_description,
                tags=product.tags,
                price=12000,
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
            logger.error(f"Do'konga saqlashda kutilmagan xatolik: {e}", exc_info=True)
            return False, {"error": str(e)}

    def select_category_and_brand(
        self, product_name: str, brand_name: str, api_client: Optional[VenuSellerAPI] = None
    ) -> Tuple[bool, Optional[dict], Optional[CategoryBrandSelectionSchema]]:
        """
        Select category and brand using AI.

        Args:
            product_name: Product name
            brand_name: Brand name
            api_client: Optional VenuSellerAPI client (overrides default)

        Returns:
            Tuple[bool, Optional[dict], Optional]: (success, error_dict, category_selection)
        """
        try:
            venu_api = api_client if api_client else self._get_venu_api()

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
