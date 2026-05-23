import api from "./api";

export async function generateQuestion(payload) {
  const response = await api.post("/interview/generate-question/", payload);
  return response.data;
}

export async function evaluateResponse(payload) {
  const response = await api.post("/interview/evaluate-response/", payload);
  return response.data;
}

export async function startInterview(payload) {
  const response = await api.post("/interview/start/", payload);
  return response.data;
}

export async function submitAnswer(payload) {
  if (payload.audioBlob) {
    const formData = new FormData();
    formData.append("session_id", payload.session_id);
    if (payload.answer_text) {
      formData.append("answer_text", payload.answer_text);
    }
    if (payload.speech_metrics) {
      formData.append("speech_metrics", JSON.stringify(payload.speech_metrics));
    }
    if (payload.vision_metrics) {
      formData.append("vision_metrics", JSON.stringify(payload.vision_metrics));
    }
    formData.append("audio_file", payload.audioBlob, "recording.webm");
    
    const response = await api.post("/interview/answer/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return response.data;
  }
  
  const response = await api.post("/interview/answer/", payload);
  return response.data;
}

export async function analyzeVisionFrame(imageBlob) {
  const formData = new FormData();
  formData.append("image_file", imageBlob, "frame.jpg");
  const response = await api.post("/vision/analyze/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return response.data;
}

export async function evaluateAnswer(payload) {
  const response = await api.post("/interview/evaluate/", payload);
  return response.data;
}

export async function getInterviewReport(sessionId) {
  const response = await api.get(`/interview/report/?session_id=${sessionId}`);
  return response.data;
}

export async function getInterviewHistory() {
  const response = await api.get("/interview/history/");
  return response.data;
}
