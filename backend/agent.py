"""Campus Customs shop agent.

Run the API from backend/ with: uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

try:
    from pydantic_ai.models.openai import OpenAIChatModel
except ImportError:  # older pydantic-ai
    from pydantic_ai.models.openai import OpenAIModel as OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

try:
    from pydantic_ai.usage import UsageLimits
except ImportError:  # pragma: no cover
    from pydantic_ai import UsageLimits  # type: ignore

from models import ChatAnswer, SearchResults, ShopperContext
from tools import (
    MAX_RESULTS,
    get_product_card,
    lookup_product,
)
from tools import search_catalogue as search_catalogue_db
from tools import similar_products as similar_products_db

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")

PROMPT_PATH = HERE / "prompts" / "prompt.md"
AUDIT_PATH = ROOT / "output" / "audit_trail.json"
MAX_REQUESTS = 8
RESULT_PREVIEW = 280

_audit_lock = threading.Lock()
_agent: Agent[Any, ChatAnswer] | None = None


@dataclass
class ShopperDeps:
    """Passed into every tool call so the agent knows the shopper and the page."""

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    page: str = ""
    product_id: str | None = None
    history: list[dict[str, str]] = field(default_factory=list)
    search_ids: list[str] = field(default_factory=list)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def model_name() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-5.6-sol").strip() or "gpt-5.6-sol"


def load_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Missing system prompt: {PROMPT_PATH}")
    return PROMPT_PATH.read_text(encoding="utf-8")


def _preview(value: Any) -> str:
    if hasattr(value, "model_dump"):
        text = json.dumps(value.model_dump(), ensure_ascii=False)
    elif isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, default=str)
    text = " ".join(text.split())
    if len(text) <= RESULT_PREVIEW:
        return text
    return text[: RESULT_PREVIEW - 1] + "…"


def _remember(deps: ShopperDeps, products: list[Any]) -> None:
    for product in products:
        product_id = getattr(product, "product_id", None)
        if product_id and product_id not in deps.search_ids:
            deps.search_ids.append(product_id)


def build_agent() -> Agent[ShopperDeps, ChatAnswer]:
    api_key = os.getenv("PORTKEY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is missing. Copy .env.example to .env.")
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1"),
        default_headers={"x-portkey-api-key": api_key},
        timeout=120,
    )
    model = OpenAIChatModel(model_name(), provider=OpenAIProvider(openai_client=client))
    agent = Agent(
        model,
        deps_type=ShopperDeps,
        output_type=ChatAnswer,
        instructions=load_prompt(),
    )

    @agent.instructions
    def shopper_instructions(ctx: RunContext[ShopperDeps]) -> str:
        deps = ctx.deps
        who = "a guest who is not logged in"
        if deps.email:
            name = " ".join(part for part in (deps.first_name, deps.last_name) if part) or "the shopper"
            who = f"{name} ({deps.email})"
        viewing = deps.product_id or "none"
        return (
            "This turn's shopper context:\n"
            f"- Shopper: {who}\n"
            f"- Page: {deps.page or 'unknown'}\n"
            f"- Product id on screen: {viewing}\n"
            "Use current_shopper and current_page_product instead of guessing."
        )

    @agent.tool
    def current_shopper(ctx: RunContext[ShopperDeps]) -> ShopperContext:
        """Who is chatting right now. Guests are not logged in. No password data."""
        deps = ctx.deps
        return ShopperContext(
            logged_in=bool(deps.email),
            first_name=deps.first_name,
            last_name=deps.last_name,
            email=deps.email,
            page=deps.page,
            viewing_product_id=deps.product_id,
        )

    @agent.tool
    def current_page_product(ctx: RunContext[ShopperDeps]) -> str:
        """The product page the shopper has open, if any. Use this for 'this' and 'it'."""
        if not ctx.deps.product_id:
            return json.dumps({"viewing": False, "note": "The shopper is not on a product page."})
        found = lookup_product(product_id=ctx.deps.product_id)
        if found.product is not None:
            _remember(ctx.deps, [found.product])
        return found.model_dump_json()

    @agent.tool
    def search_catalogue(ctx: RunContext[ShopperDeps], query: str) -> SearchResults:
        """Search the Campus Customs catalogue. Returns at most 8 real products.

        Args:
            query: What the shopper asked for, such as hoodies, crewnecks, or a Yale college.
        """
        results = search_catalogue_db(query, limit=MAX_RESULTS)
        _remember(ctx.deps, results.products)
        return results

    @agent.tool
    def search_in_stock(ctx: RunContext[ShopperDeps], query: str, size: str = "") -> SearchResults:
        """Search items that are actually in stock, optionally in one size.

        Args:
            query: Garment or keyword, such as hoodie or crewneck.
            size: Optional size such as M, L, or XL. Leave empty for any size.
        """
        results = search_catalogue_db(query, limit=MAX_RESULTS, size=size or None, in_stock_only=True)
        _remember(ctx.deps, results.products)
        return results

    @agent.tool
    def get_product(ctx: RunContext[ShopperDeps], product_id: str = "", name_query: str = "") -> str:
        """Look up one product's description, price, colors, and stock by size.

        Args:
            product_id: Catalogue id when you already have it.
            name_query: Name or keywords when you do not have an id.
        """
        found = lookup_product(product_id=product_id, name_query=name_query)
        if found.product is not None:
            _remember(ctx.deps, [found.product])
        return found.model_dump_json()

    @agent.tool
    def check_stock(ctx: RunContext[ShopperDeps], product_id: str = "", name_query: str = "", size: str = "") -> str:
        """Read the price and on-hand quantity for a product, optionally one size.

        Args:
            product_id: Catalogue id when you have it.
            name_query: Name words when you do not.
            size: Size to highlight, such as XL. Empty returns every size.
        """
        found = lookup_product(product_id=product_id, name_query=name_query)
        if not found.found or found.product is None:
            return found.model_dump_json()
        _remember(ctx.deps, [found.product])
        product = found.product
        wanted = (size or "").strip().upper()
        rows = product.inventory
        if wanted:
            rows = [row for row in product.inventory if row.size.upper() == wanted]
        return json.dumps(
            {
                "product_id": product.product_id,
                "name": product.name,
                "price": product.price,
                "colors": product.colors,
                "size": wanted or None,
                "inventory": [row.model_dump() for row in rows],
                "note": "Quantities are from inventory. Zero means out of stock.",
            }
        )

    @agent.tool
    def similar_products(ctx: RunContext[ShopperDeps], product_id: str) -> SearchResults:
        """Other in-stock items of the same kind when the requested color or size is unavailable.

        Args:
            product_id: The item that did not match what the shopper wanted.
        """
        results = similar_products_db(product_id, limit=4)
        _remember(ctx.deps, results.products)
        return results

    return agent


def get_agent() -> Agent[ShopperDeps, ChatAnswer]:
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent


def _tool_args(part: Any) -> dict:
    args = getattr(part, "args", None)
    if args is None and hasattr(part, "args_as_dict"):
        try:
            args = part.args_as_dict()
        except Exception:
            args = {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except json.JSONDecodeError:
            args = {"raw": args}
    if not isinstance(args, dict):
        args = {"value": args}
    return args


def _events_from_messages(run_id: str, messages: list[Any], stop_reason: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    pending: dict[str, dict[str, Any]] = {}
    for message in messages:
        for part in getattr(message, "parts", []) or []:
            kind = type(part).__name__
            tool_name = getattr(part, "tool_name", None)
            call_id = getattr(part, "tool_call_id", None)
            if tool_name and kind.endswith("CallPart"):
                event = {
                    "timestamp": utc_now(),
                    "run_id": run_id,
                    "tool_name": tool_name,
                    "args": _tool_args(part),
                    "result": "",
                    "stop_reason": "continue",
                }
                events.append(event)
                if call_id:
                    pending[call_id] = event
            elif tool_name and "Return" in kind:
                event = pending.get(call_id or "")
                content = getattr(part, "content", None)
                summary = _preview(content)
                if event is None:
                    events.append(
                        {
                            "timestamp": utc_now(),
                            "run_id": run_id,
                            "tool_name": tool_name,
                            "args": {},
                            "result": summary,
                            "stop_reason": "continue",
                        }
                    )
                else:
                    event["result"] = summary
    events.append(
        {
            "timestamp": utc_now(),
            "run_id": run_id,
            "tool_name": "",
            "args": {},
            "result": stop_reason,
            "stop_reason": stop_reason,
        }
    )
    return events


def append_audit(events: list[dict[str, Any]]) -> None:
    """Append events. Never replaces an existing trail with an empty file."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _audit_lock:
        existing: list[Any] = []
        if AUDIT_PATH.exists():
            raw = AUDIT_PATH.read_text(encoding="utf-8").strip()
            if raw:
                parsed = json.loads(raw)
                if not isinstance(parsed, list):
                    raise RuntimeError("audit_trail.json is not a list; refusing to overwrite it.")
                existing = parsed
        existing.extend(events)
        AUDIT_PATH.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _history_block(history: list[dict[str, str]]) -> str:
    if not history:
        return ""
    lines = ["Recent conversation with this shopper:"]
    for turn in history[-8:]:
        role = turn.get("role", "user")
        content = " ".join((turn.get("content") or "").split())
        if len(content) > 400:
            content = content[:399] + "…"
        lines.append(f"- {role}: {content}")
    return "\n".join(lines)


