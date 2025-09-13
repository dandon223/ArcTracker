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

    if (!username.trim()) {
      alert("Username is required");
      return;
    }

    if (!password.trim()) {
      alert("Password is required");
      return;
    }

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
    <form onSubmit={handleRegister}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <input
        type="password"
        value={password2}
        onChange={(e) => setPassword2(e.target.value)}
        placeholder="Repeat Password"
      />
      <button type="submit">Register</button>
    </form>
  );
}