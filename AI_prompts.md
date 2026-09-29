# Vibe coder prompts

This is the log of what I typed to my vibe coder (Cursor agent). I gave the whole assignment in one request instead of one problem at a time, so most sections share the same opening prompt. The follow-ups are listed under the problem they fixed.

**Opening prompt (used for every problem):**

> [attached 1A.pdf … 13.pdf] Please work on these PDF request and give me a GitHub repo URL for this assignment with your app code to submit. I need an URL as output.

I sent this same prompt in two separate chats because the first chat did not finish the whole assignment.

**Re-check prompt (used for every problem):**

> [attached 1A.pdf … 13.pdf] now, study all these again, and check if the requirement fulfill. 100% correct. if not correct, please update it and refresh everything. eventually I will submit a GitHub repo URL for this assignment with your app code. please zip the app code and also give me the link for submission.

## Problem 1: Vibe coder prompts

Prompt: the opening prompt above.

Follow-up: "please write the proper prompt. you need to help me with this submission." The first version of this file listed per-problem prompts I had not actually typed, so I had it rewritten to show my real prompts.

## Problem 2: Analyze the database

Prompt: the opening prompt above. The result is the table and field notes in `output/harness.md`.

Follow-up: none needed.

## Problem 3: Build the Campus Customs website

Prompt: the opening prompt above.

Follow-up: none needed. The nav, Products grid, product detail page, and chat panel were in place from the first chat.

## Problem 4: Create account and login

Prompt: the opening prompt above.

Follow-up: the re-check prompt. It tested logging in as `test@campuscustoms.yale.edu` / `password` and creating a brand-new account, and confirmed the new password was stored as a PBKDF2 hash.

## Problem 5: PydanticAI agent backend

Prompt: the opening prompt above.

Follow-up: none needed. While testing, the chat first said it "could not reach the model" because the backend was running without network access. Restarting it fixed that, and no code change was needed.

## Problem 6: Tools for product info and stock

Prompt: the opening prompt above.

Follow-up: none needed. Asked the price and XL stock of the Champion Reverse Weave Hoodie, the chat answered $68 and said XL is out of stock, which matches the database.

## Problem 7: Chat search that updates the page

Prompt: the opening prompt above.

Follow-up: none needed. "What hoodies do you have?" put 8 hoodie cards on the page, and clicking one opened the detail page.

## Problem 8: Customer memory

Prompt: the opening prompt above.

Follow-up: the second send of the opening prompt. Testing showed the chat did not know which product page I was on: it asked "which item did you mean?" even though I was looking at a hoodie. The chat panel lives outside the page routes, so it never received the product id. It was fixed to read the id from the page address. After that, "Do you have this in pink? And what is my name?" was answered correctly and saved to my chat history.

## Problem 9: Usability improvements

Prompt: the opening prompt above.

Follow-up: none needed. The four improvements in `output/usability.md` show up in the running app: size pills and filters, suggested questions with the "looking at this item" line, in-stock search by size, and similar items when a color is missing.

## Problem 10: Style the website

Prompt: the opening prompt above.

Follow-up: none needed.

## Problem 11: Site testing

Prompt: the opening prompt above.

Follow-up: the second send of the opening prompt. The first chat had not made `output/app_check.html`, so it was added with screenshots of the stock check, the hoodie search cards, and the size pills and filters.

## Problem 12: Audit trail, safety, finish harness

Prompt: the opening prompt above.

Follow-up: the re-check prompt. It confirmed `output/audit_trail.json` keeps growing between runs instead of being wiped.

## Problem 13: Push to GitHub

Prompt: the opening prompt above.

Follow-ups:

- "submit a GitHub repo URL for this assignment with your app code." The repo could not be created because I was not signed in to GitHub, and the first sign-in codes expired.
- "i logined the github and it asked me to have a new activation code. could you give me that?" The sign-in worked, but the login could not be saved because my `~/.config` folder is owned by root. It was saved to another folder instead, and the public repo was created.
- The re-check prompt, which also asked for a zip of the app code.
