import { useState, useEffect } from "react";
const API_URL = import.meta.env.VITE_API_URL;
import Card from "./Card";

export default function CardsSection(props) {
    const [playerHands, setPlayerHands] = useState([]);
    const [cardsPlayedByPlayers, setCardsPlayedByPlayers] = useState([]);
    const cardsNotPlayedElements = props.cards.filter(card => props.game?.cards_not_played.includes(card.id)).map(card => <Card key={card.id} number={card.number} suit={card.suit}/>)
    const cardsInHandsElements = playerHands.map(playerHand => (
        <div key={playerHand.player}>
            <h3>{props.playerIdToNick[playerHand.player]}</h3>
            <div className="cards-container">
                {[...Array(playerHand.number_of_cards)].map((_, i) => (
                    <Card key={i} />
                ))}
                {playerHand.cards.map((card, i) => (
                    <Card key={i} number={props.cardIdToCard[card.id].number} suit={props.cardIdToCard[card.id].suit}  />
                ))}
            </div>
        </div>
    ))
    const cardsPlayedByPlayersElements = cardsPlayedByPlayers.map(cardsPlayedByPlayer => (
        <div key={cardsPlayedByPlayer.player}>
            <h3>{props.playerIdToNick[cardsPlayedByPlayer.player]}</h3>
            <div className="cards-container">
                {cardsPlayedByPlayer.cards.map((roundCards, i) => (
                    <div key={i} className="round">
                        <h4>Round {i + 1}</h4>
                        <div className="round-cards">
                            {roundCards.map((card, j) => {
                                if (Object.keys(card).length === 0)
                                    return <Card key={j} />
                                else
                                    return <Card key={card.id} number={props.cardIdToCard[card.id].number} suit={props.cardIdToCard[card.id].suit}  />
                            }
                        )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    ))

    const getPlayerHandFromAPI = async (player_id) => {
        try {
            const res = await fetch(`${API_URL}/api/games/${props.game.id}/players/${player_id}/hand`, { 
                credentials: "include",
                headers: { "Accept": "application/json" }
            });
            const playerHandsData = await res.json();
            return playerHandsData
        } catch (err) {
            console.error("Failed to fetch cards:", err);
        }
    };

    const getCardsPlayedByPlayersFromAPI = async () => {
        if (!props.game?.players) return;
        try {
            const res = await fetch(`${API_URL}/api/games/${props.game.id}/cards_history`, { 
                credentials: "include",
                headers: { "Accept": "application/json" }
            });
            const cardsPlayedByPlayersData = await res.json();
            setCardsPlayedByPlayers(cardsPlayedByPlayersData)
            
        } catch (err) {
            console.error("Failed to fetch cards played:", err);
        }
    };

    useEffect(() => {
        const setPlayerHandsFromAPI = async () => {
            if (!props.game?.players) return;
            const allHands = await Promise.all(
            props.game.players.map(getPlayerHandFromAPI)
            );
            setPlayerHands(allHands);
        };
        setPlayerHands([]); // clear old hands
        setPlayerHandsFromAPI();
        getCardsPlayedByPlayersFromAPI();
    }, [props.game]);
  return (
        <>
            <h3>Cards not played:</h3>
            <div className="cards-container">{cardsNotPlayedElements}</div>
            <h3>Players hand:</h3>
            {cardsInHandsElements}
            <h3>Cards Played:</h3>
            {cardsPlayedByPlayersElements}
        </>
  );
}