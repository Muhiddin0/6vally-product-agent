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

