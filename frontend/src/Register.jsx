import { useState } from "react";
import { getCookie } from "./csrf";
import { useNavigate } from "react-router-dom";

const API_URL = import.meta.env.VITE_API_URL;

export default function Register(props) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");

  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();

    if (password !== password2) {
      alert("Passwords do not match");
      return;
    }
    const response = await fetch(`${API_URL}/api/register/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        "Accept": "application/json"
      },
      body: JSON.stringify({ username, password }),
      credentials: "include",
    });

    const data = await response.json();
    if (!response.ok) {
      const messages = Object.entries(data)
        .map(([, errors]) => {
          // Ensure errors is always an array
          const errorList = Array.isArray(errors) ? errors : [errors];
          return `${errorList.join(", ")}`;
        })
        .join("\n");

      alert(messages || "Registration failed. Please check your input.");
      return;
    }
    props.setUser(data.username);
    navigate("/");
  };

  return (
  <form className="registerForm" onSubmit={handleRegister}>
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

    <div className="formRow">
      <label>Repeat Password:</label>
      <input
        type="password"
        value={password2}
        onChange={(e) => setPassword2(e.target.value.trim())}
        placeholder="repeat password"
        required
      />
    </div>

    <button className="button" type="submit">Register</button>
  </form>
  );
}