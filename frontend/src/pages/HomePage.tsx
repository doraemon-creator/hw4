import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchProducts } from "../api";
import ProductCard from "../components/ProductCard";
import type { Product } from "../types";

const FEATURED = [
  "basic-hoodie-big-yale",
  "the-official-y-sweater",
  "yale-crest-hoodie",
  "big-yale-tri-blend-t-shirt",
];

export default function HomePage() {
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    fetchProducts()
      .then((res) => setProducts(res.products))
      .catch(() => setProducts([]));
  }, []);

  const featured = FEATURED.map((id) => products.find((item) => item.product_id === id)).filter(
    (item): item is Product => Boolean(item),
  );
  const shown = featured.length > 0 ? featured : products.slice(0, 4);

  return (
    <div className="page home">
      <section className="hero">
        <p className="eyebrow">New Haven · since 1975</p>
        <h1>Yale gear, printed down the street.</h1>
        <p className="lede">
          Campus Customs is the family shop at 57 Broadway. We keep the classic Y sweater, the big-letter
          hoodies, and the college crests on the rack, and we print and embroider for teams and reunions in the
          shop next door.
        </p>
        <div className="hero__actions">
          <Link className="button" to="/products">
            Browse the rack
          </Link>
          <Link className="button button--ghost" to="/about">
            Visit the store
          </Link>
        </div>
        <dl className="hours">
          <div>
            <dt>Weekdays & Saturday</dt>
            <dd>9am – 9pm</dd>
          </div>
          <div>
            <dt>Sunday</dt>
            <dd>10am – 6pm</dd>
          </div>
          <div>
            <dt>Find us</dt>
            <dd>57 Broadway, New Haven</dd>
          </div>
        </dl>
      </section>
      <section>
        <div className="section-head">
          <h2>On the front table</h2>
          <Link to="/products">All products</Link>
        </div>
        <div className="grid">
          {shown.map((product) => (
            <ProductCard key={product.product_id} product={product} />
          ))}
        </div>
      </section>
    </div>
  );
}
