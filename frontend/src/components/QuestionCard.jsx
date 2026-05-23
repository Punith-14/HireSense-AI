import { MessageSquareText } from "lucide-react";

export default function QuestionCard({ agent, difficulty, question, questionNumber }) {
  const diffClass = difficulty ? `difficulty-${difficulty.toLowerCase()}` : "";

  return (
    <section className="question-card fade-in">
      <div className="question-kicker">
        <MessageSquareText size={15} />
        Question {questionNumber}
      </div>
      <p className={`question-text ${!question ? "question-empty" : ""}`}>
        {question || "Press \"Next Question\" to generate your first AI interview question."}
      </p>
      <div className="question-meta">
        {agent && <span className="meta-badge">{agent}</span>}
        {difficulty && <span className={`meta-badge ${diffClass}`}>{difficulty}</span>}
      </div>
    </section>
  );
}
