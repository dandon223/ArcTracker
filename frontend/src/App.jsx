import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import Header from "./Header";
import Login from "./Login";
import Register from "./Register";
import { getCookie } from "./csrf";

const API_URL = import.meta.env.VITE_API_URL;

export default function App() {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetch(`${API_URL}/api/me/`, { 
        credentials: "include",
        headers:{"Accept": "application/json"} })
      .then((res) => res.json())
      .then((data) => setUser(data.username || null));
  }, []);
  
  useEffect(() => {
    fetch(`${API_URL}/api/csrf/`, {
        credentials: "include",
    });
    }, []);

  const handleLogout = async () => {
    await fetch(`${API_URL}/api/logout/`, {
      method: "POST",
      credentials: "include",
      
      headers:{
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        "Accept": "application/json"}
    });
    setUser(null);
  };

  return (
    <Router>
      <Header user={user} onLogout={handleLogout} />
      <main>
        <Routes>
          <Route
            path="/"
            element={
              <div>
                {user ? (
                  <p>Welcome, {user}!</p>
                ) : (
                  null
                )}
              </div>
            }
          />
          <Route path="/login" element={<Login setUser={setUser} />} />
          <Route path="/register" element={<Register setUser={setUser} />} />
        </Routes>
      </main>
    </Router>
  );
}
