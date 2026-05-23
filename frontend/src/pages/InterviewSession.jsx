import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bot, Loader2, Send, SkipForward, Square, TrendingUp, User, Video, Zap, Mic, MicOff } from "lucide-react";
import InterviewProgress from "../components/InterviewProgress.jsx";
import Timer from "../components/Timer.jsx";
import { useInterview } from "../context/InterviewContext.jsx";
import { analyzeVisionFrame, startInterview, submitAnswer } from "../services/interviewApi.js";

export default function InterviewSession() {
  const interview = useInterview();
  const navigate  = useNavigate();
  const [status, setStatus]   = useState("idle");
  const [error,  setError]    = useState("");
  const [draft,  setDraft]    = useState("");
  const [timeLeft, setTimeLeft] = useState(120); // 2 minutes per question
  const [sessionId, setSessionId] = useState("");

  const MAX_QUESTIONS = 5;
  const [messages, setMessages] = useState([
    {
      role: "ai",
      type: "welcome",
      text: `👋 Hello! I'm your ${interview.selectedAgent || "AI"} interviewer. Press **Next Question** to begin your session for the **${interview.selectedRole || "selected role"}** role.`,
    },
  ]);

  const bottomRef  = useRef(null);
  const textareaRef = useRef(null);
  const timerRef    = useRef(null);
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const visionIntervalRef = useRef(null);

  const [isRecording, setIsRecording] = useState(false);
  const [mediaStream, setMediaStream] = useState(null);
  const [visionMetrics, setVisionMetrics] = useState({ attention: "unknown", emotion_score: 0 });

  /* ── Media Devices Initialization ── */
  useEffect(() => {
    let stream = null;
    async function enableMedia() {
      if (interview.webcamAnalysis || interview.voiceInput) {
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: interview.webcamAnalysis,
            audio: interview.voiceInput
          });
          setMediaStream(stream);
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        } catch (err) {
          console.error("Failed to access media devices", err);
          setError("Camera/Microphone access denied or unavailable.");
        }
      }
    }
    enableMedia();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [interview.webcamAnalysis, interview.voiceInput]);

  /* ── Vision Polling ── */
  useEffect(() => {
    if (!interview.webcamAnalysis || !mediaStream || status !== "idle" || !interview.currentQuestion) return;
    
    visionIntervalRef.current = setInterval(async () => {
      if (videoRef.current && videoRef.current.readyState === 4) {
        const canvas = document.createElement("canvas");
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob(async (blob) => {
          if (blob) {
            try {
              const res = await analyzeVisionFrame(blob);
              if (res.status === "ok" && res.vision) {
                setVisionMetrics(prev => ({
                  ...prev,
                  attention: res.vision.attention || prev.attention,
                  emotion_score: res.vision.emotion_score !== undefined ? res.vision.emotion_score : prev.emotion_score
                }));
              }
            } catch (e) {
              console.error("Vision polling error", e);
            }
          }
        }, "image/jpeg", 0.7);
      }
    }, 3000); // 3 seconds
    
    return () => clearInterval(visionIntervalRef.current);
  }, [interview.webcamAnalysis, mediaStream, status, interview.currentQuestion]);

  /* Countdown Timer Effect */
  useEffect(() => {
    if (status !== "idle" || !interview.currentQuestion) return;

    timerRef.current = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timerRef.current);
  }, [status, interview.currentQuestion]);

  /* Auto-submit on timeout */
  useEffect(() => {
    if (timeLeft === 0 && status === "idle" && interview.currentQuestion) {
      handleSubmit("Time is up - no answer provided.");
    }
  }, [timeLeft, status, interview.currentQuestion]);

  /* Auto-scroll to latest message */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, status]);

  /* Auto-resize textarea */
  function handleDraftChange(e) {
    setDraft(e.target.value);
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 180) + "px";
    }
  }

  /* Submit on Enter (Shift+Enter = newline) */
  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  /* ── Generate Question ── */
  async function handleGenerate() {
    setStatus("generating");
    setError("");
    setTimeLeft(120); // reset timer for new question
    setMessages((m) => [...m, { role: "ai", type: "thinking", text: "Starting session…" }]);

    try {
      if (!sessionId) {
        let userEmail = "";
        let fullName = "";
        try {
          const userStr = localStorage.getItem("user");
          if (userStr) {
            const user = JSON.parse(userStr);
            userEmail = user.email;
            fullName = user.full_name;
          }
        } catch (e) {
          console.error("Error reading user from localStorage:", e);
        }

        const data = await startInterview({
          mode: interview.selectedAgent,
          role: interview.selectedRole,
          difficulty: interview.difficulty,
          user_email: userEmail,
          full_name: fullName,
        });
        setSessionId(data.session_id);
        const questionObj = data.question;
        interview.updateInterview({ currentQuestion: questionObj.question, currentAnswer: "" });

        setMessages((m) => [
          ...m.filter((msg) => msg.type !== "thinking"),
          {
            role: "ai",
            type: "question",
            text: questionObj.question,
            meta: { agent: interview.selectedAgent, difficulty: questionObj.difficulty },
          },
        ]);
      }
    } catch (err) {
      setMessages((m) => m.filter((msg) => msg.type !== "thinking"));
      setError(err.response?.data?.error || err.message);
    } finally {
      setStatus("idle");
    }
  }

  /* ── Voice Recording ── */
  function toggleRecording() {
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    } else {
      if (!mediaStream) {
        setError("Microphone is not accessible. Please check permissions.");
        return;
      }
      audioChunksRef.current = [];
      const recorder = new MediaRecorder(mediaStream);
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        handleSubmit(null, audioBlob);
      };
      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
      setDraft("🎙️ Recording your answer... Click stop to submit.");
    }
  }

  /* ── Submit Answer ── */
  async function handleSubmit(forcedAnswer = null, audioBlob = null) {
    const answer = typeof forcedAnswer === "string" ? forcedAnswer : draft.trim();
    if (!interview.currentQuestion) { setError("Generate a question first."); return; }
    if (!answer && !audioBlob) { setError("Please type your answer or record audio before submitting."); return; }

    setError("");
    setDraft("");
    setTimeLeft(120); // freeze/reset timer
    if (textareaRef.current) textareaRef.current.style.height = "auto";

    /* Show user bubble */
    setMessages((m) => [...m, { role: "user", type: "answer", text: audioBlob ? "🎵 (Audio Answer Submitted)" : answer }]);
    setStatus("evaluating");

    /* Show AI thinking */
    setMessages((m) => [...m, { role: "ai", type: "thinking", text: "Evaluating your answer…" }]);

    try {
      const data = await submitAnswer({
        session_id: sessionId,
        mode: interview.selectedAgent,
        answer_text: audioBlob ? "" : answer,
        audioBlob: audioBlob,
        vision_metrics: interview.webcamAnalysis ? visionMetrics : {}
      });

      const { evaluation, next_question, is_complete } = data;
      const score = evaluation?.overall_rating || evaluation?.technical_score || evaluation?.communication_score || evaluation?.teamwork_score || 0;

      interview.addEvaluation({
        agent: interview.selectedAgent,
        question: interview.currentQuestion,
        answer,
        score,
        feedback: evaluation?.feedback || evaluation?.answer_summary || "Evaluation complete.",
        followup: next_question,
        emotion_score: interview.webcamAnalysis ? (visionMetrics.emotion_score || 0) : 0,
      });

      interview.updateInterview({ currentAnswer: answer });

      /* Test Mode: Do not show AI feedback bubble inline */
      setMessages((m) => m.filter((msg) => msg.type !== "thinking"));

      if (is_complete || interview.questionHistory.length + 1 >= MAX_QUESTIONS) {
        navigate(`/dashboard?session_id=${sessionId}`);
      } else {
        if (next_question) {
           interview.updateInterview({ currentQuestion: next_question.question, currentAnswer: "" });
           setMessages((m) => [
             ...m,
             {
               role: "ai",
               type: "question",
               text: next_question.question,
               meta: { agent: interview.selectedAgent, difficulty: next_question.difficulty },
             },
           ]);
        }
      }
    } catch (err) {
      setMessages((m) => m.filter((msg) => msg.type !== "thinking"));
      if (err.response?.status === 422 && err.response?.data?.status === "transcription_unavailable") {
        setError("Offline speech models are unavailable. Please fall back to typing your answer.");
      } else {
        setError(err.response?.data?.error || err.message);
      }
    } finally {
      setStatus("idle");
    }
  }

  return (
    <div className="session-page">

      {/* ── LEFT SIDEBAR ── */}
      <aside className="session-sidebar">
        <div className="webcam-card" style={{ position: "relative", overflow: "hidden" }}>
          {interview.webcamAnalysis ? (
             <>
               <video ref={videoRef} autoPlay muted playsInline style={{ width: "100%", height: "100%", objectFit: "cover", position: "absolute", top: 0, left: 0, zIndex: 0 }} />
               <div style={{ position: "relative", zIndex: 1, textShadow: "0 1px 3px rgba(0,0,0,0.8)", display: "flex", flexDirection: "column", alignItems: "center" }}>
                  <Video size={30} />
                  <span>Live Feed</span>
               </div>
             </>
          ) : (
             <>
               <Video size={30} />
               <span>Webcam Off</span>
               <small>Enable in setup</small>
             </>
          )}
        </div>
        <div className="candidate-card">
          <div className="label">Role</div>
          <div className="value">{interview.selectedRole || "—"}</div>
          <div className="divider" />
          <div className="label">Agent</div>
          <div className="value">{interview.selectedAgent || "—"}</div>
        </div>
        <Timer timeLeft={timeLeft} />
        <InterviewProgress completed={interview.questionHistory.length} />
      </aside>

      {/* ── CHAT CENTER ── */}
      <section className="chat-section">

        {/* Chat header */}
        <div className="chat-header">
          <div className="chat-header-left">
            <div className="ai-avatar-sm">
              <Bot size={16} />
            </div>
            <div>
              <div className="chat-header-title">HireSense AI Interviewer</div>
              <div className="chat-header-sub">
                {status === "generating"  && "Generating question…"}
                {status === "evaluating"  && "Evaluating your answer…"}
                {status === "idle"        && "Online · Ready"}
              </div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button
              className="primary-link as-button"
              disabled={status !== "idle" || interview.currentQuestion}
              onClick={handleGenerate}
              style={{ fontSize: 13, padding: "8px 16px", display: interview.currentQuestion ? "none" : "flex" }}
              type="button"
            >
              {status === "generating"
                ? <><Loader2 className="spin" size={14} /> Generating…</>
                : <><SkipForward size={14} /> Next Question</>}
            </button>
            <button
              className="ghost-button"
              onClick={() => navigate(`/dashboard?session_id=${sessionId}`)}
              style={{ fontSize: 13, padding: "8px 14px" }}
              type="button"
            >
              <Square size={13} /> End
            </button>
          </div>
        </div>

        {/* Message list */}
        <div className="chat-messages">
          {messages.map((msg, i) => (
            <ChatMessage key={i} msg={msg} />
          ))}

          {/* Loading bubble */}
          {status !== "idle" && messages.at(-1)?.type === "thinking" && (
            <div className="chat-bubble ai">
              <div className="ai-avatar-sm"><Bot size={14} /></div>
              <div className="bubble bubble-ai thinking-bubble">
                <span /><span /><span />
              </div>
            </div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Error */}
        {error && <p className="chat-error">{error}</p>}

        {/* Input bar */}
        <div className="chat-input-bar">
          {interview.voiceInput && (
             <button 
               type="button"
               disabled={status !== "idle"}
               onClick={toggleRecording}
               style={{ background: "transparent", border: "none", color: isRecording ? "#f87171" : "#93b8d4", cursor: "pointer", padding: "8px", display: "flex", alignItems: "center" }}
               title={isRecording ? "Stop Recording & Submit" : "Start Voice Recording"}
             >
                {isRecording ? <MicOff size={22} className="pulse-anim" /> : <Mic size={22} />}
             </button>
          )}
          <textarea
            className="chat-input"
            disabled={status !== "idle"}
            maxLength={2000}
            onChange={handleDraftChange}
            onKeyDown={handleKeyDown}
            placeholder={
              status !== "idle"
                ? "Please wait…"
                : interview.currentQuestion
                  ? "Type your answer… (Enter to send, Shift+Enter for new line)"
                  : "Press Next Question to get your first question…"
            }
            ref={textareaRef}
            rows={1}
            value={draft}
          />
          <button
            className="chat-send-btn"
            disabled={status !== "idle" || !draft.trim()}
            onClick={handleSubmit}
            type="button"
          >
            {status === "evaluating"
              ? <Loader2 className="spin" size={18} />
              : <Send size={18} />}
          </button>
        </div>
        <div className="chat-hint">
          HireSense AI · Answers are evaluated by Gemini
        </div>
      </section>

      {/* ── RIGHT SIDEBAR ── */}
      <aside className="session-sidebar right">
        <div className="metric-tile">
          <div className="m-label">Difficulty</div>
          <div className="m-value">{interview.difficulty}</div>
        </div>
        <div className="metric-tile">
          <div className="m-label">Questions Done</div>
          <div className="m-value">{interview.questionHistory.length}</div>
        </div>
        <div className="adaptive-card">
          {interview.adaptiveMode
            ? <><Zap size={14} /> Adaptive mode on</>
            : <><TrendingUp size={14} /> Fixed difficulty</>}
        </div>
      </aside>
    </div>
  );
}

