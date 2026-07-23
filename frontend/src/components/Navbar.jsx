import React from "react";
import { Link, NavLink } from "react-router-dom";
import { Bot, Menu, Play, X } from "lucide-react";

const links = [
  ["Home", "/"],
  ["Interview", "/interview"],
  ["Dashboard", "/dashboard"],
  ["History", "/history"],
  ["About", "/about"],
];

export default function Navbar() {
  const [open, setOpen] = React.useState(false);
  
  // Basic auth state using localStorage
  const [user, setUser] = React.useState(() => {
    const userStr = localStorage.getItem("user");
    return userStr ? JSON.parse(userStr) : null;
  });

  React.useEffect(() => {
    const handleAuth = () => {
      const userStr = localStorage.getItem("user");
      setUser(userStr ? JSON.parse(userStr) : null);
    };
    window.addEventListener("auth_change", handleAuth);
    return () => window.removeEventListener("auth_change", handleAuth);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.dispatchEvent(new Event("auth_change"));
    window.location.href = "/"; // Refresh and go home
  };

  return (
    <header className="navbar">
      <Link className="brand" to="/">
        <span className="brand-mark">
          <Bot color="#050810" size={18} />
        </span>
        HireSense AI
      </Link>

      <nav className={`nav-links ${open ? "open" : ""}`}>
        {links.map(([label, to]) => (
          <NavLink
            className={({ isActive }) => (isActive ? "active" : "")}
            key={to}
            to={to}
            onClick={() => setOpen(false)}
          >
            {label}
          </NavLink>
        ))}
      </nav>

      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        {user ? (
          <>
            <span style={{ fontSize: "13px", color: "var(--text-dim)", marginRight: 8 }}>
              {user.full_name || user.email}
            </span>
            <button 
              onClick={handleLogout} 
              className="ghost-link as-button" 
              style={{ padding: "8px 16px", fontSize: "13px" }}
            >
              Log out
            </button>
          </>
        ) : (
          <>
            <Link className="ghost-link" to="/login" style={{ padding: "8px 16px", fontSize: "13px" }}>
              Log in
            </Link>
            <Link className="primary-link" to="/signup" style={{ padding: "8px 16px", fontSize: "13px" }}>
              Sign up
            </Link>
          </>
        )}
        <Link className="nav-cta" to="/interview" style={{ marginLeft: 8 }}>
          <Play size={14} />
          Start Interview
        </Link>
        <button
          className="nav-toggle"
          aria-label="Toggle menu"
          onClick={() => setOpen((o) => !o)}
        >
          {open ? <X size={18} /> : <Menu size={18} />}
        </button>
      </div>
    </header>
  );
}
