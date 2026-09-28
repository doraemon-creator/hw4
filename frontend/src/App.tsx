import { Route, Routes } from "react-router-dom";
import ChatWidget from "./components/ChatWidget";
import MatchStrip from "./components/MatchStrip";
import NavBar from "./components/NavBar";
import AboutPage from "./pages/AboutPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import ProductPage from "./pages/ProductPage";
import ProductsPage from "./pages/ProductsPage";
import RegisterPage from "./pages/RegisterPage";

export default function App() {
  return (
    <div className="shell">
      <NavBar />
      <MatchStrip />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/products/:id" element={<ProductPage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </main>
      <footer className="foot">
        <span>Campus Customs</span>
        <span>57 Broadway, New Haven</span>
        <span>Mon–Sat 9–9 · Sun 10–6</span>
      </footer>
      <ChatWidget />
    </div>
  );
}
