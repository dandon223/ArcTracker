import { useState, useEffect } from "react";
const API_URL = import.meta.env.VITE_API_URL;
import { getCookie } from "./csrf";

export default function UnrevealCardForm(props) {
    const [selectedPlayerId, setSelectedPlayerId] = useState(null);
    const [cardId, setCardId] = useState(null);
    const [cardsToUnreveal, setCardsToUnreveal] = useState([])
    
    const handleUnRevealCard = async (e) => {
        e.preventDefault();

        if (!selectedPlayerId) {
        alert("Please select a player");
        return;
        }

        const response = await fetch(`${API_URL}/api/games/${props.game.id}/players/${selectedPlayerId}/hand/unreveal`, {
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
        props.reloadAfterUnrevealCard()

    };

    useEffect(() => {
        const getPlayerHandFromAPI = async () => {
            try {
                const res = await fetch(`${API_URL}/api/games/${props.game.id}/players/${selectedPlayerId}/hand`, { 
                    credentials: "include",
                    headers: { "Accept": "application/json" }
                });
                const playerHandData = await res.json();
                const cardsToUnreveal = playerHandData.cards.map(card => props.cardIdToCard[card])
                setCardsToUnreveal(cardsToUnreveal)
            } catch (err) {
                console.error("Failed to fetch cards:", err);
            }
        };
        if (!selectedPlayerId)
            return;
        getPlayerHandFromAPI()

    }, [selectedPlayerId]);

    return  <form className="UnrevealCardForm" onSubmit={handleUnRevealCard}>
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
                    <label>Card to unreveal:</label>
                    <select
                        value={cardId || ""}  // empty string = no selection
                        onChange={(e) => {
                        setCardId(e.target.value || null);
                        }}
                    >
                        <option value="">-- Choose card --</option>  {/* optional "no selection" */}
                        {cardsToUnreveal.map((card) => (
                        <option key={card.id} value={card.id}>
                            {card.suit} {card.number}
                        </option>
                        ))}
                    </select>
                </div>
            <button className="button" type="submit">Unreveal Card</button>
        </form>
}