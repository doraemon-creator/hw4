"""Campus Customs API.

Run from the backend folder:
    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agent import model_name, run_chat
from tools import card_from_row, connect, db_path, ensure_chat_table, resolve_media

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
load_dotenv(ROOT.parent / ".env")

PBKDF2_ROUNDS = 120_000
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 14
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = FastAPI(title="Campus Customs", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RegisterBody(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: str
    password: str = Field(min_length=8, max_length=200)


class LoginBody(BaseModel):
    email: str
    password: str = Field(min_length=1, max_length=200)


class ChatBody(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    page: str = ""
    product_id: str | None = None


def session_secret() -> bytes:
    return os.getenv("SESSION_SECRET", "campus-customs-local-session").encode()


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, salt, digest = stored.split("$", 2)
    except ValueError:
        return False
    if algo != "pbkdf2_sha256" or not salt or not digest:
        return False
    check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), PBKDF2_ROUNDS).hex()
    return hmac.compare_digest(check, digest)


def make_token(user_id: int) -> str:
    exp = int(time.time()) + TOKEN_TTL_SECONDS
    payload = f"{user_id}:{exp}"
    sig = hmac.new(session_secret(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def read_token(token: str) -> int | None:
    parts = token.split(":")
    if len(parts) != 3:
        return None
    user_id_raw, exp_raw, sig = parts
    payload = f"{user_id_raw}:{exp_raw}"
    expected = hmac.new(session_secret(), payload.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return None
    try:
        if int(exp_raw) < int(time.time()):
            return None
        return int(user_id_raw)
    except ValueError:
        return None


def public_user(row: sqlite3.Row) -> dict:
    first = row["first_name"] or ""
    last = row["last_name"] or ""
    if not first and not last and row["name"]:
        bits = row["name"].split(" ", 1)
        first = bits[0]
        last = bits[1] if len(bits) > 1 else ""
    return {
        "id": row["id"],
        "first_name": first,
        "last_name": last,
        "name": row["name"],
        "email": row["email"],
    }


def user_by_id(user_id: int) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def optional_user(authorization: str | None = Header(default=None)) -> dict | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    user_id = read_token(authorization.split(" ", 1)[1].strip())
    if user_id is None:
        return None
    row = user_by_id(user_id)
    if row is None:
        return None
    return public_user(row)


def require_user(user: dict | None = Depends(optional_user)) -> dict:
    if user is None:
        raise HTTPException(status_code=401, detail="Log in to continue.")
    return user


@app.get("/api/health")
def health():
    ready = db_path().exists()
    return {"ok": ready, "database": db_path().name, "model": model_name()}


@app.get("/api/products")
def list_products():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        products = [card_from_row(conn, row).model_dump() for row in rows]
    return {"count": len(products), "products": products}


@app.get("/api/products/{product_id}")
def product_detail(product_id: str):
    with connect() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="That item is not in the catalogue.")
        return card_from_row(conn, row).model_dump()


@app.get("/media/{file_path:path}")
def media(file_path: str):
    path = resolve_media(file_path)
    if path is None:
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(path)


@app.post("/api/register")
def register(body: RegisterBody):
    email = body.email.strip().lower()
    if not EMAIL_RE.match(email):
        raise HTTPException(status_code=400, detail="Enter a valid email.")
    first = body.first_name.strip()
    last = body.last_name.strip()
    full_name = f"{first} {last}".strip()
    password_hash = hash_password(body.password)
    try:
        with connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO users (name, email, password_hash, first_name, last_name)
                VALUES (?, ?, ?, ?, ?)
                """,
                (full_name, email, password_hash, first, last),
            )
            conn.commit()
            user_id = int(cur.lastrowid)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="An account with that email already exists.") from None
    row = user_by_id(user_id)
    assert row is not None
    user = public_user(row)
    return {"token": make_token(user_id), "user": user}


@app.post("/api/login")
def login(body: LoginBody):
    email = body.email.strip().lower()
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row is None or not verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    return {"token": make_token(int(row["id"])), "user": public_user(row)}


@app.get("/api/me")
def me(user: dict = Depends(require_user)):
    return user


def _history(user_id: int) -> list[dict]:
    with connect() as conn:
        ensure_chat_table(conn)
        rows = conn.execute(
            """
            SELECT role, content, products_json, created_at
            FROM chat_messages
            WHERE user_id = ?
            ORDER BY id
            """,
            (user_id,),
        ).fetchall()
    messages = []
    for row in rows:
        products = []
        if row["products_json"]:
            try:
                import json

                parsed = json.loads(row["products_json"])
                if isinstance(parsed, list):
                    products = parsed
            except json.JSONDecodeError:
                products = []
        messages.append(
            {
                "role": row["role"],
                "content": row["content"],
                "products": products,
                "created_at": row["created_at"],
            }
        )
    return messages


@app.get("/api/chat/history")
def chat_history(user: dict = Depends(require_user)):
    return {"messages": _history(user["id"])}


def _save_turn(user_id: int, role: str, content: str, products: list | None) -> None:
    import json

    payload = json.dumps(products or [], ensure_ascii=False)
    with connect() as conn:
        ensure_chat_table(conn)
        conn.execute(
            """
            INSERT INTO chat_messages (user_id, role, content, products_json)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, role, content, payload),
        )
        conn.commit()


@app.post("/api/chat")
async def chat(body: ChatBody, user: dict | None = Depends(optional_user)):
    history = []
    if user is not None:
        history = [
            {"role": item["role"], "content": item["content"]}
            for item in _history(user["id"])
        ]
    try:
        result = await run_chat(
            body.message,
            first_name=(user or {}).get("first_name"),
            last_name=(user or {}).get("last_name"),
            email=(user or {}).get("email"),
            page=body.page,
            product_id=body.product_id,
            history=history,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The shop assistant could not reach the model. Check PORTKEY_API_KEY and try again.",
        ) from exc
    if user is not None:
        _save_turn(user["id"], "user", body.message.strip(), None)
        _save_turn(user["id"], "assistant", result["reply"], result["products"])
    return result
