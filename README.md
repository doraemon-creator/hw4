# Campus Customs shop

A small storefront for Campus Customs, the Yale gear shop at 57 Broadway, with a chatbot that reads prices and stock from a local SQLite database.

## What you need

- Python 3.11+
- Node.js 20+
- A Portkey API key for the shop assistant
- The homework data pack (not in this repo)

## Data pack

Unzip `data.zip` at the project root so you have:

```
data/campus_customs.db
data/products/
```

Image paths in the database look like `products/basic-hoodie-big-yale.jpg`. Do not commit the database or the images.

A test account is already in the database:

- Email: `test@campuscustoms.yale.edu`
- Password: `password`

## API key

Copy `.env.example` to `.env` in the project root and set `PORTKEY_API_KEY`. The backend also checks the parent folder for `.env`. The default model is `gpt-5.6-sol` (a 5.6-series model through Portkey). Override it with `OPENAI_MODEL` if you want another 5.6 or 6 series model.

## Run the backend

From the `backend/` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8000
```

## Run the front end

In another terminal, from `frontend/`:

```bash
npm install
npm run dev
```

Open http://127.0.0.1:5173. The Vite dev server proxies `/api` and `/media` to port 8000.

## What the site does

- Home, Products, About Us, Log in, and Create account
- Product photos, prices, and size counts from the database
- A chat panel in the bottom right
- Search replies that put matching product cards on the page
- Saved chat history for logged-in shoppers

Passwords are stored with PBKDF2-HMAC-SHA256 (120,000 rounds), which is the same scheme as the seed user.
