export default function ScoreCard({ label, value, tone = "cyan" }) {
  const numVal = Number(value) || 0;

  return (
    <article className={`score-card ${tone}`}>
      <div className="sc-label">{label}</div>
      <div className="sc-value">{value}</div>
      <div className="sc-bar">
        <div className="sc-bar-fill" style={{ width: `${numVal}%` }} />
      </div>
    </article>
  );
}
