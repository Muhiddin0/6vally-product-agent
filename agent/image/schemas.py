"""Image generation schemas."""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ImageGenRequest(BaseModel):
    """Request schema for image generation."""

    model_config = ConfigDict(extra="forbid")

    template_image_path: str = Field(..., description="Path to template/poster image")
    product_image_path: str = Field(..., description="Path to product image")
    mask_image_path: Optional[str] = Field(
        None, description="Path to mask image (optional)"
    )
    product_params: str = Field(..., description="Product parameters/description")
    size: str = Field(default="1024x1536", description="Image size")
    output_path: Optional[str] = Field(None, description="Output file path")


class ImageGenResponse(BaseModel):
    """Response schema for image generation."""

    model_config = ConfigDict(extra="forbid")

    success: bool = Field(..., description="Whether generation was successful")
    image_path: Optional[str] = Field(None, description="Path to generated image")
    error: Optional[str] = Field(None, description="Error message if generation failed")
