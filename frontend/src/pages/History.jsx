import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useInterview } from "../context/InterviewContext.jsx";
import { getInterviewHistory } from "../services/interviewApi.js";

const DEMO_ROWS = [
  { date: "May 21, 2026", agent: "Technical",  score: 82, rec: "Junior Backend Developer" },
  { date: "May 20, 2026", agent: "HR",          score: 78, rec: "Improve confidence examples" },
  { date: "May 19, 2026", agent: "Behavioral",  score: 80, rec: "Strong leadership fit" },
];

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const data = await getInterviewHistory();
        if (data.history && data.history.length > 0) {
          setHistory(data.history.map(row => ({
            date: new Date(row.date).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }),
            agent: row.agent_type,
            score: row.score,
            rec: row.recommendation || "—"
          })));
        } else {
          setHistory(DEMO_ROWS);
        }
      } catch (err) {
        console.error("Failed to fetch history:", err);
        setHistory(DEMO_ROWS);
      } finally {
        setLoading(false);
      }
    }
    fetchHistory();
  }, []);

  return (
    <main className="page">
      <motion.section
        className="section compact"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <div className="eyebrow">History</div>
        <h1>Previous Interview Attempts</h1>
        <p>A log of all your past sessions with scores and recommendations.</p>
      </motion.section>

      <motion.section
        className="glass-card table-card"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.08 }}
      >
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Agent Type</th>
              <th>Score</th>
              <th>Recommendation / Feedback</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="4" style={{textAlign:"center"}}>Loading history...</td></tr>
            ) : history.map((row, i) => (
              <tr key={i}>
                <td>{row.date}</td>
                <td>
                  <span className="td-badge">{row.agent}</span>
                </td>
                <td className="td-score">{row.score}</td>
                <td style={{ maxWidth: 320 }}>{row.rec}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.section>
    </main>
  );
}
