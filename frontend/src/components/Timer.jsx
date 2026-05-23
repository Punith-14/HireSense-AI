import React from "react";
import { Clock3 } from "lucide-react";

export default function Timer({ timeLeft }) {
  const mm = String(Math.floor(timeLeft / 60)).padStart(2, "0");
  const ss = String(timeLeft % 60).padStart(2, "0");
  const isUrgent = timeLeft <= 30; // warn after 30 seconds left

  return (
    <div className="timer-card">
      <Clock3 size={18} />
      <div>
        <div className="timer-label">Time Remaining</div>
        <div className={`timer-value ${isUrgent ? "timer-warning" : ""}`}>
          {mm}:{ss}
        </div>
      </div>
    </div>
  );
}
