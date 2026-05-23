export default function InterviewProgress({ completed, total = 10 }) {
  const pct = Math.min(100, Math.round((completed / total) * 100));

  return (
    <div className="progress-card">
      <div className="progress-header">
        <span>Interview Progress</span>
        <strong>{completed} / {total}</strong>
      </div>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
