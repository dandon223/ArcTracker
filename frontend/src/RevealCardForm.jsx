import { useState, useEffect } from "react";
const API_URL = import.meta.env.VITE_API_URL;
import { getCookie } from "./csrf";

export default function RevealCardForm(props) {
    const [selectedPlayerId, setSelectedPlayerId] = useState(null);
    const [cardId, setCardId] = useState(null);
    const [cardsToReveal, setCardsToReveal] = useState([])
    
    const handleRevealCard = async (e) => {
        e.preventDefault();

        if (!selectedPlayerId) {
        alert("Please select a player");
        return;
        }

        const response = await fetch(`${API_URL}/api/games/${props.game.id}/players/${selectedPlayerId}/hand/reveal`, {
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
        props.reloadAfterRevealCard()

    };

    useEffect(() => {
        if (!props.game)
            return;        
        setCardsToReveal([...props.game.cards_not_played].map(card => props.cardIdToCard[card]))
      }, [props.game]);

    return  <form className="RevealCardForm" onSubmit={handleRevealCard}>
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
                    <label>Card to reveal:</label>
                    <select
                        value={cardId || ""}  // empty string = no selection
                        onChange={(e) => {
                        setCardId(e.target.value || null);
                        }}
                    >
                        <option value="">-- Choose card --</option>  {/* optional "no selection" */}
                        {cardsToReveal.map((card) => (
                        <option key={card.id} value={card.id}>
                            {card.suit} {card.number}
                        </option>
                        ))}
                    </select>
                </div>
            <button className="button" type="submit">Reveal Card</button>
        </form>
}