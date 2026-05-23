import { motion } from "framer-motion";
import { UserPlus } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { registerUser } from "../services/authApi";

const fade = {
  initial: { opacity: 0, y: 18 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.4, ease: [0.4, 0, 0.2, 1] },
};

export default function Signup() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignup = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    try {
      const data = await registerUser(name, email, password);
      // Store user info in localStorage
      localStorage.setItem("user", JSON.stringify(data.user));
      window.dispatchEvent(new Event("auth_change"));
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Registration failed. Please try again.");
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
            background: "var(--violet-dim)", border: "1px solid rgba(167,139,250,0.2)",
            display: "flex", alignItems: "center", justifyContent: "center", color: "var(--violet)"
          }}>
            <UserPlus size={28} />
          </div>
        </div>
        <h1>Create an account</h1>
        <p>Join HireSense AI to practice your interviews.</p>

        {error && <p className="chat-error" style={{ textAlign: "center", marginBottom: 16 }}>{error}</p>}

        <form className="auth-form" onSubmit={handleSignup}>
          <div className="input-group">
            <label htmlFor="name">Full Name</label>
            <input 
              id="name" 
              type="text" 
              placeholder="John Doe" 
              value={name}
              onChange={(e) => setName(e.target.value)}
              required 
            />
          </div>
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
          <button type="submit" className="primary-link as-button auth-button" disabled={loading} style={{
            background: "linear-gradient(135deg, var(--violet), var(--cyan))"
          }}>
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <div className="auth-link">
          Already have an account? 
          <Link to="/login">Log in</Link>
        </div>
      </motion.div>
    </main>
  );
}
