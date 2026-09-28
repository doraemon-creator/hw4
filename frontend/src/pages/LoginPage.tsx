import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../api";
import { useShop } from "../shop";

export default function LoginPage() {
  const { setUser } = useShop();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const result = await login(email, password);
      setUser(result.user, result.token);
      navigate("/products");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not log in.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page narrow">
      <p className="eyebrow">Welcome back</p>
      <h1>Log in</h1>
      <form className="stack" onSubmit={onSubmit}>
        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required autoComplete="email" />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            autoComplete="current-password"
          />
        </label>
        {error && <p className="form-error">{error}</p>}
        <button className="button" type="submit" disabled={busy}>
          {busy ? "Checking…" : "Log in"}
        </button>
      </form>
      <p className="fine">
        New here? <Link to="/register">Create an account</Link>
      </p>
    </div>
  );
}
