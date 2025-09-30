import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
const API_URL = import.meta.env.VITE_API_URL;
import Card from "./Card";
import Player from "./Player";
import PlayOptions from "./PlayOptions";
import PlayCardForm from "./PlayCardForm";

export default function CurrentGame() {
    const [game, setGame] = useState({});
    const [cards, setCards] = useState([]);
    const [players, setPlayers] = useState([]);
    const [selected, setSelected] = useState(null);
    const { name } = useParams();
    const cardsNotPlayedElements = cards.filter(card => game.cards_not_played?.includes(card.id)).map(card => <Card key={card.id} number={card.number} suit={card.suit}/>)

    const setGameStateFromAPI = async () => {
        const resGame = await fetch(`${API_URL}/api/games/?name=${encodeURIComponent(name)}`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} });
        const gameData = await resGame.json();
        setGame(gameData)

        const resPlayers = await fetch(`${API_URL}/api/players/`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} });
        const playersData = await resPlayers.json();
        setPlayers(playersData.filter(player => gameData.players.includes(player.id)));
    }
    const setCardsFromAPI = async () => {
        fetch(`${API_URL}/api/cards/`, { 
            credentials: "include",
            headers:{"Accept": "application/json"} })
            .then((res) => res.json())
            .then((data) => setCards(data));
    }
    useEffect(() => {
        setGameStateFromAPI();
        setCardsFromAPI()
      }, []);

    const reloadAfterPlayCard = async () => {
        setGameStateFromAPI()
        setSelected(null)
    };

    return (
        <section className="current-game">
            <h2>CURRENT GAME: {name}</h2>
            <h3>Cards not played:</h3>
            <div className="cards-container">
            {cardsNotPlayedElements}
            </div>
            <h3>Choose Action:</h3>
            <PlayOptions selected={selected} setSelected={setSelected}/>
            {selected == "Play" && <PlayCardForm game={game} players={players} reloadAfterPlayCard={reloadAfterPlayCard}/>}
        </section>
    );
}