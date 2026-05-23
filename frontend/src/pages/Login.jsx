import { motion } from "framer-motion";
import { LogIn } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { loginUser } from "../services/authApi";

const fade = {
  initial: { opacity: 0, y: 18 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] },
};

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    try {
      const data = await loginUser(email, password);
      // Store user info in localStorage for simple persistence
      localStorage.setItem("user", JSON.stringify(data.user));
      window.dispatchEvent(new Event("auth_change"));
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <motion.div className="glass-card auth-card" {...fade}>
        <div style={{ display: "flex", justifyContent: "center", marginBottom: 16 }}>
          <div className="icon-wrap" style={{ 
            width: 56, height: 56, borderRadius: "50%", 
            background: "var(--cyan-dim)", border: "1px solid rgba(47,244,216,0.2)",
            display: "flex", alignItems: "center", justifyContent: "center", color: "var(--cyan)"
          }}>
            <LogIn size={28} />
          </div>
        </div>
        <h1>Welcome back</h1>
        <p>Log in to save and access your interview results.</p>

        {error && <p className="chat-error" style={{ textAlign: "center", marginBottom: 16 }}>{error}</p>}

        <form className="auth-form" onSubmit={handleLogin}>
          <div className="input-group">
            <label htmlFor="email">Email address</label>
            <input 
              id="email" 
              type="email" 
              placeholder="name@example.com" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          <div className="input-group">
            <label htmlFor="password">Password</label>
            <input 
              id="password" 
              type="password" 
              placeholder="••••••••" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>
          <button type="submit" className="primary-link as-button auth-button" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="auth-link">
          Don't have an account? 
          <Link to="/signup">Sign up</Link>
        </div>
      </motion.div>
    </main>
  );
}
