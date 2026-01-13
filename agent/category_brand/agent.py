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

