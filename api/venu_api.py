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
            "discount": 0,
            "discount_type": "flat",
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
