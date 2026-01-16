"""Product schemas - single source of truth for product data structures."""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field, ConfigDict, conint, constr


class ProductGenSchema(BaseModel):
    """AI agent generated product JSON schema (Russian only)."""

    model_config = ConfigDict(extra="forbid")

    name: constr(min_length=1) = Field(..., description="Product name in Russian")
    description: constr(min_length=1) = Field(
        ..., description="Product description in Russian"
    )
    meta_title: constr(min_length=1) = Field(..., description="Meta title in Russian")
    meta_description: constr(min_length=1) = Field(
        ..., description="Meta description in Russian"
    )

    # Tags are a simple list
    tags: List[constr(min_length=1)] = Field(
        default_factory=list, description="5-10 lowercase tags, no duplicates"
    )

    stock: conint(ge=0) = Field(default=5, description="Available stock quantity")
