import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
const API_URL = import.meta.env.VITE_API_URL;
import { getCookie } from "./csrf";
import PlayOptions from "./PlayOptions";
import PlayCardForm from "./PlayCardForm";
import CardsSection from "./CardsSection";

export default function CurrentGame() {
    const [game, setGame] = useState({});
    const [cards, setCards] = useState([]);
    const [players, setPlayers] = useState([]);
    const [selected, setSelected] = useState(null);
    const { name } = useParams();
    const playerIdToNick = Object.fromEntries(
        players.map(player => [player.id, player.nick])
    );
    const cardIdToCard = Object.fromEntries(
        cards.map(card => [card.id, card])
    );
    
    
    const setGameStateFromAPI = async (includePlayers = false) => {
        try {
            const resGame = await fetch(`${API_URL}/api/games/?name=${encodeURIComponent(name)}`, { 
                credentials: "include",
                headers: { "Accept": "application/json" }
            });
            const gameData = await resGame.json();
            setGame(gameData);

            if (includePlayers) {
            const resPlayers = await fetch(`${API_URL}/api/players/`, { 
                credentials: "include",
                headers: { "Accept": "application/json" }
            });
            const playersData = await resPlayers.json();
            setPlayers(playersData.filter(player => gameData.players.includes(player.id)));
            }
        } catch (err) {
            console.error("Failed to fetch game/players:", err);
        }
    };

    const setCardsFromAPI = async () => {
        try {
            const res = await fetch(`${API_URL}/api/cards/`, { 
                credentials: "include",
                headers: { "Accept": "application/json" }
            });
            const cardsData = await res.json();
            setCards(cardsData);
        } catch (err) {
            console.error("Failed to fetch cards:", err);
        }
    };

    const setNewRoundFromAPI = async () => {
        try {
            const response = await fetch(`${API_URL}/api/games/${game.id}/rounds/create`, { 
                credentials: "include",
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Accept": "application/json"
                },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (!response.ok) {
                alert(data.detail);
                return
            }
            
        } catch (err) {
            console.error("Failed to post new round:", err);
        }
    };

    const setNewChapterFromAPI = async () => {
        try {
            const response = await fetch(`${API_URL}/api/games/${game.id}/chapters/create`, { 
                credentials: "include",
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Accept": "application/json"
                },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (!response.ok) {
                alert(data.detail);
                return
            }
            
        } catch (err) {
            console.error("Failed to post new chapter:", err);
        }
    };

    useEffect(() => {
        setGameStateFromAPI(true); // game + players
        setCardsFromAPI();
    }, []);

    useEffect(() => {
        if (selected === "New Round") {
            const run = async () => {
                await setNewRoundFromAPI();
                setSelected(null);
            };
            run();
        }
        if (selected === "New Chapter") {
            const run = async () => {
                await setNewChapterFromAPI();
                await setGameStateFromAPI();
                setSelected(null);
            };
            run();
        }


    }, [selected]);

    const reloadAfterPlayCard = async () => {
        await setGameStateFromAPI(); // just game
        setSelected(null);
    };

    return (
        <section className="current-game">
            <h2>CURRENT GAME: {name}</h2>
            <CardsSection game={game} cards={cards} playerIdToNick={playerIdToNick} cardIdToCard={cardIdToCard}/>
            <h3>Choose Action:</h3>
            <PlayOptions selected={selected} setSelected={setSelected}/>
            {selected == "Play" && <PlayCardForm game={game} players={players} reloadAfterPlayCard={reloadAfterPlayCard}/>}
        </section>
    );
}