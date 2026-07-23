import { Route, Routes } from "react-router-dom";
import About from "../pages/About.jsx";
import Dashboard from "../pages/Dashboard.jsx";
import History from "../pages/History.jsx";
import Home from "../pages/Home.jsx";
import InterviewSession from "../pages/InterviewSession.jsx";
import InterviewSetup from "../pages/InterviewSetup.jsx";
import Login from "../pages/Login.jsx";
import Signup from "../pages/Signup.jsx";
import ProtectedRoute from "./ProtectedRoute.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      {/* Public */}
      <Route path="/" element={<Home />} />
      <Route path="/about" element={<About />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      {/* Require a logged-in user */}
      <Route path="/interview" element={<ProtectedRoute><InterviewSetup /></ProtectedRoute>} />
      <Route path="/session" element={<ProtectedRoute><InterviewSession /></ProtectedRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
    </Routes>
  );
}
