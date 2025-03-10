import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api/client.js";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const account = await login(email, password);
      onLogin?.(account);
      navigate("/");
    } catch (err) {
      setError(err.status === 401 ? "Email or password is incorrect." : "Sign-in is unavailable right now.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="login">
      <form className="card" onSubmit={submit}>
        <h1>Sign in to Harborline Book</h1>
        <label>
          Work email
          <input type="email" autoComplete="username" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label>
          Password
          <input
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="button primary" disabled={busy}>
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <p className="muted small">
          SSO customers: use the link in your onboarding email. Need help? support@harborline.example
        </p>
      </form>
    </section>
  );
}
