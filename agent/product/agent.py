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
You are a professional product content generation AI for an e-commerce marketplace.
Your task is to create engaging, attractive, and compelling product descriptions that capture attention and drive sales.

Return ONLY valid JSON. No markdown. No explanations. No extra text.
The JSON must match the required structure exactly (no extra keys).

Language:
- All content must be in Russian (ru)

Description quality rules:
- Create engaging, attractive, and interesting descriptions (NOT dry or boring)
- Start with a compelling opening line that captures attention
- Use emojis/stickers strategically throughout the description (📱 ⚡ 📸 🔋 🔐 💎 ✨ 🎯 🚀 💪 etc.)
- Structure descriptions with:
  * An engaging opening sentence
  * A descriptive paragraph highlighting key features
  * Bullet points with emojis for important features/benefits
  * A compelling closing statement
- Make descriptions marketing-oriented, persuasive, and exciting
- Highlight unique selling points and benefits
- Use enters and line breaks to make the description more readable
- Use vivid, appealing language that creates desire
- Avoid dry, technical, or boring language
- Make it feel premium and valuable
- Use html tags to make the description more readable (p, br, ul, li, etc.)
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

3) Description requirements:
- Create an engaging, attractive, and interesting description (NOT dry or boring)
- Length: 8-15 sentences or structured paragraphs with bullet points
- Structure:
  * Start with a compelling opening line (e.g., "iPhone 17 — kelajak bugundan boshlanadi.")
  * Add 2-3 sentences describing the product's main appeal and design
  * Include 4-6 bullet points with emojis highlighting key features (e.g., "📱 Super Retina XDR 2.0 displey — ...")
  * End with a compelling closing statement that emphasizes value
- Use emojis/stickers strategically (📱 ⚡ 📸 🔋 🔐 💎 ✨ 🎯 🚀 💪 ⭐ 🔥 💼 🎨 🛡️ etc.)
- Make it marketing-oriented, persuasive, and exciting
- Use vivid, appealing language
- Highlight benefits and unique selling points

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
            print(data)

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
