import { Link } from "react-router-dom";
import { money } from "../api";
import type { Product } from "../types";

export default function ProductCard({ product }: { product: Product }) {
  return (
    <Link className="card" to={`/products/${product.product_id}`}>
      <div className="card__photo">
        <img src={product.image_url} alt={product.name} />
      </div>
      <div className="card__body">
        <p className="card__type">{product.garment_type}</p>
        <h3>{product.name}</h3>
        <p className="card__price">{money(product.price)}</p>
        <p className="card__blurb">{product.description}</p>
        <ul className="sizes" aria-label="Sizes in stock">
          {product.inventory.map((size) => (
            <li
              key={size.size}
              className={size.in_stock ? (size.low_stock ? "low" : "in") : "out"}
              title={size.in_stock ? `${size.quantity} in stock` : "Out of stock"}
            >
              {size.size}
            </li>
          ))}
        </ul>
      </div>
    </Link>
  );
}
