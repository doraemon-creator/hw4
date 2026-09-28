import type { ChatMessage, Product, Shopper } from "./types";

const TOKEN_KEY = "campus_customs_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(path, { ...init, headers });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* keep status text */
    }
    throw new Error(detail);
  }
  return (await response.json()) as T;
}

export function fetchProducts() {
  return request<{ count: number; products: Product[] }>("/api/products");
}

export function fetchProduct(id: string) {
  return request<Product>(`/api/products/${encodeURIComponent(id)}`);
}

export function register(body: {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}) {
  return request<{ token: string; user: Shopper }>("/api/register", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function login(email: string, password: string) {
  return request<{ token: string; user: Shopper }>("/api/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function fetchMe() {
  return request<Shopper>("/api/me");
}

export function fetchHistory() {
  return request<{ messages: ChatMessage[] }>("/api/chat/history");
}

export function sendChat(message: string, page: string, productId: string | null) {
  return request<{ reply: string; products: Product[] }>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ message, page, product_id: productId }),
  });
}

export function money(price: number) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(price);
}
