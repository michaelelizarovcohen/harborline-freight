import { NavLink, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import Dashboard from "./pages/Dashboard.jsx";
import NewBooking from "./pages/NewBooking.jsx";
import Tracking from "./pages/Tracking.jsx";
import Invoices from "./pages/Invoices.jsx";
import Login from "./pages/Login.jsx";
import { api, session } from "./api/client.js";

function RequireAuth({ children }) {
  if (!session.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  const [account, setAccount] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!session.isAuthenticated()) return;
    api
      .get("/v1/me")
      .then(setAccount)
      .catch(() => {
        session.clear();
        navigate("/login");
      });
  }, [navigate]);

  function logout() {
    session.clear();
    setAccount(null);
    navigate("/login");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <span className="brand">
          <span className="brand-mark">⚓</span> Harborline Book
        </span>
        {session.isAuthenticated() && (
          <nav>
            <NavLink to="/">Dashboard</NavLink>
            <NavLink to="/book">New booking</NavLink>
            <NavLink to="/track">Track</NavLink>
            <NavLink to="/invoices">Invoices</NavLink>
          </nav>
        )}
        {account && (
          <div className="account">
            <span>{account.company_name}</span>
            <button className="link" onClick={logout}>
              Sign out
            </button>
          </div>
        )}
      </header>
      <main>
        <Routes>
          <Route path="/login" element={<Login onLogin={setAccount} />} />
          <Route
            path="/"
            element={
              <RequireAuth>
                <Dashboard />
              </RequireAuth>
            }
          />
          <Route
            path="/book"
            element={
              <RequireAuth>
                <NewBooking />
              </RequireAuth>
            }
          />
          <Route
            path="/track/:reference?"
            element={
              <RequireAuth>
                <Tracking />
              </RequireAuth>
            }
          />
          <Route
            path="/invoices"
            element={
              <RequireAuth>
                <Invoices />
              </RequireAuth>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <footer className="footer">
        © Harborline Freight, Inc. · <a href="mailto:support@harborline.example">support@harborline.example</a>
      </footer>
    </div>
  );
}
