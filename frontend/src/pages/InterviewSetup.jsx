import React, { useEffect } from "react";
import { motion } from "framer-motion";
import { ChevronRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import AgentSelector from "../components/AgentSelector.jsx";
import RoleSelector from "../components/RoleSelector.jsx";
import { useInterview } from "../context/InterviewContext.jsx";

const difficulties = ["easy", "medium", "hard", "adaptive"];

const fade = (delay = 0) => ({
  initial:    { opacity: 0, y: 18 },
  animate:    { opacity: 1, y: 0 },
  transition: { duration: 0.4, delay, ease: [0.4, 0, 0.2, 1] },
});

export default function InterviewSetup() {
  const navigate = useNavigate();
  const interview = useInterview();

  useEffect(() => {
    // Clear any leftover progress from a previous session, but keep role/agent preferences
    interview.clearProgress();
  }, []);

  const canStart = interview.selectedRole && interview.selectedAgent;

  return (
    <main className="page">
      <motion.section className="section compact" {...fade(0)}>
        <div className="eyebrow">Interview Setup</div>
        <h1>Choose your role, agent &amp; preferences</h1>
        <p style={{ maxWidth: 560 }}>
          Configure your mock interview session. Select a role and an AI agent to
          begin a personalized interview experience.
        </p>
      </motion.section>


      {/* Agent */}
      <motion.section className="section" {...fade(0.1)}>
        <div className="section-heading">
          <h2>Interviewer Selection</h2>
          <p>Pick the interviewer style — Technical, HR, or Behavioral.</p>
        </div>
        <AgentSelector
          selectedAgent={interview.selectedAgent}
          onSelect={(selectedAgent) => interview.updateInterview({ selectedAgent })}
        />
      </motion.section>

      {/* Role */}
      <motion.section className="section" {...fade(0.05)}>
        <div className="section-heading">
          <h2>Role Selection</h2>
          <p>Select the target job role for this interview session.</p>
        </div>
        <RoleSelector
          selectedRole={interview.selectedRole}
          onSelect={(selectedRole) => interview.updateInterview({ selectedRole })}
        />
      </motion.section>

      {/* Difficulty + Preferences */}
      <motion.div className="setup-grid" {...fade(0.15)}>
        {/* Difficulty */}
        <div className="glass-card">
          <h3 style={{ marginBottom: 16 }}>Difficulty</h3>
          <div className="segmented">
            {difficulties.map((d) => (
              <button
                className={interview.difficulty === d ? "selected" : ""}
                key={d}
                onClick={() => interview.updateInterview({ difficulty: d })}
                type="button"
                style={{ textTransform: "capitalize" }}
              >
                {d}
              </button>
            ))}
          </div>
          {interview.difficulty === "adaptive" && (
            <p style={{ marginTop: 12, fontSize: 13, color: "var(--cyan)" }}>
              ✦ Difficulty auto-adjusts based on your answers.
            </p>
          )}
        </div>

        {/* Preferences */}
        <div className="glass-card">
          <h3 style={{ marginBottom: 4 }}>Interview Preferences</h3>
          <Toggle
            checked={interview.voiceInput}
            label="Enable voice input"
            onChange={(v) => interview.updateInterview({ voiceInput: v })}
          />
          <Toggle
            checked={interview.webcamAnalysis}
            label="Enable webcam analysis"
            onChange={(v) => interview.updateInterview({ webcamAnalysis: v })}
          />
          <Toggle
            checked={interview.adaptiveMode}
            label="Enable adaptive questioning"
            onChange={(v) => interview.updateInterview({ adaptiveMode: v })}
          />
          <Toggle
            checked={interview.followUps}
            label="Enable follow-up questions"
            onChange={(v) => interview.updateInterview({ followUps: v })}
          />
        </div>
      </motion.div>

      {/* Start Button */}
      <motion.div className="page-actions" {...fade(0.2)}>
        <button className="ghost-button" onClick={() => navigate("/")} type="button">
          Back
        </button>
        <button
          className="primary-link as-button"
          disabled={!canStart}
          onClick={() => navigate("/session")}
          type="button"
          style={{ opacity: canStart ? 1 : 0.5, cursor: canStart ? "pointer" : "not-allowed" }}
        >
          Start Interview <ChevronRight size={17} />
        </button>
      </motion.div>
    </main>
  );
}

function Toggle({ checked, label, onChange }) {
  return (
    <label className="toggle-row" style={{ cursor: "pointer" }}>
      <span className="tl">{label}</span>
      <span className="toggle-switch">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <span className="toggle-slider" />
      </span>
    </label>
  );
}
