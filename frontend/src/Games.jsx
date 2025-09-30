import { useState, useEffect } from "react";
import { getCookie } from "./csrf";
import { useNavigate } from "react-router-dom";
import Game from "./Game";

const API_URL = import.meta.env.VITE_API_URL;

export default function Games() {
    const [players, setPlayers] = useState([]);
    const [games, setGames] = useState([]);
    const [name, setName] = useState("")
    const [selectedPlayers, setSelectedPlayers] = useState([]);
    const gamesList = games.map(game => <Game key={game.id} game={game} />);
    const navigate = useNavigate();

    useEffect(() => {
        fetch(`${API_URL}/api/players/`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} })
            .then((res) => res.json())
            .then((data) => setPlayers(data));
      }, []);

    useEffect(() => {
        fetch(`${API_URL}/api/games/`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} })
            .then((res) => res.json())
            .then((data) => setGames(data));
      }, []);

    const handleAddGame = async (e) => {
        e.preventDefault();

        const response = await fetch(`${API_URL}/api/games/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json"
        },
        body: JSON.stringify({ name, players: selectedPlayers }),
        credentials: "include",
        });
        const data = await response.json();
        if (!response.ok) {
        alert(data.detail);
        return
        }
        setName("")
        setGames(prev => [...prev, data])
        setSelectedPlayers([])
        navigate(`/games/${data.name}`);

    };

    return  <section className="games">

        <div>
            {games.length > 0 && <h3>Games:</h3>}
            <ul className="gamesList">{gamesList}</ul>
        </div>
        <form className="AddGameForm" onSubmit={handleAddGame}>
            <div className="formRow">
            <label>Name:</label>
            <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value.trim())}
                placeholder="name"
                required
            />
            </div>

            <div className="formRow">
                <label>Players:</label>
                <div className="playersList">
                {players.map((player) => (
                    <label key={player.id} className="playerOption">
                    <input
                        type="checkbox"
                        value={player.id}
                        checked={selectedPlayers.includes(player.id)}
                        onChange={(e) => {
                        if (e.target.checked) {
                            setSelectedPlayers([...selectedPlayers, player.id]);
                        } else {
                            setSelectedPlayers(
                            selectedPlayers.filter((id) => id !== player.id)
                            );
                        }
                        }}
                    />
                    {player.nick}
                    </label>
                ))}
                </div>
            </div>
            <button className="button" type="submit">New Game</button>
        </form>
    </section>
    }
