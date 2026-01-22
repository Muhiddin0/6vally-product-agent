"""Category and Brand selection schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class CategoryBrandSelectionSchema(BaseModel):
    """Schema for category and brand selection by AI."""

    category_id: str = Field(..., description="Selected category ID")
    category: Optional[str] = Field(None, description="Selected category name")
    sub_category_id: Optional[str] = Field(None, description="Selected sub-category ID")
    sub_category: Optional[str] = Field(None, description="Selected sub-category name")
    sub_sub_category_id: Optional[str] = Field(
        None, description="Selected sub-sub-category ID"
    )
    sub_sub_category: Optional[str] = Field(
        None, description="Selected sub-sub-category name"
    )
    sub_sub_sub_category_id: Optional[str] = Field(
        None, description="Selected sub-sub-sub-category ID"
    )
    sub_sub_sub_category: Optional[str] = Field(
        None, description="Selected sub-sub-sub-category name"
    )
    brand_id: int = Field(..., description="Selected brand ID")
