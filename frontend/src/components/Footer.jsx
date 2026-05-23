import { Bot } from "lucide-react";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-brand" style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <Bot size={16} />
        HireSense AI
      </div>
      <span className="footer-copy">Django · Gemini · LangChain · React</span>
      <span className="footer-copy">
        <Link to="/about" style={{ color: "inherit" }}>Architecture</Link>
      </span>
    </footer>
  );
}
