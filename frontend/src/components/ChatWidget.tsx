import { FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import { useLocation } from "react-router-dom";
import { fetchHistory, sendChat } from "../api";
import { useShop } from "../shop";
import type { ChatMessage } from "../types";

const SUGGESTIONS = [
  "What hoodies do you have?",
  "What's in stock in a medium?",
  "Do you have this in another color?",
  "Compare the Basic Hoodie Big Yale and the Champion Full Zip Hood",
];

export default function ChatWidget() {
  const { user } = useShop();
  const { setMatches } = useShop();
  const location = useLocation();
  // The widget sits outside <Routes>, so useParams() is empty. Read the id from the URL.
  const productMatch = location.pathname.match(/^\/products\/([^/]+)$/);
  const productId = productMatch ? decodeURIComponent(productMatch[1]) : null;
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [error, setError] = useState("");
  const endRef = useRef<HTMLDivElement>(null);
  const loadedFor = useRef<number | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy, open]);

  useEffect(() => {
    if (!user) {
      loadedFor.current = null;
      return;
    }
    if (loadedFor.current === user.id) return;
    loadedFor.current = user.id;
    fetchHistory()
      .then((res) => {
        setMessages(res.messages);
        const lastWithCards = [...res.messages].reverse().find((msg) => msg.products && msg.products.length > 0);
        if (lastWithCards?.products) setMatches(lastWithCards.products);
      })
      .catch(() => {
        /* guest-style chat still works if history fails */
      });
  }, [user, setMatches]);

  async function submit(text: string) {
    const message = text.trim();
    if (!message || busy) return;
    setInput("");
    setError("");
    setOpen(true);
    setMessages((current) => [...current, { role: "user", content: message }]);
    setBusy(true);
    try {
      const result = await sendChat(message, location.pathname, productId);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: result.reply, products: result.products },
      ]);
      if (result.products.length > 0) setMatches(result.products);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The shop assistant is unavailable.");
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    void submit(input);
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void submit(input);
    }
  }

  return (
    <div className={`chat-dock ${open ? "open" : ""}`}>
      {open && (
        <section className="chat" aria-label="Campus Customs chat">
          <header className="chat__bar">
            <div>
              <strong>Shop assistant</strong>
              <span>{user ? `Chatting as ${user.first_name}` : "Ask about price and stock"}</span>
            </div>
            <button type="button" className="icon-button" onClick={() => setOpen(false)} aria-label="Close chat">
              ×
            </button>
          </header>
          {productId && (
            <p className="chat__context">Looking at this item — “this” means the page you’re on.</p>
          )}
          <div className="chat__log">
            {messages.length === 0 && (
              <p className="chat__empty">
                Ask what we have on the shelf. Prices and quantities come from the shop database, not a guess.
              </p>
            )}
            {messages.map((message, index) => (
              <article key={`${message.role}-${index}`} className={`bubble ${message.role}`}>
                {message.role === "assistant" ? <Markdown>{message.content}</Markdown> : <p>{message.content}</p>}
              </article>
            ))}
            {busy && (
              <p className="bubble assistant pending" aria-live="polite">
                Checking the stock book
                <span className="typing" aria-hidden>
                  <i />
                  <i />
                  <i />
                </span>
              </p>
            )}
            {error && <p className="chat__error">{error}</p>}
            <div ref={endRef} />
          </div>
          <div className="chat__suggestions">
            {SUGGESTIONS.map((prompt) => (
              <button key={prompt} type="button" onClick={() => void submit(prompt)} disabled={busy}>
                {prompt}
              </button>
            ))}
          </div>
          <form className="chat__form" onSubmit={onSubmit}>
            <textarea
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={onKeyDown}
              placeholder="Ask about a hoodie, a size, a price…"
              rows={2}
              aria-label="Message the shop assistant"
            />
            <button type="submit" disabled={busy || !input.trim()}>
              Send
            </button>
          </form>
        </section>
      )}
      <button type="button" className="chat-launcher" onClick={() => setOpen((value) => !value)}>
        <span aria-hidden>✿</span>
        {open ? "Hide chat" : "Ask the shop"}
      </button>
    </div>
  );
}
