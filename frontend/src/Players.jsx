import { useState, useEffect } from "react";
import { getCookie } from "./csrf";

const API_URL = import.meta.env.VITE_API_URL;

export default function Players() {
    const [players, setPlayers] = useState([]);
    const [nick, setNick] = useState("")
    const playersList = players.map(player => (
        <li key={player.id} className="playerItem">
            <h4>{player.nick}</h4>
        </li>
    ))

    useEffect(() => {
        fetch(`${API_URL}/api/players/`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} })
            .then((res) => res.json())
            .then((data) => setPlayers(data));
      }, []);

    const handleAddPlayer = async (e) => {
        e.preventDefault();

        const response = await fetch(`${API_URL}/api/players/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json"
        },
        body: JSON.stringify({ nick }),
        credentials: "include",
        });
        const data = await response.json();
        if (!response.ok) {
        alert(data.detail);
        return
        }
        setNick("")
        setPlayers(prev => [...prev, data])

    };

    return  <section className="players">

        <div>
            {players.length > 0 && <h3>Players:</h3>}
            <ul className="playersList">{playersList}</ul>
        </div>
        <form className="AddPlayerForm" onSubmit={handleAddPlayer}>
            <div className="formRow">
            <label>Nick:</label>
            <input
                type="text"
                value={nick}
                onChange={(e) => setNick(e.target.value.trim())}
                placeholder="nick"
                required
            />
            </div>
            <button className="button" type="submit">Add Player</button>
        </form>
    </section>
    }
