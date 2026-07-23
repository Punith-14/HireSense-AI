import { useLocation } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Footer from "./components/Footer.jsx";
import AppRoutes from "./routes/AppRoutes.jsx";

export default function App() {
  const location = useLocation();
  // The interview session runs in an immersive, full-screen "interview room"
  // with no site chrome around it.
  const immersive = location.pathname === "/session";

  return (
    <div className="app">
      {!immersive && <Navbar />}
      <AppRoutes />
      {!immersive && <Footer />}
    </div>
  );
}
