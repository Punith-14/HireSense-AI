import { Sparkles } from "lucide-react";

export default function FeedbackCard({ title, items = [] }) {
  return (
    <article className="glass-card feedback-card">
      <div className="feedback-kicker">
        <Sparkles size={14} />
        {title}
      </div>
      <ul>
        {items.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>
    </article>
  );
}
