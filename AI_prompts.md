# Vibe coder prompts

## Problem 1: Vibe coder prompts

Prompt: Please work through the Campus Customs homework from the PDFs and keep a prompt log. I need the finished app in a public GitHub repo and the repo URL to submit.

Follow-up: Put one section per problem in `AI_prompts.md`, with the title and what I asked, including a follow-up when the first pass missed something. The first draft only had the overall ask and no per-problem notes.

## Problem 2: Analyze the database

Prompt: Open `data/campus_customs.db` and write down catalogue, inventory, and users in `output/harness.md`. For each field say why the shop or the chatbot needs it.

Follow-up: The users row is not just name, email, and a hash — there are also first_name and last_name, and there is already a chat_messages table. Add those to the harness. The first pass stopped at the three tables named in the prompt.

## Problem 3: Build the Campus Customs website

Prompt: Scaffold a React + Vite + TypeScript site with a nav for Home, Products, About Us, Log in, and Create account. Write Home and About in my own words using the Broadway shop as the setting, not copied site text. Products should show the catalogue photos, name, price, and a short description, and a click should open a page with a large image and the full write-up. Put a chat box in the bottom right that can call the backend later. A small FastAPI app can serve products and images for now.

## Problem 4: Create account and login

Prompt: Add create-account (first name, last name, email, password, confirm password) and login (email, password). Save new people in the users table and hash passwords so the plain password is not stored. Check that test@campuscustoms.yale.edu / password works, and that a brand-new account works too. Document the hash in the harness.

Follow-up: The seed hash is `pbkdf2_sha256$salt$hex`, and a 120,000-round SHA-256 digest matches the test user. The first version used a different hash format, so the seed login failed.

## Problem 5: PydanticAI agent backend

Prompt: Turn the chatbot into a PydanticAI agent behind FastAPI. Keep `backend/main.py` as the uvicorn app (`uvicorn main:app --reload --port 8000` from `backend/`). Put the prompt in `backend/prompts/prompt.md`, wiring in `agent.py`, tools in `tools.py`, and types in `models.py`. Give the assistant a Campus Customs voice and a chat route the widget can call. Note in the harness how the front end reaches FastAPI and how the prompt file and model are loaded.

## Problem 6: Tools for product info and stock

Prompt: Give the agent tools that read description, price, and stock by size from the database. It should not invent prices or quantities, and it should say when a size is out of stock. Tell the prompt to call those tools, add the return types in `models.py`, and list each tool in the harness with why those fields were chosen.

## Problem 7: Chat search that updates the page

Prompt: When someone asks “what hoodies do you have?”, search the catalogue and show those items as cards on the website (image, name, price, short info). Clicking a card, including one the chat just added, should still open the big product page. Explain in the prompt and the harness how the search results get onto the page.

## Problem 8: Customer memory

Prompt: If a shopper is logged in, save the chat in the database and load it when they come back. The agent should know their name and email. If they are on a product page and ask “do you have this in pink?”, the agent should know which item they mean. Guests can still chat, but only logged-in history has to persist. Write that up in the harness.

## Problem 9: Usability improvements

Prompt: Add two front-end improvements and two agent improvements that make the shop easier or the answers more accurate. Write `output/usability.md` first: what each one is and why it helps a Campus Customs shopper. Then actually build them so they show up in the running app.

I picked size-and-stock pills plus filters on the rack, suggested chat questions with a “you are looking at this item” line, an in-stock-by-size search, and a similar-items tool when the color is not in the catalogue.

## Problem 10: Style the website

Prompt: Make the site feel like a real Campus Customs storefront — type, color, hierarchy, a little motion, how products and the chat are presented. Then write a short `output/design.md` about what changed and why it should help someone stay and buy.

## Problem 11: Site testing

Prompt: Test the live site and write `output/app_check.html` with a heading, a screenshot, and a sentence or two for each check: inventory and price from the database, hoodie cards showing up after a category question, and one usability feature from problem 9. Put the images in `output/app_check_images/` and link them with relative paths.

## Problem 12: Audit trail, safety, finish harness

Prompt: Keep an append-only `output/audit_trail.json` with time, tool name, short args, short result, and stop reason. Do not wipe it between runs. Add safety rules to the prompt. Finish the harness so it covers the model fields, the tools, the safety rules, and the specs (loop limit, result cap, model, how to run both apps).

## Problem 13: Push to GitHub

Prompt: Put the project in a public GitHub repo I can submit. Do not commit `.env`, `campus_customs.db`, or the product images. Include `.env.example` with placeholders only. The layout should match the homework tree, and the README should say how to run the site after the data pack is in place. I need the repo URL.
