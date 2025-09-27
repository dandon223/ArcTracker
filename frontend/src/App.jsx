import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import { useState, useEffect } from "react";
import Header from "./Header";
import Login from "./Login";
import Register from "./Register";
import Menu from "./Menu";
import Players from "./Players";
import Games from "./Games"
import CurrentGame from "./CurrentGame";

const API_URL = import.meta.env.VITE_API_URL;

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch(`${API_URL}/api/me/`, { 
        credentials: "include",
        headers:{"Accept": "application/json"} })
      .then((res) => res.json())
      .then((data) => {
        setUser(data.username || null);
        setLoading(false);
      });
  }, []);
  
  useEffect(() => {
    fetch(`${API_URL}/api/csrf/`, {
        credentials: "include",
    });
    }, []);

  return (
    <Router>
        {loading ? (
          <div className="loading-overlay">
            <div className="spinner"></div>
          </div>
        ) : (
      <>
      <Header user={user} setUser={setUser}/>
      <main>
        <Routes>
          <Route path="/" element={user ? <Menu/> : null}/>
          <Route path="/login" element={<Login setUser={setUser} />} />
          <Route path="/register" element={<Register setUser={setUser} />} />
          <Route path="/players" element={<Players />} />
          <Route path="/games" element={<Games />} />
          <Route path="/games/:name" element={<CurrentGame />} />
        </Routes>
      </main>
      </>
    )}
    </Router>
  );
}
