import React from "react";

const InterviewContext = React.createContext(null);

const initialState = {
  selectedRole: "Java Developer",
  selectedAgent: "technical",
  difficulty: "medium",
  adaptiveMode: true,
  voiceInput: false,
  webcamAnalysis: false,
  followUps: true,
  currentQuestion: "",
  currentAnswer: "",
  questionNumber: 1,
  questionHistory: [],
  scores: [],
  feedback: [],
  followUpQuestions: [],
  finalReport: null
};

export function InterviewProvider({ children }) {
  const [state, setState] = React.useState(initialState);

  const updateInterview = (updates) => {
    setState((current) => ({
      ...current,
      ...updates
    }));
  };

  const addEvaluation = (entry) => {
    setState((current) => ({
      ...current,
      questionHistory: [...current.questionHistory, entry],
      scores: [...current.scores, entry.score],
      feedback: [...current.feedback, entry.feedback],
      followUpQuestions: entry.followup
        ? [...current.followUpQuestions, entry.followup]
        : current.followUpQuestions,
      questionNumber: current.questionNumber + 1
    }));
  };

  const resetInterview = () => {
    setState(initialState);
  };

  const clearProgress = () => {
    setState((current) => ({
      ...current,
      currentQuestion: "",
      currentAnswer: "",
      questionNumber: 1,
      questionHistory: [],
      scores: [],
      feedback: [],
      followUpQuestions: [],
      finalReport: null
    }));
  };

  return (
    <InterviewContext.Provider
      value={{
        ...state,
        updateInterview,
        addEvaluation,
        resetInterview,
        clearProgress
      }}
    >
      {children}
    </InterviewContext.Provider>
  );
}

export function useInterview() {
  const context = React.useContext(InterviewContext);

  if (!context) {
    throw new Error("useInterview must be used inside InterviewProvider");
  }

  return context;
}
