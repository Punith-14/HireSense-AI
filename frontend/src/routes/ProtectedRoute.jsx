import { Navigate, useLocation } from "react-router-dom";

/**
 * Guards routes that require a logged-in user. If no auth token is present,
 * the user is redirected to /login (remembering where they were headed).
 */
export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const token = localStorage.getItem("token");

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return children;
}
