import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
const API_URL = import.meta.env.VITE_API_URL;
import Card from "./Card";

export default function CurrentGame() {
    const [game, setGame] = useState({});
    const [cards, setCards] = useState([]);
    const cardsElements = cards.filter(card => game.cards_not_played?.includes(card.id)).map(card => <Card key={card.id} number={card.number} suit={card.suit}/>)

    useEffect(() => {
        fetch(`${API_URL}/api/games/?name=${encodeURIComponent(name)}`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} })
            .then((res) => res.json())
            .then((data) => setGame(data));
      }, []);

    useEffect(() => {
        fetch(`${API_URL}/api/cards/`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} })
            .then((res) => res.json())
            .then((data) => setCards(data));
      }, []);

    const { name } = useParams();
    return (
        <section className="current-game">
            <h2>CURRENT GAME: {name}</h2>
            <div className="cards-container">
            {cardsElements}
            </div>
        </section>
    );
}