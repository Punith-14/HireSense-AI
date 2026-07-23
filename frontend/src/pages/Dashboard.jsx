import { motion } from "framer-motion";
import {
  Legend, Line, LineChart, PolarAngleAxis, PolarGrid, PolarRadiusAxis,
  Radar, RadarChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import FeedbackCard from "../components/FeedbackCard.jsx";
import RecommendationCard from "../components/RecommendationCard.jsx";
import ScoreCard from "../components/ScoreCard.jsx";
import { useInterview } from "../context/InterviewContext.jsx";
import { getInterviewReport, getInterviewHistory } from "../services/interviewApi.js";

const fade = (delay = 0) => ({
  initial:    { opacity: 0, y: 16 },
  animate:    { opacity: 1, y: 0 },
  transition: { duration: 0.4, delay },
});

const RADAR_COLORS = {
  stroke: "#2ff4d8",
  fill:   "#2ff4d8",
};

const TOOLTIP_STYLE = {
  backgroundColor: "#0d1828",
  border: "1px solid rgba(150,200,255,0.15)",
  borderRadius: 10,
  color: "#e0f0ff",
  fontSize: 13,
};

export default function Dashboard() {
  const interview = useInterview();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const sessionId = searchParams.get("session_id");
  const notice = location.state?.notice;

  const [report, setReport] = useState(null);
  const [transcript, setTranscript] = useState([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  /* Load the full session history once, for the cross-session progress view. */
  useEffect(() => {
    getInterviewHistory()
      .then(data => setHistory(data.history || []))
      .catch(err => console.error("Failed to fetch progress history", err));
  }, []);

  useEffect(() => {
    setLoading(true);
    if (sessionId) {
      getInterviewReport(sessionId).then(data => {
        if (data.report) setReport(data.report);
        if (data.transcript) setTranscript(data.transcript);
      }).catch(err => {
        console.error("Failed to fetch report", err);
      }).finally(() => setLoading(false));
    } else {
      getInterviewHistory().then(data => {
        if (data.history && data.history.length > 0) {
          getInterviewReport(data.history[0].session_id).then(rData => {
            if (rData.report) setReport(rData.report);
            if (rData.transcript) setTranscript(rData.transcript);
          }).catch(console.error).finally(() => setLoading(false));
        } else {
          setLoading(false);
        }
      }).catch(err => {
        console.error("Failed to fetch history", err);
        setLoading(false);
      });
    }
  }, [sessionId]);

  /* ── Get User ── */
  const userStr = localStorage.getItem("user");
  const user = userStr ? JSON.parse(userStr) : null;
  const userName = user ? (user.full_name || user.email.split("@")[0]) : "Guest";

  /* ── Cross-session progress (oldest → newest) ── */
  const num = (v) => (typeof v === "number" ? v : 0);
  const sessions = [...history]
    .filter((h) => typeof h.score === "number")
    .reverse(); // history arrives newest-first
  const progressData = sessions.map((h, i) => ({
    label: `Test ${i + 1}`,
    date: h.date ? new Date(h.date).toLocaleDateString() : `Test ${i + 1}`,
    overall: num(h.score),
    technical: num(h.technical_score),
    communication: num(h.communication_score),
    confidence: num(h.confidence_score),
  }));
  const sessionCount = sessions.length;
  const avgScore = sessionCount
    ? Math.round(sessions.reduce((a, h) => a + num(h.score), 0) / sessionCount)
    : 0;
  const bestScore = sessionCount ? Math.max(...sessions.map((h) => num(h.score))) : 0;
  const improvement = sessionCount >= 2
    ? Math.round(num(sessions[sessionCount - 1].score) - num(sessions[sessionCount - 2].score))
    : null;

  /* ── Scores ── */
  const hasHistory = interview.scores && interview.scores.length > 0;
  
  const overallScore = report ? report.final_score : (hasHistory
    ? Math.round(interview.scores.reduce((a, b) => a + b, 0) / interview.scores.length)
    : 0);

  /* Fallback used before a report exists: the live overall average, or 0 if
     there is no data yet. No hardcoded per-metric numbers are shown. */
  const metricFallback = hasHistory ? overallScore : 0;

  /* ── Radar data ── */
  const skillData = [
    { metric: "Technical",       value: report ? report.technical_score : metricFallback },
    { metric: "Communication",   value: report ? report.communication_score : metricFallback },
    { metric: "Confidence",      value: report ? report.confidence_score : metricFallback },
    { metric: "Behavioral",      value: report ? report.behavior_score : metricFallback },
    { metric: "Problem Solving", value: report ? report.technical_score : metricFallback },
    { metric: "Teamwork",        value: report ? report.behavior_score : metricFallback },
  ];

  /* Pull the real score for a single answered question out of its evaluation. */
  const questionScore = (t) => {
    const e = (t && t.evaluation) || {};
    const v = e.technical_score ?? e.teamwork_score ?? e.communication_score
            ?? e.confidence_score ?? e.leadership_score;
    if (typeof v === "number") return v;
    return typeof t.score === "number" ? t.score : 0;
  };

  /* ── Timeline ── */
  const timeline = transcript && transcript.length > 0
    ? transcript.map((t, i) => ({ question: `Q${i + 1}`, score: questionScore(t) }))
    : hasHistory
      ? interview.scores.map((score, i) => ({ question: `Q${i + 1}`, score }))
      : [];

  /* ── Composure / Emotion Timeline ──
     Plots a 0-100 composure score (higher = calmer/more positive), with the
     detected mood for the tooltip. Falls back to older emotion_score data. */
  const emotionTimeline = transcript && transcript.length > 0
    ? transcript.map((t, i) => {
        const vm = t.vision_metrics || {};
        const composure = vm.composure_score ?? Math.round((vm.emotion_score || 0) * 100);
        return { question: `Q${i + 1}`, composure, mood: vm.dominant_emotion || "—" };
      })
    : interview.questionHistory && interview.questionHistory.length
      ? interview.questionHistory.map((q, i) => ({
          question: `Q${i + 1}`,
          composure: q.composure ?? Math.round((q.emotion_score || 0) * 100),
          mood: q.emotion || "—"
        }))
      : [];

  /* ── Feedback: only ever from the real report; no fabricated sample text ── */
  const strengths     = report ? (report.final_analysis?.strengths || []) : ["Complete an interview to see your strengths."];
  const weaknesses    = report ? (report.final_analysis?.weaknesses || []) : ["Complete an interview to see areas for improvement."];
  const recommendations = report ? (report.recommendations || []) : ["Start your first interview session."];

  return (
    <main className="page">
      {notice && (
        <div style={{
          margin: "0 0 16px", padding: "12px 16px", borderRadius: 10,
          background: "rgba(245,158,11,0.14)", border: "1px solid rgba(245,158,11,0.35)",
          color: "#fbbf24", fontSize: 14,
        }}>
          {notice}
        </div>
      )}
      <motion.section className="section compact" {...fade(0)}>
        <div className="eyebrow">Welcome, {userName}</div>
        <h1>Interview Performance Summary</h1>
        {report || hasHistory ? (
          <p>Your session results, skills radar, and AI-generated feedback.</p>
        ) : (
          <p>You haven't completed any interviews yet. Head to the Interview page to get started!</p>
        )}
      </motion.section>

      {/* ── SCORE CARDS ── */}
      <motion.div className="score-row" {...fade(0.05)}>
        <ScoreCard label="Overall Score"       value={overallScore} tone="cyan"   />
        <ScoreCard label="Technical Score"     value={report ? report.technical_score : metricFallback}     tone="violet" />
        <ScoreCard label="Communication Score" value={report ? report.communication_score : metricFallback} tone="blue"   />
        <ScoreCard label="Confidence Score"    value={report ? report.confidence_score : metricFallback}    tone="green"  />
      </motion.div>

      {/* ── PROGRESS ACROSS SESSIONS ── */}
      {sessionCount >= 1 && (
        <motion.section className="section compact" {...fade(0.07)}>
          <div className="section-heading">
            <h2>Your Progress</h2>
            <p>How your performance is trending across all {sessionCount} of your interviews.</p>
          </div>

          <div className="score-row">
            <div className="metric-tile">
              <div className="m-label">Interviews Taken</div>
              <div className="m-value">{sessionCount}</div>
            </div>
            <div className="metric-tile">
              <div className="m-label">Average Score</div>
              <div className="m-value">{avgScore}</div>
            </div>
            <div className="metric-tile">
              <div className="m-label">Best Score</div>
              <div className="m-value">{bestScore}</div>
            </div>
            <div className="metric-tile">
              <div className="m-label">vs Previous Test</div>
              <div
                className="m-value"
                style={{ color: improvement === null ? "#93b8d4" : improvement >= 0 ? "#2ff4d8" : "#f87171" }}
              >
                {improvement === null ? "—" : `${improvement >= 0 ? "+" : ""}${improvement}`}
              </div>
            </div>
          </div>

          <article className="glass-card chart-card" style={{ marginTop: 16 }}>
            <h2>Performance Trend</h2>
            {sessionCount >= 2 ? (
              <ResponsiveContainer height={320} width="100%">
                <LineChart data={progressData}>
                  <XAxis dataKey="label" stroke="#5a7a94" tick={{ fill: "#93b8d4", fontSize: 12 }} />
                  <YAxis domain={[0, 100]} stroke="#5a7a94" tick={{ fill: "#93b8d4", fontSize: 12 }} />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Legend wrapperStyle={{ fontSize: 12 }} />
                  <Line dataKey="overall"       name="Overall"       stroke="#2ff4d8" strokeWidth={2.5} type="monotone" dot={{ r: 4 }} />
                  <Line dataKey="technical"     name="Technical"     stroke="#a78bfa" strokeWidth={2}   type="monotone" dot={{ r: 3 }} />
                  <Line dataKey="communication" name="Communication" stroke="#60a5fa" strokeWidth={2}   type="monotone" dot={{ r: 3 }} />
                  <Line dataKey="confidence"    name="Confidence"    stroke="#34d399" strokeWidth={2}   type="monotone" dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p style={{ color: "#93b8d4", padding: "24px 4px" }}>
                Complete at least two interviews to see your improvement trend.
              </p>
            )}
          </article>
        </motion.section>
      )}

      {/* ── CHARTS ── */}
      <motion.div className="analytics-grid" {...fade(0.1)}>
        <article className="glass-card chart-card">
          <h2>Radar Skill Chart</h2>
          <ResponsiveContainer height={300} width="100%">
            <RadarChart data={skillData}>
              <PolarGrid stroke="rgba(150,200,255,0.12)" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: "#93b8d4", fontSize: 12 }} />
              <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fill: "#5a7a94", fontSize: 10 }} />
              <Radar
                dataKey="value"
                fill={RADAR_COLORS.fill}
                fillOpacity={0.22}
                stroke={RADAR_COLORS.stroke}
                strokeWidth={2}
              />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
            </RadarChart>
          </ResponsiveContainer>
        </article>

        <article className="glass-card chart-card">
          <h2>Performance Timeline</h2>
          <ResponsiveContainer height={300} width="100%">
            <LineChart data={timeline}>
              <XAxis dataKey="question" stroke="#5a7a94" tick={{ fill: "#93b8d4", fontSize: 12 }} />
              <YAxis domain={[0, 100]} stroke="#5a7a94" tick={{ fill: "#93b8d4", fontSize: 12 }} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Line
                dataKey="score"
                dot={{ fill: "#2ff4d8", r: 4, strokeWidth: 0 }}
                stroke="#2ff4d8"
                strokeWidth={2.5}
                type="monotone"
                activeDot={{ r: 6, fill: "#a78bfa" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </article>
      </motion.div>

      {/* ── EMOTION + RECOMMENDATION ── */}
      <motion.div className="analytics-grid" {...fade(0.15)}>
        <article className="glass-card chart-card">
          <h2>Composure Timeline</h2>
          <p style={{ margin: "0 0 8px", fontSize: 12, color: "#93b8d4" }}>
            Higher = calmer &amp; more positive. Hover to see the detected mood.
          </p>
          <ResponsiveContainer height={280} width="100%">
            <LineChart data={emotionTimeline}>
              <XAxis dataKey="question" stroke="#5a7a94" tick={{ fill: "#93b8d4", fontSize: 12 }} />
              <YAxis domain={[0, 100]} stroke="#5a7a94" tick={{ fill: "#93b8d4", fontSize: 12 }} />
              <Tooltip content={<ComposureTooltip />} />
              <Line
                dataKey="composure"
                name="Composure"
                dot={{ fill: "#f472b6", r: 4, strokeWidth: 0 }}
                stroke="#f472b6"
                strokeWidth={2.5}
                type="monotone"
                activeDot={{ r: 6, fill: "#fda4af" }}
              />
            </LineChart>
          </ResponsiveContainer>
        </article>

        <RecommendationCard />
      </motion.div>

      {/* ── FEEDBACK ── */}
      <motion.div className="card-grid three" {...fade(0.2)}>
        <FeedbackCard title="Strengths"       items={strengths} />
        <FeedbackCard title="Weaknesses"      items={weaknesses} />
        <FeedbackCard title="Recommendations" items={recommendations} />
      </motion.div>
    </main>
  );
}

/* Tooltip for the composure timeline: shows the score and the detected mood. */
function ComposureTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  const point = payload[0].payload;
  return (
    <div style={{ ...TOOLTIP_STYLE, padding: "8px 12px" }}>
      <div style={{ fontWeight: 600 }}>{label}</div>
      <div>Composure: {point.composure}</div>
      <div style={{ textTransform: "capitalize", color: "#93b8d4" }}>Mood: {point.mood || "—"}</div>
    </div>
  );
}
