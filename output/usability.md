# Usability notes

## Front end

### Size pills and an in-stock filter

What: Every product card shows XS–XXL. A size in stock is green, a size with only a few left is gold, and a sold-out size is struck through. The Products page can also hide anything with no stock, and it can filter by hoodie, tee, crewneck, quarter-zip, or jacket, or sort by price.

Why: A shopper on Broadway asks “do you have this in a medium?” before they care about the story on the shirt. Showing the count on the card, and letting them hide sold-out rows, saves a trip into a product that they cannot buy.

### Suggested questions and a “this item” chip

What: The chat offers three starter questions (hoodies, mediums in stock, another color). On a product page a line in the chat says the assistant already knows which item is open.

Why: People do not know what to type in a store chat. The prompts point them at the questions the database can actually answer, and the chip stops the “which shirt?” round-trip when they are already looking at one.

## Agent and backend

### In-stock search by size

What: `search_in_stock` takes a garment query and an optional size and drops rows whose quantity is 0 in that size. `low_stock` is set when 1–3 remain, and the prompt tells the agent to mention it.

Why: “What medium hoodies are in stock?” should not list a hoodie whose medium is gone. The shopper gets items they can walk out with, and a short warning when the size is about to sell through.

### Similar items when the color is missing

What: If the requested color is not on the product, the agent is told to say so and call `similar_products`, which returns other in-stock items of the same kind. Those ids become cards on the page. Search itself also refuses to invent a color: a color word in the query has to appear on the row.

Why: “Do you have this in pink?” is a common dead end. An honest no, plus something else on the rack, keeps the shopper in the store instead of ending the chat.
