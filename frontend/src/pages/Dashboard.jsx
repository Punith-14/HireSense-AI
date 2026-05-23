import { motion } from "framer-motion";
import {
  Line, LineChart, PolarAngleAxis, PolarGrid, PolarRadiusAxis,
  Radar, RadarChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import FeedbackCard from "../components/FeedbackCard.jsx";
import RecommendationCard from "../components/RecommendationCard.jsx";
import ScoreCard from "../components/ScoreCard.jsx";
import { useInterview } from "../context/InterviewContext.jsx";
import { getInterviewReport } from "../services/interviewApi.js";

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

  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (sessionId) {
      setLoading(true);
      getInterviewReport(sessionId).then(data => {
        if (data.report) setReport(data.report);
      }).catch(err => {
        console.error("Failed to fetch report", err);
      }).finally(() => setLoading(false));
    }
  }, [sessionId]);

  /* ── Get User ── */
  const userStr = localStorage.getItem("user");
  const user = userStr ? JSON.parse(userStr) : null;
  const userName = user ? (user.full_name || user.email.split("@")[0]) : "Guest";

  /* ── Scores ── */
  const hasHistory = interview.scores && interview.scores.length > 0;
  
  const overallScore = report ? report.final_score : (hasHistory
    ? Math.round(interview.scores.reduce((a, b) => a + b, 0) / interview.scores.length)
    : 0);

  /* ── Radar data ── */
  const skillData = [
    { metric: "Technical",    value: report ? report.technical_score : overallScore },
    { metric: "Communication",value: report ? report.communication_score : (hasHistory ? 74 : 0) },
    { metric: "Confidence",   value: report ? report.confidence_score : (hasHistory ? 78 : 0) },
    { metric: "Behavioral",   value: report ? report.behavior_score : (hasHistory ? 80 : 0) },
    { metric: "Problem Solving", value: hasHistory ? 80 : 0 },
    { metric: "Teamwork",     value: hasHistory ? 76 : 0 },
  ];

  /* ── Timeline ── */
  const timeline = hasHistory
    ? interview.scores.map((score, i) => ({ question: `Q${i + 1}`, score }))
    : [];

  /* ── Emotion Timeline ── */
  const emotionTimeline = interview.questionHistory && interview.questionHistory.length
    ? interview.questionHistory.map((q, i) => ({
        question: `Q${i + 1}`,
        emotion: Math.round((q.emotion_score || 0) * 100)
      }))
    : [];

  /* ── Feedback from real data or demo ── */
  const strengths     = report ? report.final_analysis?.strengths || [] : (hasHistory ? ["Strong OOP understanding", "Clear communication style"] : ["Complete an interview to see strengths."]);
  const weaknesses    = report ? report.final_analysis?.weaknesses || [] : (hasHistory ? ["Needs better optimization explanation", "Add more code examples"] : ["Complete an interview to see areas for improvement."]);
  const recommendations = report ? report.recommendations || [] : (hasHistory ? ["Practice concurrency concepts", "Use STAR format for answers"] : ["Start your first interview session."]);

  return (
    <main className="page">
      <motion.section className="section compact" {...fade(0)}>
        <div className="eyebrow">Welcome, {userName}</div>
        <h1>Interview Performance Summary</h1>
        {hasHistory ? (
          <p>Your session results, skills radar, and AI-generated feedback.</p>
        ) : (
          <p>You haven't completed any interviews yet. Head to the Interview page to get started!</p>
        )}
      </motion.section>

      {/* ── SCORE CARDS ── */}
      <motion.div className="score-row" {...fade(0.05)}>
        <ScoreCard label="Overall Score"       value={overallScore} tone="cyan"   />
        <ScoreCard label="Technical Score"     value={report ? report.technical_score : (hasHistory ? 82 : 0)}           tone="violet" />
        <ScoreCard label="Communication Score" value={report ? report.communication_score : (hasHistory ? 74 : 0)}           tone="blue"   />
        <ScoreCard label="Confidence Score"    value={report ? report.confidence_score : (hasHistory ? 78 : 0)}           tone="green"  />
      </motion.div>

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
          <h2>Emotion Timeline</h2>
          <ResponsiveContainer height={300} width="100%">
            <LineChart data={emotionTimeline}>
              <XAxis dataKey="question" stroke="#5a7a94" tick={{ fill: "#93b8d4", fontSize: 12 }} />
              <YAxis domain={[0, 100]} stroke="#5a7a94" tick={{ fill: "#93b8d4", fontSize: 12 }} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
              <Line
                dataKey="emotion"
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
