import { useShop } from "../shop";
import ProductCard from "./ProductCard";

export default function MatchStrip() {
  const { matches } = useShop();
  if (matches.length === 0) return null;
  return (
    <section className="matches" aria-label="Items from the shop assistant">
      <div className="matches__head">
        <p className="eyebrow">From the shop assistant</p>
        <h2>Pulled from the shelf</h2>
      </div>
      <div className="matches__row">
        {matches.map((product) => (
          <ProductCard key={product.product_id} product={product} />
        ))}
      </div>
    </section>
  );
}
