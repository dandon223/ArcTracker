import Card
 from "./Card";
export default function CardsSection(props) {
    const cardsNotPlayedElements = props.cards.filter(card => props.game.cards_not_played?.includes(card.id)).map(card => <Card key={card.id} number={card.number} suit={card.suit}/>)

  return (
        <>
            <h3>Cards not played:</h3>
            <div className="cards-container">{cardsNotPlayedElements}</div>
        </>
  );
}