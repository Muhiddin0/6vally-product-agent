import base64
import os
from core.openai_client import get_openai_client
from dataclasses import dataclass
from typing import List, Optional, Literal, Dict, Any


client = get_openai_client()


@dataclass
class ProductInput:
    name: str
    category: Optional[str] = None
    sub_category: Optional[str] = None
    sub_sub_category: Optional[str] = None
    brand: Optional[str] = None
    image_paths: Optional[List[str]] = None  # local paths


def encode_image_to_base64(image_path: str) -> str:
    """Encode a local image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_mime_type(image_path: str) -> str:
    """Get MIME type based on file extension."""
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mime_types.get(ext, "image/jpeg")


def get_product_params(product_input: ProductInput) -> Dict[str, Any]:
    """
    Get product physical parameters (width, height, length, weight) using AI.

    Args:
        product_input: ProductInput with product name, category info, brand, and images

    Returns:
        Dict with keys: weight (g), height (mm), width (mm), length (mm),
                       confidence (float), method (str), notes (str)
    """
    system = (
        "Sen product data extractor agentisan. Vazifa: Width/Height/Length (mm) va Weight (g) qaytar.\n"
        "Qoidalar:\n"
        "1) Agar rasmda qutida/etiketkada o'lcham-vazn yozilgan bo'lsa, shuni ol.\n"
        "2) Agar aniq topilmasa, vizual va product turiga qarab taxmin qil.\n"
        "3) Hech qachon 0 yoki manfiy qiymat qaytarmagin.\n"
        "4) confidence: aniq bo'lsa 0.8-1.0, taxmin bo'lsa 0.2-0.7 oralig'ida.\n"
        "5) method: exact_from_source | estimated_from_visual | estimated_from_category.\n"
        "6) notes juda qisqa bo'lsin (1-2 gap).\n\n"
        "Return ONLY valid JSON. No markdown. No extra text.\n"
        "The JSON must match this structure exactly:\n"
        "{\n"
        '  "width": integer (mm),\n'
        '  "height": integer (mm),\n'
        '  "length": integer (mm),\n'
        '  "weight": integer (g),\n'
        '  "confidence": float (0.0-1.0),\n'
        '  "method": "string",\n'
        '  "notes": "string"\n'
        "}"
    )

    user_text = (
        f"Product:\n"
        f"- name: {product_input.name}\n"
        f"- category: {product_input.category or ''}\n"
        f"- sub_category: {product_input.sub_category or ''}\n"
        f"- sub_sub_category: {product_input.sub_sub_category or ''}\n"
        f"- brand: {product_input.brand or ''}\n"
        f"Rasmlar asosida o'lcham/vaznni top."
    )

    # Build content array with text and images
    content = [{"type": "text", "text": user_text}]

    # Add images if provided
    # Qachonki venudagilar aniqroq ishlasin desa commentdan olinadi
    # if product_input.image_paths:
    #     for image_path in product_input.image_paths:
    #         if os.path.exists(image_path):
    #             # Convert local image to base64
    #             base64_image = encode_image_to_base64(image_path)
    #             mime_type = get_image_mime_type(image_path)
    #             content.append(
    #                 {
    #                     "type": "image_url",
    #                     "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
    #                 }
    #             )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {
                "role": "user",
                "content": content,
            },
        ],
    )

    result_text = response.choices[0].message.content or ""

    # Parse JSON response
    import json

    try:
        result = json.loads(result_text.strip())
        return {
            "width": int(result.get("width", 1)),
            "height": int(result.get("height", 1)),
            "length": int(result.get("length", 1)),
            "weight": int(result.get("weight", 1)),
            "confidence": result.get("confidence", 0.5),
            "method": result.get("method", "estimated_from_category"),
            "notes": result.get("notes", ""),
        }
    except (json.JSONDecodeError, ValueError, TypeError) as e:
        # Return default values if parsing fails
        print(f"Warning: Failed to parse product params: {e}")
        print(f"Response was: {result_text}")
        return {
            "width": 1,
            "height": 1,
            "length": 1,
            "weight": 1,
            "confidence": 0.0,
            "method": "default_fallback",
            "notes": "Failed to parse AI response",
        }
