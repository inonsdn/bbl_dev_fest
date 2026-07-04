import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth.jsx";
import Login from "./pages/Login.jsx";
import Booking from "./pages/Booking.jsx";

// Redirects to the login page when there is no active session.
function RequireAuth({ children }) {
  const { auth } = useAuth();
  return auth ? children : <Navigate to="/login" replace />;
}

export default function App() {
  const { auth } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={auth ? <Navigate to="/booking" replace /> : <Login />}
      />
      <Route
        path="/booking"
        element={
          <RequireAuth>
            <Booking />
          </RequireAuth>
        }
      />
      <Route path="*" element={<Navigate to={auth ? "/booking" : "/login"} replace />} />
    </Routes>
  );
}
