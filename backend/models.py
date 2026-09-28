"""Pydantic models for the Campus Customs shop and chatbot.

Lookup models carry database fields the agent must quote exactly.
The chat answer only names product ids. The API fills in price, stock,
and images from SQLite so a model cannot invent a number the page then shows.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SizeStock(BaseModel):
    """One size row from inventory."""

    size: str
    quantity: int = Field(description="Units on hand. Zero means that size is out of stock.")
    in_stock: bool
    low_stock: bool = Field(description="True when the size is still available but only 1–3 are left.")


class ProductCard(BaseModel):
    """A catalogue row plus stock, shaped for the website and for tool results."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    search_tags: list[str] = Field(description="Words shoppers use that should find this item.")
    image_file_path: str
    image_url: str
    price: float = Field(description="Shelf price in dollars, copied from catalogue.price.")
    inventory: list[SizeStock]
    total_stock: int
    matched_on: str = Field(
        default="",
        description="Why search returned this row, so the agent can explain the match.",
    )


class ProductLookup(BaseModel):
    """Full read of one product. Price and quantities are database values only."""

    found: bool
    product: ProductCard | None = None
    note: str = ""


class SearchResults(BaseModel):
    """Catalogue search capped so the page and the model stay on a short list."""

    query: str
    size: str | None = None
    count: int
    capped: bool = Field(description="True when more rows matched than the result cap allows.")
    products: list[ProductCard]


class ShopperContext(BaseModel):
    """Who is chatting. Guests have no email. Never includes a password hash."""

    logged_in: bool
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    page: str = ""
    viewing_product_id: str | None = None


class ChatAnswer(BaseModel):
    """What the website receives from the agent, before ids are turned into cards."""

    reply: str = Field(description="Plain answer for the shopper. Quote only prices and quantities tools returned.")
    product_ids: list[str] = Field(
        default_factory=list,
        description="Catalogue ids to render as cards. Empty when the answer is not about specific items.",
    )


class AuditEvent(BaseModel):
    """One line in the append-only audit trail."""

    timestamp: str
    run_id: str
    tool_name: str = ""
    args: dict = Field(default_factory=dict)
    result: str = ""
    stop_reason: str
