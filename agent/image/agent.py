"""Image generation agent using OpenAI."""

from __future__ import annotations

import base64
import logging
import os
from typing import Optional

from core.openai_client import get_openai_client

logger = logging.getLogger(__name__)

# Get OpenAI client from core
client = get_openai_client()


def generate_poster(
    template_image_path: str,
    product_image_path: str,
    product_params: str,
    mask_image_path: Optional[str] = None,
    size: str = "1024x1536",
    output_path: Optional[str] = None,
) -> str:
    """
    Generate a poster image using template and product images.

    Args:
        template_image_path: Path to template/poster image
        product_image_path: Path to product image
        product_params: Product parameters/description
        mask_image_path: Optional path to mask image
        size: Image size (default: "1024x1536")
        output_path: Optional output file path (default: auto-generated)

    Returns:
        str: Path to generated image file

    Raises:
        FileNotFoundError: If input images are not found
        ValueError: If image generation fails
    """
    # Validate input files exist
    if not os.path.exists(template_image_path):
        raise FileNotFoundError(f"Template image not found: {template_image_path}")
    if not os.path.exists(product_image_path):
        raise FileNotFoundError(f"Product image not found: {product_image_path}")
    if mask_image_path and not os.path.exists(mask_image_path):
        raise FileNotFoundError(f"Mask image not found: {mask_image_path}")

    # Build prompt
    prompt = f"""
1-rasimdagi posterdan andoza olib 2-rasimdagi maxsulot uchun poster yaratib ber.

2-rasimdagi maxsulotning parametrlari
{product_params}
""".strip()

    logger.info(f"Generating poster image from template: {template_image_path}")

    try:
        # Prepare image files - matching rasim.py implementation exactly
        # rasim.py uses: [mask.png, poster.png]
        # So we use: [mask or template, template or product]
        image_files = []

        if mask_image_path:
            # If mask provided, use it as first image (matching rasim.py: mask.png)
            image_files.append(open(mask_image_path, "rb"))
            # Second image: template (matching rasim.py: poster.png)
            image_files.append(open(template_image_path, "rb"))
        else:
            # If no mask, use template as first image
            image_files.append(open(template_image_path, "rb"))
            # Second image: product image (to create poster for)
            image_files.append(open(product_image_path, "rb"))

        # Call OpenAI image edit API - matching rasim.py format
        result = client.images.edit(
            model="gpt-image-1",  # Using same model as rasim.py
            image=image_files,  # List of image files
            size=size,
            prompt=prompt,
        )

        # Close file handles
        for img_file in image_files:
            img_file.close()

        # Get image data
        if hasattr(result.data[0], "b64_json") and result.data[0].b64_json:
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
        elif hasattr(result.data[0], "url"):
            # If URL is returned instead of base64
            import requests

            response = requests.get(result.data[0].url)
            image_bytes = response.content
        else:
            raise ValueError("No image data returned from API")

        # Determine output path
        if not output_path:
            # Generate output path based on product image name
            base_name = os.path.splitext(os.path.basename(product_image_path))[0]
            output_dir = os.path.dirname(product_image_path) or "."
            output_path = os.path.join(output_dir, f"{base_name}_poster.png")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        # Save the image
        with open(output_path, "wb") as f:
            f.write(image_bytes)

        logger.info(f"Successfully generated poster image: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error generating poster image: {e}", exc_info=True)
        raise ValueError(f"Failed to generate poster image: {str(e)}")


def generate_poster_from_template(
    template_image_path: str,
    product_image_path: str,
    product_params: str,
    mask_image_path: Optional[str] = None,
    size: str = "1024x1536",
    output_path: Optional[str] = None,
) -> str:
    """
    Alias for generate_poster for backward compatibility.

    Generate a poster image using template and product images.
    """
    return generate_poster(
        template_image_path=template_image_path,
        product_image_path=product_image_path,
        product_params=product_params,
        mask_image_path=mask_image_path,
        size=size,
        output_path=output_path,
    )
