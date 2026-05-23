import { motion } from "framer-motion";
import {
  BarChart3,
  BrainCircuit,
  ChevronRight,
  Gauge,
  HeartPulse,
  MessageCircle,
  ShieldCheck,
  Sparkles,
  Target,
  Zap,
} from "lucide-react";
import { Link } from "react-router-dom";

const fade = (delay = 0) => ({
  initial:    { opacity: 0, y: 18 },
  animate:    { opacity: 1, y: 0 },
  transition: { duration: 0.45, delay, ease: [0.4, 0, 0.2, 1] },
});

const benefits = [
  {
    icon: BrainCircuit,
    title: "Practice Real Interview Questions",
    desc: "Get AI-generated questions tailored to your role — Java, Python, Frontend, Backend, AI/ML, and more.",
  },
  {
    icon: Gauge,
    title: "Adaptive Difficulty",
    desc: "The more you answer, the smarter it gets. Questions adjust based on your performance automatically.",
  },
  {
    icon: Sparkles,
    title: "Instant AI Feedback",
    desc: "Every answer is evaluated immediately with scores, feedback, and a follow-up question to deepen your thinking.",
  },
  {
    icon: MessageCircle,
    title: "HR & Behavioral Prep",
    desc: "Go beyond technical — practice communication, confidence, leadership and teamwork questions.",
  },
  {
    icon: BarChart3,
    title: "Detailed Performance Dashboard",
    desc: "See your radar skill chart, score timeline, strengths, weaknesses, and role recommendation — all in one place.",
  },
  {
    icon: HeartPulse,
    title: "Emotion & Confidence Tracking",
    desc: "Coming soon — webcam-based analysis of your stress level, eye contact, and confidence during answers.",
  },
];

const steps = [
  { icon: Target,      title: "Pick Your Role",     desc: "Choose the job role you are preparing for." },
  { icon: ShieldCheck, title: "Choose an Agent",     desc: "Select Technical, HR, or Behavioral interview mode." },
  { icon: Zap,         title: "Answer Questions",    desc: "AI generates a question. You answer it in your own words." },
  { icon: Sparkles,    title: "Get Evaluated",       desc: "Your answer is scored instantly with detailed feedback." },
  { icon: BarChart3,   title: "Review Your Results", desc: "See your full performance report on the dashboard." },
];

export default function About() {
  return (
    <main className="page">

      {/* ── INTRO ── */}
      <motion.section className="section compact" {...fade(0)}>
        <div className="eyebrow">About HireSense AI</div>
        <h1>Your Personal AI Interview Coach</h1>
        <p style={{ maxWidth: 620, fontSize: 18, lineHeight: 1.75 }}>
          HireSense AI helps you prepare for job interviews by simulating real interview
          scenarios — asking smart questions, evaluating your answers, and giving you
          actionable feedback so you walk into your next interview with confidence.
        </p>
        <div className="hero-actions" style={{ marginTop: 24 }}>
          <Link className="primary-link" to="/interview">
            Start Practicing <ChevronRight size={16} />
          </Link>
          <Link className="ghost-link" to="/dashboard">
            View Dashboard
          </Link>
        </div>
      </motion.section>

      {/* ── HOW IT WORKS ── */}
      <motion.section className="section" {...fade(0.06)}>
        <div className="section-heading">
          <div className="eyebrow">How It Works</div>
          <h2>5 steps to interview-ready</h2>
          <p>From setup to results in under 10 minutes.</p>
        </div>
        <div className="workflow">
          {steps.map(({ icon: Icon, title, desc }, i) => (
            <motion.div className="workflow-step" key={title} {...fade(i * 0.06)}>
              <span className="step-num">{i + 1}</span>
              <div>
                <strong style={{ display: "block", marginBottom: 2, color: "var(--text-1)" }}>
                  {title}
                </strong>
                <span style={{ fontSize: 13, color: "var(--text-2)" }}>{desc}</span>
              </div>
              <ChevronRight className="step-arrow" size={16} />
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* ── BENEFITS ── */}
      <motion.section className="section" {...fade(0.1)}>
        <div className="section-heading">
          <div className="eyebrow">What You Get</div>
          <h2>Everything you need to ace your interview</h2>
        </div>
        <div className="card-grid three">
          {benefits.map(({ icon: Icon, title, desc }, i) => (
            <motion.article
              className="glass-card feature-card"
              key={title}
              {...fade(i * 0.06)}
            >
              <div className="icon-wrap">
                <Icon size={22} />
              </div>
              <strong>{title}</strong>
              <p>{desc}</p>
            </motion.article>
          ))}
        </div>
      </motion.section>

    </main>
  );
}
