import { motion } from "framer-motion";
import {
  BarChart3, BrainCircuit, ChevronRight,
  Gauge, HeartPulse, MessageCircle, ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";

const features = [
  { title: "Technical AI Interviews",   icon: BrainCircuit,  desc: "Java, DSA, system design, and OOP questions powered by AI." },
  { title: "HR Interview Simulation",   icon: MessageCircle, desc: "Personality, motivation, and communication skill evaluation." },
  { title: "Behavioral Analysis",       icon: ShieldCheck,   desc: "STAR-based teamwork and leadership question generation." },
  { title: "Adaptive Difficulty",       icon: Gauge,         desc: "Questions get harder or easier based on your performance." },
  { title: "Emotion Analysis",          icon: HeartPulse,    desc: "Webcam-based stress, confidence, and eye contact tracking." },
  { title: "Smart Dashboard",           icon: BarChart3,     desc: "Radar charts, score cards, and actionable AI feedback." },
];


const workflow = [
  "Select Role",
  "Choose Agent",
  "Start Interview",
  "AI Evaluation",
  "Dashboard",
];

const fade = (delay = 0) => ({
  initial:    { opacity: 0, y: 22 },
  animate:    { opacity: 1, y: 0 },
  transition: { duration: 0.5, delay, ease: [0.4, 0, 0.2, 1] },
});

export default function Home() {
  return (
    <main className="page">
      {/* ── HERO ── */}
      <section className="hero">
        <motion.div className="hero-text" {...fade(0)}>
          <div className="eyebrow">✦ AI-Powered Interview Platform</div>
          <h1>AI-Powered Adaptive Mock Interview Platform</h1>
          <p className="hero-copy">
            Practice technical, HR, and behavioral interviews with AI-generated
            questions, real-time evaluation, adaptive difficulty, and rich analytics.
          </p>
          <div className="hero-actions">
            <Link className="primary-link" to="/interview">
              Start Interview <ChevronRight size={16} />
            </Link>
            <Link className="ghost-link" to="/about">
              View Architecture
            </Link>
          </div>
        </motion.div>

        <motion.div className="hero-visual" {...fade(0.15)}>
          <div className="ai-core">AI</div>
          <span>Role</span>
          <span>Agent</span>
          <span>Score</span>
          <span>Feedback</span>
        </motion.div>
      </section>

      {/* ── FEATURES ── */}
      <section className="section">
        <motion.div className="section-heading" {...fade(0)}>
          <div className="eyebrow">Features</div>
          <h2>Built for a complete interview flow</h2>
          <p>Every stage of the interview experience — powered by AI.</p>
        </motion.div>
        <div className="card-grid three">
          {features.map(({ title, icon: Icon, desc }, i) => (
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
      </section>

      {/* ── WORKFLOW ── */}
      <section className="section split">
        <motion.div {...fade(0)}>
          <div className="eyebrow">Workflow</div>
          <h2>From setup to insights in minutes</h2>
          <p style={{ marginTop: 12 }}>
            A seamless end-to-end interview experience — select your role, pick
            an agent, answer AI questions, and get detailed performance analytics.
          </p>
        </motion.div>
        <motion.div className="workflow" {...fade(0.1)}>
          {workflow.map((step, i) => (
            <div className="workflow-step" key={step}>
              <span className="step-num">{i + 1}</span>
              {step}
              <ChevronRight className="step-arrow" size={16} />
            </div>
          ))}
        </motion.div>
      </section>


    </main>
  );
}
