import { BadgeCheck } from "lucide-react";

export default function RecommendationCard({ role = "Junior Backend Developer", note }) {
  return (
    <article className="recommendation-card">
      <BadgeCheck size={28} />
      <div>
        <div className="rec-label">Recommended Role</div>
        <div className="rec-role">{role}</div>
        <p className="rec-note">
          {note || "Strong foundation with room to improve system depth and examples."}
        </p>
      </div>
    </article>
  );
}
