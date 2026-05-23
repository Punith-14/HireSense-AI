import { Route, Routes } from "react-router-dom";
import About from "../pages/About.jsx";
import Dashboard from "../pages/Dashboard.jsx";
import History from "../pages/History.jsx";
import Home from "../pages/Home.jsx";
import InterviewSession from "../pages/InterviewSession.jsx";
import InterviewSetup from "../pages/InterviewSetup.jsx";
import Login from "../pages/Login.jsx";
import Signup from "../pages/Signup.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/interview" element={<InterviewSetup />} />
      <Route path="/session" element={<InterviewSession />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/history" element={<History />} />
      <Route path="/about" element={<About />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
    </Routes>
  );
}