/* ── Individual Chat Message ── */
function ChatMessage({ msg }) {
  if (msg.type === "thinking") return null; // rendered separately

  if (msg.role === "user") {
    return (
      <div className="chat-bubble user">
        <div className="bubble bubble-user">{msg.text}</div>
        <div className="user-avatar"><User size={14} /></div>
      </div>
    );
  }

  if (msg.type === "welcome") {
    return (
      <div className="chat-bubble ai">
        <div className="ai-avatar-sm"><Bot size={14} /></div>
        <div className="bubble bubble-ai">
          <p style={{ margin: 0 }}>{msg.text}</p>
        </div>
      </div>
    );
  }

  if (msg.type === "question") {
    const diff = msg.meta?.difficulty;
    return (
      <div className="chat-bubble ai">
        <div className="ai-avatar-sm"><Bot size={14} /></div>
        <div className="bubble bubble-ai bubble-question">
          <div className="bubble-label">Interview Question</div>
          <p className="bubble-q-text">{msg.text}</p>
          {diff && (
            <span className={`meta-badge difficulty-${diff}`} style={{ marginTop: 8, display: "inline-flex" }}>
              {diff}
            </span>
          )}
        </div>
      </div>
    );
  }

  if (msg.type === "feedback") {
    return (
      <div className="chat-bubble ai">
        <div className="ai-avatar-sm"><Bot size={14} /></div>
        <div className="bubble bubble-ai bubble-feedback">
          <div className="bubble-label">AI Evaluation</div>
          <div className="fb-score-row">
            <span className="fb-score-num">{msg.score}</span>
            <span className="fb-score-label">/ 100</span>
            <div className="fb-score-bar">
              <div className="fb-score-fill" style={{ width: `${msg.score}%` }} />
            </div>
          </div>
          <p className="fb-feedback">{msg.feedback}</p>
          {msg.followup && (
            <div className="fb-followup">
              <span className="fb-followup-label">💡 Follow-up</span>
              <p>{msg.followup}</p>
            </div>
          )}
          {msg.nextDifficulty && (
            <div className="fb-difficulty-tag">
              Next difficulty → <strong>{msg.nextDifficulty}</strong>
            </div>
          )}
        </div>
      </div>
    );
  }

  return null;
}

function getPrimaryScore(result) {
  if (typeof result?.technical_score  === "number") return result.technical_score;
  if (typeof result?.confidence_score === "number") return result.confidence_score;
  if (typeof result?.leadership_score === "number") return result.leadership_score;
  if (typeof result?.teamwork_score   === "number") return result.teamwork_score;
  return 0;
}
