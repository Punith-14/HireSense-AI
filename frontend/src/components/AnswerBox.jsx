export default function AnswerBox({ answer, onChange }) {
  const max = 2000;
  const warn = answer.length > max * 0.8;

  return (
    <div className="answer-panel">
      <span className="answer-label">Your Answer</span>
      <textarea
        value={answer}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Type your answer here..."
        maxLength={max}
        rows={7}
      />
      <span className={`char-count ${warn ? "warn" : ""}`}>
        {answer.length} / {max} characters
      </span>
    </div>
  );
}
