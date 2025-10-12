import { useState, useEffect } from "react";
const API_URL = import.meta.env.VITE_API_URL;
import { getCookie } from "./csrf";

export default function RetrieveCardForm(props) {
    const [selectedPlayerId, setSelectedPlayerId] = useState(null);
    const [cardId, setCardId] = useState(null);
    const [cardsToRetrieve, setCardsToRetrieve] = useState([])
    
    const handleRetrieveCard = async (e) => {
        e.preventDefault();

        if (!selectedPlayerId) {
        alert("Please select a player");
        return;
        }

        const response = await fetch(`${API_URL}/api/games/${props.game.id}/players/${selectedPlayerId}/hand/retrieve`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json"
        },
        body: JSON.stringify({ id: cardId}),
        credentials: "include",
        });
        const data = await response.json();
        if (!response.ok) {
        alert(data.detail);
        return
        }
        setSelectedPlayerId(null);
        setCardId(null);
        props.reloadAfterRetrieveCard()

    };

    useEffect(() => {
        if (!selectedPlayerId) return;
        fetch(`${API_URL}/api/games/${props.game.id}/retrieve/cards`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} })
            .then((res) => res.json())
            .then((data) => setCardsToRetrieve(data));
      }, [selectedPlayerId]);

    return  <form className="RetrieveCardForm" onSubmit={handleRetrieveCard}>
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
                    <label>Card to Retrieve:</label>
                    <select
                        value={cardId || ""}  // empty string = no selection
                        onChange={(e) => {
                        setCardId(e.target.value || null);
                        }}
                    >
                        <option value="">-- Choose card --</option>  {/* optional "no selection" */}
                        {cardsToRetrieve.map((card) => (
                        <option key={card.id} value={card.id}>
                            {card.suit} {card.number}
                        </option>
                        ))}
                    </select>
                </div>
            <button className="button" type="submit">Retrieve Card</button>
        </form>
}