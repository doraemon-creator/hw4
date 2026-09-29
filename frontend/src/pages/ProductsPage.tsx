import { useEffect, useMemo, useState } from "react";
import { fetchProducts } from "../api";
import ProductCard from "../components/ProductCard";
import type { Product } from "../types";

const FAMILIES = [
  { id: "all", label: "All" },
  { id: "hoodie", label: "Hoodies" },
  { id: "t-shirt", label: "T-shirts" },
  { id: "crewneck", label: "Crewnecks" },
  { id: "quarter", label: "Quarter-zips" },
  { id: "jacket", label: "Jackets" },
];

function familyOf(product: Product) {
  const text = `${product.garment_type} ${product.name}`.toLowerCase();
  if (text.includes("hoodie") || text.includes("hooded")) return "hoodie";
  if (text.includes("t-shirt") || text.includes("tee")) return "t-shirt";
  if (text.includes("crew")) return "crewneck";
  if (text.includes("quarter")) return "quarter";
  if (text.includes("jacket") || text.includes("bomber")) return "jacket";
  return "other";
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [family, setFamily] = useState("all");
  const [inStock, setInStock] = useState(false);
  const [size, setSize] = useState("");
  const [sort, setSort] = useState("name");

  useEffect(() => {
    fetchProducts()
      .then((res) => setProducts(res.products))
      .catch((err: Error) => setError(err.message));
  }, []);

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase();
    let rows = products.filter((product) => {
      if (family !== "all" && familyOf(product) !== family) return false;
      if (inStock && !product.inventory.some((row) => row.in_stock)) return false;
      if (size && !product.inventory.some((row) => row.size === size && row.in_stock)) return false;
      if (!needle) return true;
      const blob = [product.name, product.garment_type, product.description, ...(product.colors || [])]
        .join(" ")
        .toLowerCase();
      return blob.includes(needle);
    });
    rows = [...rows].sort((a, b) => {
      if (sort === "price-asc") return a.price - b.price;
      if (sort === "price-desc") return b.price - a.price;
      return a.name.localeCompare(b.name);
    });
    return rows;
  }, [products, query, family, inStock, size, sort]);

  return (
    <div className="page">
      <header className="section-head">
        <div>
          <p className="eyebrow">The rack</p>
          <h1>Products</h1>
        </div>
      </header>
      <div className="filters">
        <label>
          Search
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Yale, baseball, navy…"
            aria-label="Filter products"
          />
        </label>
        <label>
          Sort
          <select value={sort} onChange={(event) => setSort(event.target.value)} aria-label="Sort products">
            <option value="name">Name</option>
            <option value="price-asc">Price, low to high</option>
            <option value="price-desc">Price, high to low</option>
          </select>
        </label>
        <label>
          Size in stock
          <select value={size} onChange={(event) => setSize(event.target.value)} aria-label="Filter by size in stock">
            <option value="">Any size</option>
            {["XS", "S", "M", "L", "XL", "XXL"].map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </label>
        <label className="check">
          <input type="checkbox" checked={inStock} onChange={(event) => setInStock(event.target.checked)} />
          In stock only
        </label>
      </div>
      <div className="chips" role="tablist" aria-label="Garment type">
        {FAMILIES.map((item) => (
          <button
            key={item.id}
            type="button"
            className={family === item.id ? "chip on" : "chip"}
            onClick={() => setFamily(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
      {error && <p className="form-error">{error}</p>}
      <p className="count">{visible.length} items</p>
      <div className="grid">
        {visible.map((product) => (
          <ProductCard key={product.product_id} product={product} />
        ))}
      </div>
    </div>
  );
}
