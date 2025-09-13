import { useState } from "react";
import { getCookie } from "./csrf";
import { useNavigate } from "react-router-dom";

const API_URL = import.meta.env.VITE_API_URL;

export default function Login(props) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    const response = await fetch(`${API_URL}/api/login/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        "Accept": "application/json"
      },
      body: JSON.stringify({ username, password }),
      credentials: "include", // important for session cookies
    });
    const data = await response.json();
    if (!response.ok) {
      alert("Login failed. Please check your input.");
      return;
    }
    props.setUser(data.username);
    navigate("/");
  };

  return (
  <form className="loginForm" onSubmit={handleLogin}>
    <div className="formRow">
      <label>Username:</label>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value.trim())}
        placeholder="username"
        required
      />
    </div>

    <div className="formRow">
      <label>Password:</label>
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value.trim())}
        placeholder="password"
        required
      />
    </div>

    <button className="button" type="submit">Login</button>
  </form>
  );
}