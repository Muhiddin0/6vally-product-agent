"""Category and Brand selection agent using OpenAI."""

import difflib
import json
import logging
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from agent.category_brand.schemas import CategoryBrandSelectionSchema
from core.config import settings
from core.openai_client import get_openai_client

logger = logging.getLogger(__name__)

# Get OpenAI client from core
client = get_openai_client()


def _build_categories_tree(
    categories: List[Dict[str, Any]],
    parent_id: Optional[str] = None,
    level: str = "category",
) -> List[Dict[str, Any]]:
    """Build a simplified structure for categories at a specific level."""
    result = []

    if level == "category":
        for cat in categories:
            result.append({"id": str(cat["id"]), "name": cat["name"]})
    elif level == "sub_category" and parent_id:
        for cat in categories:
            if str(cat["id"]) == parent_id:
                for sub_cat in cat.get("childes", []):
                    result.append({"id": str(sub_cat["id"]), "name": sub_cat["name"]})
                break
    elif level == "sub_sub_category" and parent_id:
        # parent_id here is the sub_category_id, so we need to find it across all main categories
        for cat in categories:
            for sub_cat in cat.get("childes", []):
                if str(sub_cat["id"]) == parent_id:
                    for sub_sub_cat in sub_cat.get("childes", []):
                        result.append(
                            {"id": str(sub_sub_cat["id"]), "name": sub_sub_cat["name"]}
                        )
                    return result
    return result


def _select_step(
    prompt_level: str,
    product_name: str,
    brand_name: str,
    options: List[Dict[str, Any]],
    model: str,
    temperature: float,
) -> Optional[Dict[str, Any]]:
    """Helper to perform a single AI selection step."""
    if not options:
        return None

    system_prompt = f"""
You are a category selection assistant.
Select the most appropriate {prompt_level.replace('_', ' ')} ID based on the product name and brand.

Return ONLY valid JSON:
{{
  "id": "string",
  "name": "string"
}}
""".strip()

    user_prompt = f"""
Product: {product_name}
Brand: {brand_name}

Available {prompt_level.replace('_', ' ')}s:
{json.dumps(options, ensure_ascii=False)}

Select the ID. Return ONLY JSON.
""".strip()

    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = (resp.choices[0].message.content or "").strip()
        return json.loads(content)
    except Exception as e:
        logger.warning(f"AI selection failed for {prompt_level}: {e}")
        return None


def _match_brand(brand_name: str, brands: List[Dict[str, Any]]) -> int:
    """
    Match brand name from API list using fuzzy matching.

    Args:
        brand_name: Input brand name to search for
        brands: List of brands from API

    Returns:
        int: Best matching brand ID. Returns 0 (Unknown) if no good match.
    """
    if not brands:
        return 0

    # Try exact match first (case-insensitive)
    search_name = brand_name.strip().lower()
    for brand in brands:
        if brand["name"].strip().lower() == search_name:
            return brand["id"]

    # Use difflib for fuzzy matching
    brand_names = [b["name"] for b in brands]
    matches = difflib.get_close_matches(brand_name, brand_names, n=1, cutoff=0.6)

    if matches:
        matched_name = matches[0]
        for brand in brands:
            if brand["name"] == matched_name:
                return brand["id"]

    # Default to first brand if it exists, or 0
    # Usually the first brand in 6Valley is "Unknown" or similar if not specified
    # But here we just return 0 if no match found
    return brands[0]["id"] if brands else 0


def select_category_brand(
    product_name: str,
    brand_name: str,
    categories: List[Dict[str, Any]],
    brands: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> CategoryBrandSelectionSchema:
    """
    Select category and brand IDs using AI based on product name and brand.
    Uses 3-step process (Category -> Sub-category -> Sub-sub-category) to reduce tokens.
    """
    model = model or settings.openai_model
    temperature = (
        temperature if temperature is not None else settings.openai_temperature
    )

    # 1. Match brand using Python logic (Fast, no AI)
    brand_id = _match_brand(brand_name, brands)
    logger.info(f"Matched brand '{brand_name}' to ID {brand_id}")

    # 2. Step-by-step category selection
    result = {
        "category_id": "0",
        "category": None,
        "sub_category_id": None,
        "sub_category": None,
        "sub_sub_category_id": None,
        "sub_sub_category": None,
        "brand_id": brand_id,
    }

    # Step A: Main Category
    main_options = _build_categories_tree(categories, level="category")
    main_sel = _select_step(
        "category", product_name, brand_name, main_options, model, temperature
    )

    if main_sel and "id" in main_sel:
        result["category_id"] = main_sel["id"]
        result["category"] = main_sel.get("name")

        # Step B: Sub Category
        sub_options = _build_categories_tree(
            categories, parent_id=main_sel["id"], level="sub_category"
        )
        if sub_options:
            sub_sel = _select_step(
                "sub_category",
                product_name,
                brand_name,
                sub_options,
                model,
                temperature,
            )
            if sub_sel and "id" in sub_sel:
                result["sub_category_id"] = sub_sel["id"]
                result["sub_category"] = sub_sel.get("name")

                # Step C: Sub-sub Category
                sub_sub_options = _build_categories_tree(
                    categories, parent_id=sub_sel["id"], level="sub_sub_category"
                )
                if sub_sub_options:
                    ss_sel = _select_step(
                        "sub_sub_category",
                        product_name,
                        brand_name,
                        sub_sub_options,
                        model,
                        temperature,
                    )
                    if ss_sel and "id" in ss_sel:
                        result["sub_sub_category_id"] = ss_sel["id"]
                        result["sub_sub_category"] = ss_sel.get("name")

    try:
        selection = CategoryBrandSelectionSchema(**result)
        logger.info(
            f"Successfully selected category hierarchy for {product_name}: "
            f"{result['category']} > {result['sub_category']} > {result['sub_sub_category']}"
        )
        return selection
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        # Return a fallback schema if validation fails after AI steps
        return CategoryBrandSelectionSchema(
            category_id=result["category_id"] or "0",
            category=result.get("category"),
            brand_id=brand_id,
        )
