import { evaluateResponse, generateQuestion } from "./interviewApi";

export function generateHrQuestion(role) {
  return generateQuestion({
    interview_type: "hr",
    role
  });
}

export function evaluateHrResponse(question, answer) {
  return evaluateResponse({
    interview_type: "hr",
    question,
    answer
  });
}
