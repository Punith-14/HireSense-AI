import { evaluateResponse, generateQuestion } from "./interviewApi";

export function generateBehavioralQuestion(topic) {
  return generateQuestion({
    interview_type: "behavioral",
    topic
  });
}

export function evaluateBehavioralResponse(question, answer) {
  return evaluateResponse({
    interview_type: "behavioral",
    question,
    answer
  });
}
