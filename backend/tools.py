"""Database lookups the shop agent is allowed to use.

Every price and quantity in here is read from campus_customs.db.
Nothing in this file writes catalogue or inventory rows.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from models import ProductCard, ProductLookup, SearchResults, SizeStock

ROOT = Path(__file__).resolve().parent.parent
MAX_RESULTS = 8
LOW_STOCK_AT = 3

FAMILIES: dict[str, tuple[str, ...]] = {
    "hoodie": ("hoodie", "hooded"),
    "hoodies": ("hoodie", "hooded"),
    "crewneck": ("crewneck", "crew neck", "crew-neck"),
    "crewnecks": ("crewneck", "crew neck", "crew-neck"),
    "sweatshirt": ("sweatshirt", "crewneck", "hoodie"),
    "t-shirt": ("t-shirt", "t shirt", "tee"),
    "tshirt": ("t-shirt", "t shirt", "tee"),
    "tee": ("t-shirt", "tee"),
    "tees": ("t-shirt", "tee"),
    "quarter-zip": ("quarter-zip", "quarter zip", "1/4"),
    "quarterzip": ("quarter-zip", "quarter zip"),
    "jacket": ("jacket", "bomber"),
    "jackets": ("jacket", "bomber"),
    "fleece": ("fleece",),
}

COLOR_WORDS = (
    "pink",
    "navy",
    "white",
    "gray",
    "grey",
    "black",
    "red",
    "green",
    "blue",
    "yellow",
    "purple",
    "gold",
    "heather",
    "natural",
    "orange",
    "brown",
    "maroon",
    "crimson",
)

SIZE_WORDS = {"xs": "XS", "s": "S", "m": "M", "l": "L", "xl": "XL", "xxl": "XXL"}


def data_root() -> Path:
    for candidate in (ROOT / "data", ROOT.parent / "data"):
        if (candidate / "campus_customs.db").exists() or (candidate / "products").is_dir():
            return candidate
    return ROOT / "data"


def db_path() -> Path:
    return data_root() / "campus_customs.db"


def connect() -> sqlite3.Connection:
    path = db_path()
    if not path.exists():
        raise FileNotFoundError(
            "Missing data/campus_customs.db. Unzip the homework data pack at the project root."
        )
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def ensure_chat_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            products_json TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()


def _json_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return [part.strip() for part in raw.split(",") if part.strip()]
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return [str(parsed)]


def _sizes_for(conn: sqlite3.Connection, product_id: str) -> list[SizeStock]:
    rows = conn.execute(
        """
        SELECT size, quantity
        FROM inventory
        WHERE product_id = ?
        ORDER BY CASE size
            WHEN 'XS' THEN 1 WHEN 'S' THEN 2 WHEN 'M' THEN 3
            WHEN 'L' THEN 4 WHEN 'XL' THEN 5 WHEN 'XXL' THEN 6
            ELSE 7 END
        """,
        (product_id,),
    ).fetchall()
    sizes: list[SizeStock] = []
    for row in rows:
        quantity = int(row["quantity"])
        sizes.append(
            SizeStock(
                size=row["size"],
                quantity=quantity,
                in_stock=quantity > 0,
                low_stock=0 < quantity <= LOW_STOCK_AT,
            )
        )
    return sizes


def card_from_row(conn: sqlite3.Connection, row: sqlite3.Row, matched_on: str = "") -> ProductCard:
    product_id = row["product_id"]
    image_file = row["image_file_path"]
    filename = Path(image_file).name
    sizes = _sizes_for(conn, product_id)
    return ProductCard(
        product_id=product_id,
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=_json_list(row["colors"]),
        search_tags=_json_list(row["search_tags"]),
        image_file_path=image_file,
        image_url=f"/media/products/{filename}",
        price=float(row["price"]),
        inventory=sizes,
        total_stock=sum(size.quantity for size in sizes),
        matched_on=matched_on,
    )


def get_product_card(product_id: str) -> ProductCard | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            return None
        return card_from_row(conn, row, matched_on="id")


def _tokens(query: str) -> list[str]:
    return [part for part in re.findall(r"[a-z0-9][a-z0-9'+/-]*", query.lower()) if part not in {"a", "the", "do", "you", "have", "what", "show", "me", "in", "of", "for", "and", "or", "with"}]


def _family_needles(tokens: list[str]) -> list[str]:
    needles: list[str] = []
    for token in tokens:
        for needle in FAMILIES.get(token, ()):
            if needle not in needles:
                needles.append(needle)
    return needles


def _color_needles(tokens: list[str]) -> list[str]:
    found: list[str] = []
    text = " ".join(tokens)
    for color in COLOR_WORDS:
        if color in tokens or color in text:
            if color not in found:
                found.append(color)
    if "grey" in found and "gray" not in found:
        found.append("gray")
    if "gray" in found and "grey" not in found:
        found.append("grey")
    return found


def normalize_size(size: str | None) -> str | None:
    if not size:
        return None
    key = size.strip().lower().replace("-", "")
    return SIZE_WORDS.get(key)


def search_catalogue(query: str, limit: int = MAX_RESULTS, size: str | None = None, in_stock_only: bool = False) -> SearchResults:
    """Rank catalogue rows. Family and color words narrow the list. Cap is 8."""
    limit = max(1, min(int(limit or MAX_RESULTS), MAX_RESULTS))
    tokens = _tokens(query)
    family = _family_needles(tokens)
    colors = _color_needles(tokens)
    wanted_size = normalize_size(size)
    scored: list[tuple[int, str, sqlite3.Row]] = []

    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue").fetchall()
        for row in rows:
            hay_name = row["name"].lower()
            hay_type = row["garment_type"].lower()
            hay_desc = row["description"].lower()
            hay_tags = row["search_tags"].lower()
            hay_colors = row["colors"].lower()
            blob = " ".join((hay_name, hay_type, hay_desc, hay_tags, hay_colors))
            if family and not any(needle in blob for needle in family):
                continue
            if colors and not any(color in hay_colors or color in hay_name or color in hay_tags for color in colors):
                continue
            sizes = _sizes_for(conn, row["product_id"])
            if wanted_size is not None:
                size_row = next((item for item in sizes if item.size.lower() == wanted_size.lower()), None)
                if size_row is None or (in_stock_only and not size_row.in_stock):
                    continue
            elif in_stock_only and not any(item.in_stock for item in sizes):
                continue
            score = 0
            reasons: list[str] = []
            if family:
                score += 5
                reasons.append("type")
            if colors:
                score += 4
                reasons.append("color")
            for token in tokens:
                if token in FAMILIES or token in COLOR_WORDS or token in SIZE_WORDS:
                    continue
                if token in hay_name:
                    score += 4
                    reasons.append(token)
                elif token in hay_tags:
                    score += 3
                    reasons.append(token)
                elif token in hay_desc or token in hay_type:
                    score += 1
                    reasons.append(token)
            if not tokens:
                score = 1
            if score <= 0:
                continue
            scored.append((score, ", ".join(dict.fromkeys(reasons)), row))

        scored.sort(key=lambda item: (-item[0], item[2]["name"]))
        capped = len(scored) > limit
        chosen = scored[:limit]
        products = [card_from_row(conn, row, matched_on=reason) for _score, reason, row in chosen]

    return SearchResults(
        query=query,
        size=wanted_size,
        count=len(products),
        capped=capped,
        products=products,
    )


def lookup_product(product_id: str = "", name_query: str = "") -> ProductLookup:
    if product_id:
        card = get_product_card(product_id)
        if card is not None:
            return ProductLookup(found=True, product=card, note="Matched product_id.")
    query = name_query or product_id
    if not query:
        return ProductLookup(found=False, note="No product id or name was given.")
    results = search_catalogue(query, limit=1)
    if not results.products:
        return ProductLookup(found=False, note=f"Nothing in the catalogue matched {query!r}.")
    return ProductLookup(found=True, product=results.products[0], note="Best catalogue match.")


def similar_products(product_id: str, limit: int = 4) -> SearchResults:
    """Other in-stock items in the same garment family, excluding the one they asked about."""
    card = get_product_card(product_id)
    if card is None:
        return SearchResults(query=product_id, count=0, capped=False, products=[])
    family_query = card.garment_type
    results = search_catalogue(family_query, limit=MAX_RESULTS, in_stock_only=True)
    products = [item for item in results.products if item.product_id != product_id][: max(1, min(limit, MAX_RESULTS))]
    return SearchResults(
        query=family_query,
        count=len(products),
        capped=False,
        products=products,
    )


def resolve_media(relative: str) -> Path | None:
    """Map a /media/... path onto data/products, and refuse anything outside that folder."""
    cleaned = relative.lstrip("/")
    if cleaned.startswith("media/"):
        cleaned = cleaned[len("media/") :]
    path = (data_root() / cleaned).resolve()
    products = (data_root() / "products").resolve()
    if products not in path.parents and path != products:
        return None
    if not path.is_file():
        return None
    return path
