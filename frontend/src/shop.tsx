import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { fetchMe, getToken, setToken } from "./api";
import type { Product, Shopper } from "./types";

interface ShopState {
  user: Shopper | null;
  ready: boolean;
  matches: Product[];
  setUser: (user: Shopper | null, token: string | null) => void;
  setMatches: (products: Product[]) => void;
}

const ShopContext = createContext<ShopState | null>(null);

export function ShopProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<Shopper | null>(null);
  const [ready, setReady] = useState(false);
  const [matches, setMatches] = useState<Product[]>([]);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setReady(true);
      return;
    }
    fetchMe()
      .then(setUserState)
      .catch(() => setToken(null))
      .finally(() => setReady(true));
  }, []);

  const value = useMemo<ShopState>(
    () => ({
      user,
      ready,
      matches,
      setUser: (next, token) => {
        setToken(token);
        setUserState(next);
      },
      setMatches,
    }),
    [user, ready, matches],
  );

  return <ShopContext.Provider value={value}>{children}</ShopContext.Provider>;
}

export function useShop() {
  const value = useContext(ShopContext);
  if (!value) throw new Error("useShop must be used inside ShopProvider");
  return value;
}
