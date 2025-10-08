import { useState } from "react";
const API_URL = import.meta.env.VITE_API_URL;
import { getCookie } from "./csrf";

export default function AddCardForm(props) {
    const [selectedPlayerId, setSelectedPlayerId] = useState(null);
    const [numberOfCardsToAdd, setNumberOfCardsToAdd] = useState(0)
    
    const handlePlayCard = async (e) => {
        e.preventDefault();

        if (!selectedPlayerId) {
        alert("Please select a player");
        return;
        }

        const response = await fetch(`${API_URL}/api/games/${props.game.id}/players/${selectedPlayerId}/hand/add`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json"
        },
        body: JSON.stringify({ number_of_cards: numberOfCardsToAdd}),
        credentials: "include",
        });
        const data = await response.json();
        if (!response.ok) {
        alert(data.detail);
        return
        }
        setSelectedPlayerId(null);
        props.reloadAfterPlayCard()

    };

    return  <form className="PlayCardForm" onSubmit={handlePlayCard}>
                <div className="formRow">
                    <label>Player:</label>
                    <div className="playersList">
                        {props.players.map((player) => (
                        <label key={player.id} className="playerOption">
                            <input
                            type="radio"
                            name="selectedPlayer"
                            value={player.id}
                            checked={selectedPlayerId === player.id}
                            onChange={() => setSelectedPlayerId(player.id)}
                            />
                            {player.nick}
                        </label>
                        ))}
                    </div>
                </div>

                <div className="formRow">
                    <label>Number of cards to add:</label>
                    <input
                        type="number"
                        value={numberOfCardsToAdd}
                        onChange={(e) => setNumberOfCardsToAdd(Number(e.target.value))}
                        className="number-input"
                    />
                </div>
            <button className="button" type="submit">Add Cards</button>
        </form>
}