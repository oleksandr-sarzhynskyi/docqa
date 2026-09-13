import { useNavigate } from "react-router-dom";

export default function Layout({ children }) {
  const navigate = useNavigate();

  function handleLogout() {
    localStorage.removeItem("token");
    navigate("/");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <span className="brand">DocQA</span>
        <button className="btn-ghost" onClick={handleLogout}>
          Log out
        </button>
      </header>
      <main className="content">{children}</main>
    </div>
  );
}