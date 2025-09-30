import React from "react";
import { useNavigate } from "react-router-dom";

export default function Game({ game }) {
  const navigate = useNavigate();

  return (
    <li
      className="game"
      onClick={() => navigate(`/games/${game.name}`)}
      style={{ cursor: "pointer" }}
    >
      <h4>{game.name}</h4>
    </li>
  );
}