"""Product text generation agent."""

from agent.product.agent import generate_product_text
from agent.product.schemas import ProductGenSchema

__all__ = ["generate_product_text", "ProductGenSchema"]
