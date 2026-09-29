# Usability notes

Four improvements: two on the front end and two on the agent and backend. Each one is in the running app.

## Front end

### 1. Search, filter, and sort on the Products page

What: The Products page has a text search, garment chips (Hoodies, T-shirts, Crewnecks, Quarter-zips, Jackets), a "Size in stock" menu (XS–XXL), an "In stock only" toggle, and sorting by name or by price in either direction. Every card also shows XS–XXL pills: green means in stock, gold means only 1–3 left, and struck-through means sold out.

Why: A shopper usually knows the garment and their size before anything else. Picking "Hoodies" and "M" cuts 102 items down to the ones they can actually buy, and the pills answer "is my size left?" without opening every product. Fewer dead ends means more people reach a product they can take home.

### 2. A chat panel that feels responsive and guides the first question

What: While the agent works, the chat shows "Checking the stock book" with three animated dots. The log auto-scrolls to the newest message. Suggested-question chips offer "What hoodies do you have?", "What's in stock in a medium?", "Do you have this in another color?", and a two-item comparison. On a product page, a line at the top says the assistant already knows which item "this" means.

Why: A silent chat box feels broken, and a model call takes a few seconds, so the typing indicator tells the shopper something is happening. The chips show the questions the database can actually answer, and the "this item" line saves a "which shirt?" round-trip.

## Agent and backend

### 3. A compare tool for two products

What: `compare_products` takes two product ids or names and returns both items with `cheaper_product_id`, `price_difference`, `more_stock_product_id`, and `sizes_in_stock_for_both`. Every number comes from the database. The prompt tells the agent to use it for "which is cheaper / which has more / which comes in my size" questions, and both items appear as cards on the page.

Why: "Should I get the $68 pullover or the $88 full-zip?" is a common in-store question. Answering from one tool call is more accurate than the model juggling two separate lookups, and the shopper sees both items side by side.

### 4. Caching so repeated lookups skip the database and the model

What: The whole catalogue with its sizes is read once and reused for 30 seconds (`CATALOGUE_CACHE_SECONDS`), so the Products page, detail pages, and every search tool share one read instead of querying SQLite for each product. Identical first-turn guest questions on the same page are answered from a 60-second reply cache (`REPLY_CACHE_SECONDS`) without calling the model. The audit trail records those as `stop_reason: "cache_hit"`. Logged-in shoppers are never served a cached reply, because their answer can depend on their name and history.

Why: The model call is the slow and costly part of a chat. When the same suggested question is clicked again, the answer comes back instantly (about 8 seconds uncached, under a second cached) at no model cost. Stock is still at most 30 seconds old, which is fine for a shop whose inventory is not changed by the website.
