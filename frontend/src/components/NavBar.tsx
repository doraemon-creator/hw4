import { Link, NavLink, useNavigate } from "react-router-dom";
import { useShop } from "../shop";

export default function NavBar() {
  const { user, setUser } = useShop();
  const navigate = useNavigate();

  function logout() {
    setUser(null, null);
    navigate("/");
  }

  return (
    <header className="nav">
      <Link to="/" className="brand" aria-label="Campus Customs home">
        <span className="brand__mark" aria-hidden>
          Y
        </span>
        <span>
          <strong>Campus Customs</strong>
          <em>57 Broadway</em>
        </span>
      </Link>
      <nav className="nav__links">
        <NavLink to="/" end>
          Home
        </NavLink>
        <NavLink to="/products">Products</NavLink>
        <NavLink to="/about">About Us</NavLink>
        {user ? (
          <>
            <span className="nav__hello">Hi, {user.first_name || user.name}</span>
            <button type="button" className="text-button" onClick={logout}>
              Log out
            </button>
          </>
        ) : (
          <>
            <NavLink to="/login">Log in</NavLink>
            <NavLink to="/register" className="nav__join">
              Create account
            </NavLink>
          </>
        )}
      </nav>
    </header>
  );
}
