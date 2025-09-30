import { useState, useEffect } from "react";
const API_URL = import.meta.env.VITE_API_URL;
import { getCookie } from "./csrf";

export default function PlayCardForm(props) {
    const [selectedPlayerId, setSelectedPlayerId] = useState(null);
    const [cardFaceUpId, setCardFaceUpId] = useState(null);
    const [cardsToPlay, setCardsToPlay] = useState([])
    const [numberOfCardsFaceDown, setNumberOfCardsFaceDown] = useState(0)
    
    const handlePlayCard = async (e) => {
        e.preventDefault();

        if (!selectedPlayerId) {
        alert("Please select a player");
        return;
        }

        const response = await fetch(`${API_URL}/api/games/${props.game.id}/players/${selectedPlayerId}/hand/play`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json"
        },
        body: JSON.stringify({ card_face_up: cardFaceUpId, number_of_cards_face_down: numberOfCardsFaceDown}),
        credentials: "include",
        });
        const data = await response.json();
        if (!response.ok) {
        alert(data.detail);
        return
        }
        setSelectedPlayerId(null);
        setCardFaceUpId(null);
        window.location.reload();

    };

    useEffect(() => {
        if (!selectedPlayerId) return;
        fetch(`${API_URL}/api/games/${props.game.id}/players/${selectedPlayerId}/hand/play/cards`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} })
            .then((res) => res.json())
            .then((data) => setCardsToPlay(data));
      }, [selectedPlayerId]);

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
                    <label>Card to play:</label>
                    <select
                        value={cardFaceUpId || ""}  // empty string = no selection
                        onChange={(e) => {
                        setCardFaceUpId(e.target.value || null);
                        }}
                    >
                        <option value="">-- Choose card --</option>  {/* optional "no selection" */}
                        {cardsToPlay.map((card) => (
                        <option key={card.id} value={card.id}>
                            {card.suit} {card.number}
                        </option>
                        ))}
                    </select>
                </div>

                <div className="formRow">
                <label>Number of cards to play face down:</label>
                <select
                    value={numberOfCardsFaceDown}
                    onChange={(e) => setNumberOfCardsFaceDown(Number(e.target.value))}
                >
                    <option value={0}>0</option>
                    <option value={1}>1</option>
                    <option value={2}>2</option>
                </select>
                </div>
            <button className="button" type="submit">Play Card</button>
        </form>
}