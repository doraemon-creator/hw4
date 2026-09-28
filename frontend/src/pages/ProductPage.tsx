import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { fetchProduct, money } from "../api";
import type { Product } from "../types";

export default function ProductPage() {
  const { id } = useParams();
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState("");
  const [size, setSize] = useState("");

  useEffect(() => {
    if (!id) return;
    setProduct(null);
    setError("");
    fetchProduct(id)
      .then((item) => {
        setProduct(item);
        const first = item.inventory.find((row) => row.in_stock);
        setSize(first?.size || item.inventory[0]?.size || "");
      })
      .catch((err: Error) => setError(err.message));
  }, [id]);

  if (error) {
    return (
      <div className="page">
        <p className="form-error">{error}</p>
        <Link to="/products">Back to products</Link>
      </div>
    );
  }
  if (!product) {
    return (
      <div className="page">
        <p>Pulling this item off the rack…</p>
      </div>
    );
  }

  const selected = product.inventory.find((row) => row.size === size);

  return (
    <div className="page detail">
      <Link className="back" to="/products">
        ← All products
      </Link>
      <div className="detail__layout">
        <div className="detail__photo">
          <img src={product.image_url} alt={product.name} />
        </div>
        <div className="detail__copy">
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="detail__price">{money(product.price)}</p>
          <p>{product.description}</p>
          <p className="colors">Colors: {product.colors.join(", ") || "see the photo"}</p>
          <h2>Sizes</h2>
          <div className="size-picker">
            {product.inventory.map((row) => (
              <button
                key={row.size}
                type="button"
                className={row.size === size ? "size-btn on" : "size-btn"}
                onClick={() => setSize(row.size)}
              >
                <strong>{row.size}</strong>
                <span>{row.in_stock ? `${row.quantity} left` : "Out"}</span>
              </button>
            ))}
          </div>
          {selected && (
            <p className={selected.in_stock ? "stock-note" : "stock-note out"}>
              {selected.in_stock
                ? `${selected.quantity} in size ${selected.size}${selected.low_stock ? " — only a few left" : ""}.`
                : `Size ${selected.size} is out of stock.`}
            </p>
          )}
          <p className="hint">Open the chat and ask “do you have this in another color?” — the assistant already knows which item this is.</p>
        </div>
      </div>
    </div>
  );
}
