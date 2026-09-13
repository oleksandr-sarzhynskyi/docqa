import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { signup } from "../api/client";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await signup(email, password);
      localStorage.setItem("token", data.access_token);
      navigate("/collections");
    } catch (err) {
      setError("Could not create account. Email may already be taken.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-screen">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1 className="auth-title">Create your account</h1>
        <p className="auth-subtitle">Start asking questions of your documents.</p>

        <label className="field">
          <span>Email</span>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>

        <label className="field">
          <span>Password</span>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
        </label>

        {error && <p className="form-error">{error}</p>}

        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? "Creating account..." : "Sign up"}
        </button>

        <p className="auth-switch">
          Already have an account? <Link to="/">Log in</Link>
        </p>
      </form>
    </div>
  );
}