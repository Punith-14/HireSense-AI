import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle, Bot, ChevronRight, Loader2, Mic, MicOff, RotateCcw, Send, Square, Video, Volume2, VolumeX } from "lucide-react";
import Timer from "../components/Timer.jsx";
import { useInterview } from "../context/InterviewContext.jsx";
import { analyzeVisionFrame, startInterview, submitAnswer } from "../services/interviewApi.js";

const MAX_QUESTIONS = 5;

export default function InterviewSession() {
  const interview = useInterview();
  const navigate = useNavigate();

  const [status, setStatus] = useState("idle"); // idle | generating | evaluating
  const [error, setError] = useState("");
  const [draft, setDraft] = useState("");
  const [timeLeft, setTimeLeft] = useState(120);
  const [sessionId, setSessionId] = useState("");
  const [currentMeta, setCurrentMeta] = useState(null); // { difficulty, challenge }

  const [isRecording, setIsRecording] = useState(false);
  const [mediaStream, setMediaStream] = useState(null);
  const [visionMetrics, setVisionMetrics] = useState({ attention: "unknown", emotion_score: 0, composure_score: null, dominant_emotion: null });

  const [speaking, setSpeaking] = useState(false);
  const [ttsMuted, setTtsMuted] = useState(false);
  const [warning, setWarning] = useState("");

  const textareaRef = useRef(null);
  const timerRef = useRef(null);
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const visionIntervalRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const sessionIdRef = useRef("");
  const spokenRef = useRef("");
  const activeRef = useRef(false);
  const endedRef = useRef(false);
  const violationsRef = useRef(0);

  const started = Boolean(interview.currentQuestion);
  const qNumber = Math.min(interview.questionHistory.length + 1, MAX_QUESTIONS);

  /* ── Media Devices ── */
  useEffect(() => {
    let stream = null;
    async function enableMedia() {
      if (interview.webcamAnalysis || interview.voiceInput) {
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: interview.webcamAnalysis,
            audio: interview.voiceInput,
          });
          setMediaStream(stream);
          mediaStreamRef.current = stream;
          if (videoRef.current) videoRef.current.srcObject = stream;
        } catch (err) {
          console.error("Failed to access media devices", err);
          setError("Camera/microphone access denied or unavailable.");
        }
      }
    }
    enableMedia();
    return () => {
      if (stream) stream.getTracks().forEach((track) => track.stop());
    };
  }, [interview.webcamAnalysis, interview.voiceInput]);

  /* ── Vision polling ── */
  useEffect(() => {
    if (!interview.webcamAnalysis || !mediaStream || status !== "idle" || !interview.currentQuestion) return;

    visionIntervalRef.current = setInterval(async () => {
      if (videoRef.current && videoRef.current.readyState === 4) {
        const canvas = document.createElement("canvas");
        canvas.width = videoRef.current.videoWidth;
        canvas.height = videoRef.current.videoHeight;
        canvas.getContext("2d").drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(async (blob) => {
          if (!blob) return;
          try {
            const res = await analyzeVisionFrame(blob);
            if (res.status === "ok" && res.vision) {
              setVisionMetrics((prev) => ({
                ...prev,
                attention: res.vision.attention || prev.attention,
                emotion_score: res.vision.emotion_score !== undefined ? res.vision.emotion_score : prev.emotion_score,
                composure_score: res.vision.composure_score !== undefined && res.vision.composure_score !== null ? res.vision.composure_score : prev.composure_score,
                dominant_emotion: res.vision.dominant_emotion || prev.dominant_emotion,
              }));
            }
          } catch (e) {
            console.error("Vision polling error", e);
          }
        }, "image/jpeg", 0.7);
      }
    }, 3000);

    return () => clearInterval(visionIntervalRef.current);
  }, [interview.webcamAnalysis, mediaStream, status, interview.currentQuestion]);

  /* ── Countdown timer ── */
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

  /* ── Auto-submit on timeout ── */
  useEffect(() => {
    if (timeLeft === 0 && status === "idle" && interview.currentQuestion) {
      handleSubmit("Time is up - no answer provided.");
    }
  }, [timeLeft, status, interview.currentQuestion]);

  /* ── Speak each new question aloud ── */
  useEffect(() => {
    const q = interview.currentQuestion;
    if (q && q !== spokenRef.current) {
      spokenRef.current = q;
      speak(q);
    }
  }, [interview.currentQuestion]);

  /* ── Proctoring: warn once, then close on leaving the window ── */
  useEffect(() => {
    function onLeave() {
      if (!activeRef.current) return;
      violationsRef.current += 1;
      if (violationsRef.current >= 2) {
        closeInterview("Your interview was closed because you left the window.");
      } else {
        setWarning("Please stay on this window. Leaving again will end your interview.");
        window.setTimeout(() => setWarning(""), 6000);
      }
    }
    function onVisibility() { if (document.hidden) onLeave(); }
    function onFsChange() { if (!document.fullscreenElement) onLeave(); }

    document.addEventListener("visibilitychange", onVisibility);
    document.addEventListener("fullscreenchange", onFsChange);
    return () => {
      document.removeEventListener("visibilitychange", onVisibility);
      document.removeEventListener("fullscreenchange", onFsChange);
    };
  }, []);

  /* ── Warn before a hard refresh / tab close during the interview ── */
  useEffect(() => {
    function beforeUnload(e) {
      if (activeRef.current) {
        e.preventDefault();
        e.returnValue = "";
      }
    }
    window.addEventListener("beforeunload", beforeUnload);
    return () => window.removeEventListener("beforeunload", beforeUnload);
  }, []);

  /* ── Cleanup on unmount ── */
  useEffect(() => {
    return () => {
      stopSpeaking();
      try { mediaStreamRef.current?.getTracks().forEach((t) => t.stop()); } catch (e) {}
    };
  }, []);

  /* ── Text-to-speech ── */
  function speak(text, force = false) {
    if (!text || (ttsMuted && !force)) return;
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 1;
    u.pitch = 1;
    u.onstart = () => setSpeaking(true);
    u.onend = () => setSpeaking(false);
    u.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(u);
  }
  function stopSpeaking() {
    if (typeof window !== "undefined" && "speechSynthesis" in window) window.speechSynthesis.cancel();
    setSpeaking(false);
  }
  function toggleTts() {
    if (ttsMuted) {
      setTtsMuted(false);
      speak(interview.currentQuestion, true);
    } else {
      setTtsMuted(true);
      stopSpeaking();
    }
  }

  /* ── Fullscreen ── */
  function enterFullscreen() {
    const el = document.documentElement;
    if (el.requestFullscreen) el.requestFullscreen().catch(() => {});
  }

  /* ── Close / end the interview (single exit path) ── */
  function closeInterview(notice) {
    endedRef.current = true;
    activeRef.current = false;
    stopSpeaking();
    try { mediaStreamRef.current?.getTracks().forEach((t) => t.stop()); } catch (e) {}
    try { if (document.fullscreenElement) document.exitFullscreen(); } catch (e) {}
    const sid = sessionIdRef.current;
    navigate(sid ? `/dashboard?session_id=${sid}` : "/dashboard", notice ? { state: { notice } } : undefined);
  }

  /* ── Draft helpers ── */
  function handleDraftChange(e) {
    setDraft(e.target.value);
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 140) + "px";
    }
  }
  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  /* ── Start the interview ── */
  async function handleStart() {
    enterFullscreen();
    setStatus("generating");
    setError("");
    setTimeLeft(120);
    try {
      if (!sessionId) {
        let userEmail = "";
        let fullName = "";
        try {
          const user = JSON.parse(localStorage.getItem("user") || "null");
          if (user) { userEmail = user.email; fullName = user.full_name; }
        } catch (e) {}

        const data = await startInterview({
          mode: interview.selectedAgent,
          role: interview.selectedRole,
          difficulty: interview.difficulty,
          user_email: userEmail,
          full_name: fullName,
        });
        setSessionId(data.session_id);
        sessionIdRef.current = data.session_id;
        activeRef.current = true;
        const q = data.question;
        interview.updateInterview({ currentQuestion: q.question, currentAnswer: "" });
        setCurrentMeta({ difficulty: q.difficulty, challenge: false });
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setStatus("idle");
    }
  }

  /* ── Voice recording ── */
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
      recorder.ondataavailable = (e) => { if (e.data.size > 0) audioChunksRef.current.push(e.data); };
      recorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        handleSubmit(null, audioBlob);
      };
      recorder.start();
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
    }
  }

  /* ── Submit answer ── */
  async function handleSubmit(forcedAnswer = null, audioBlob = null) {
    const answer = typeof forcedAnswer === "string" ? forcedAnswer : draft.trim();
    if (!interview.currentQuestion) { setError("Start the interview first."); return; }
    if (!answer && !audioBlob) { setError("Type or record your answer before submitting."); return; }

    setError("");
    setDraft("");
    setTimeLeft(120);
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    stopSpeaking();
    setStatus("evaluating");

    try {
      const data = await submitAnswer({
        session_id: sessionId,
        mode: interview.selectedAgent,
        answer_text: audioBlob ? "" : answer,
        audioBlob,
        vision_metrics: interview.webcamAnalysis ? visionMetrics : {},
      });

      const { evaluation, next_question, is_complete } = data;
      const score = evaluation?.overall_rating || evaluation?.technical_score || evaluation?.communication_score || evaluation?.teamwork_score || 0;

      interview.addEvaluation({
        agent: interview.selectedAgent,
        question: interview.currentQuestion,
        answer,
        score,
        feedback: evaluation?.feedback || evaluation?.answer_summary || "Evaluation complete.",
        followup: next_question?.question || null,
        emotion_score: interview.webcamAnalysis ? (visionMetrics.emotion_score || 0) : 0,
        composure: interview.webcamAnalysis ? visionMetrics.composure_score : null,
        emotion: interview.webcamAnalysis ? visionMetrics.dominant_emotion : null,
      });

      interview.updateInterview({ currentAnswer: answer });

      if (is_complete || interview.questionHistory.length + 1 >= MAX_QUESTIONS) {
        closeInterview(null);
      } else if (next_question) {
        interview.updateInterview({ currentQuestion: next_question.question, currentAnswer: "" });
        setCurrentMeta({ difficulty: next_question.difficulty, challenge: (next_question.category || "").endsWith("debate") });
      }
    } catch (err) {
      if (err.response?.status === 422 && err.response?.data?.status === "transcription_unavailable") {
        setError("Speech model unavailable. Please type your answer instead.");
      } else {
        setError(err.response?.data?.error || err.message);
      }
    } finally {
      setStatus("idle");
    }
  }

  /* ── Turn label ── */
  let turnLabel = "Ready";
  if (status === "generating") turnLabel = "Preparing your question…";
  else if (speaking) turnLabel = "Interviewer is asking…";
  else if (status === "evaluating") turnLabel = "Evaluating your answer…";
  else if (isRecording) turnLabel = "Recording your answer…";
  else if (interview.currentQuestion) turnLabel = "Your turn to answer";

  return (
    <div className="interview-room">
      {/* Top bar */}
      <div className="ir-topbar">
        <div className="ir-title">HireSense · {interview.selectedRole || "Interview"}</div>
        {started && <div className="ir-counter">Question {qNumber} of {MAX_QUESTIONS}</div>}
        <button className="ir-exit" type="button" onClick={() => closeInterview(null)}>
          <Square size={13} /> Exit
        </button>
      </div>

      {warning && (
        <div className="ir-warning"><AlertTriangle size={16} /> {warning}</div>
      )}

      {/* Stage */}
      <div className="ir-stage">
        {/* Interviewer */}
        <div className="ir-interviewer">
          <div className={`ir-avatar${speaking ? " speaking" : ""}`}><Bot size={34} /></div>
          <div className="ir-name">AI {interview.selectedAgent || ""} Interviewer</div>
          <div className={`ir-turn${isRecording ? " rec" : ""}`}>{turnLabel}</div>
        </div>

        {/* Question / start */}
        <div className="ir-center">
          {!started ? (
            <div className="ir-ready">
              <p className="ir-ready-hi">Ready when you are.</p>
              <p className="ir-ready-sub">
                I'll ask you {MAX_QUESTIONS} questions for the <strong>{interview.selectedRole || "selected"}</strong> role.
                Answer by {interview.voiceInput ? "voice or typing" : "typing"}. Stay on this window — leaving ends the interview.
              </p>
              <button className="primary-link as-button ir-start" type="button" disabled={status === "generating"} onClick={handleStart}>
                {status === "generating"
                  ? <><Loader2 className="spin" size={16} /> Starting…</>
                  : <>Start interview <ChevronRight size={16} /></>}
              </button>
            </div>
          ) : (
            <div className={`ir-question${currentMeta?.challenge ? " challenge" : ""}`}>
              <div className="ir-q-top">
                <span className="ir-q-label">{currentMeta?.challenge ? "🔥 Debate Challenge" : `Question ${qNumber}`}</span>
                {currentMeta?.difficulty && (
                  <span className={`meta-badge difficulty-${currentMeta.difficulty}`}>{currentMeta.difficulty}</span>
                )}
                <span className="ir-q-actions">
                  <button className="ir-tts" type="button" title={ttsMuted ? "Unmute interviewer" : "Mute interviewer"} onClick={toggleTts}>
                    {ttsMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
                  </button>
                  {!ttsMuted && (
                    <button className="ir-tts" type="button" title="Replay question" onClick={() => speak(interview.currentQuestion, true)}>
                      <RotateCcw size={15} />
                    </button>
                  )}
                </span>
              </div>
              <p className="ir-q-text">{interview.currentQuestion}</p>
            </div>
          )}
        </div>

        {/* Candidate */}
        <div className="ir-candidate">
          {interview.webcamAnalysis ? (
            <video ref={videoRef} autoPlay muted playsInline className="ir-video" />
          ) : (
            <div className="ir-video ir-video-off"><Video size={26} /><span>Webcam off</span></div>
          )}
          <div className="ir-you">You</div>
        </div>
      </div>

      {/* Controls */}
      {started && (
        <div className="ir-controls">
          <div className="ir-timer"><Timer timeLeft={timeLeft} /></div>

          {interview.voiceInput && (
            <button
              className={`ir-mic${isRecording ? " rec" : ""}`}
              type="button"
              disabled={status !== "idle"}
              onClick={toggleRecording}
              title={isRecording ? "Stop & submit" : "Record answer"}
            >
              {isRecording ? <MicOff size={24} /> : <Mic size={24} />}
              <span>{isRecording ? "Stop & submit" : "Record answer"}</span>
            </button>
          )}

          <div className="ir-typebox">
            <textarea
              ref={textareaRef}
              className="ir-input"
              rows={1}
              maxLength={2000}
              value={draft}
              disabled={status !== "idle"}
              onChange={handleDraftChange}
              onKeyDown={handleKeyDown}
              placeholder={status !== "idle" ? "Please wait…" : "Type your answer… (Enter to send)"}
            />
            <button className="ir-send" type="button" disabled={status !== "idle" || !draft.trim()} onClick={() => handleSubmit()}>
              {status === "evaluating" ? <Loader2 className="spin" size={18} /> : <Send size={18} />}
            </button>
          </div>
        </div>
      )}

      {error && <p className="ir-error">{error}</p>}
    </div>
  );
}
