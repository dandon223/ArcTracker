import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
const API_URL = import.meta.env.VITE_API_URL;
import Card from "./Card";
import Player from "./Player";
import PlayOptions from "./PlayOptions";

export default function CurrentGame() {
    const [game, setGame] = useState({});
    const [cards, setCards] = useState([]);
    const [players, setPlayers] = useState([]);
    const cardsElements = cards.filter(card => game.cards_not_played?.includes(card.id)).map(card => <Card key={card.id} number={card.number} suit={card.suit}/>)
    const playerElements = players.filter(player => game.players?.includes(player.id)).map(player => <Player key={player.id} nick={player.nick}/>)
    const [selected, setSelected] = useState(null);

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

    useEffect(() => {
        fetch(`${API_URL}/api/players/`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} })
            .then((res) => res.json())
            .then((data) => setPlayers(data));
      }, []);

    const { name } = useParams();
    return (
        <section className="current-game">
            <h2>CURRENT GAME: {name}</h2>
            <h3>Cards in Play:</h3>
            <div className="cards-container">
            {cardsElements}
            </div>
            <h3>Choose Action:</h3>
            <PlayOptions selected={selected} setSelected={setSelected}/>
        </section>
    );
}