async def run_chat(
    message: str,
    *,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
    page: str = "",
    product_id: str | None = None,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    deps = ShopperDeps(
        first_name=first_name,
        last_name=last_name,
        email=email,
        page=page,
        product_id=product_id,
        history=history or [],
    )
    pieces = [_history_block(deps.history), f"Shopper message:\n{message.strip()}"]
    user_prompt = "\n\n".join(piece for piece in pieces if piece)
    run_id = uuid.uuid4().hex[:12]
    stop_reason = "final_output"
    try:
        result = await get_agent().run(
            user_prompt,
            deps=deps,
            usage_limits=UsageLimits(request_limit=MAX_REQUESTS),
        )
    except Exception as exc:
        stop_reason = "error"
        append_audit(
            [
                {
                    "timestamp": utc_now(),
                    "run_id": run_id,
                    "tool_name": "",
                    "args": {"message": message[:180]},
                    "result": type(exc).__name__,
                    "stop_reason": stop_reason,
                }
            ]
        )
        raise

    answer = result.output
    messages = result.all_messages()
    chosen = [product_id for product_id in answer.product_ids if product_id][:MAX_RESULTS]
    if not chosen:
        chosen = deps.search_ids[:MAX_RESULTS]
    cards = []
    for product_id in chosen:
        card = get_product_card(product_id)
        if card is not None:
            cards.append(card.model_dump())
    append_audit(_events_from_messages(run_id, messages, stop_reason))
    return {
        "reply": answer.reply,
        "products": cards,
        "run_id": run_id,
        "model": model_name(),
    }
