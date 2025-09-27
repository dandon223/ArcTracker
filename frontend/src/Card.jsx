export default function Card(props) {
    const imgSrc = `/static/action_cards/${props.suit}/${props.number}.jpg`;
    return <div className="card"><img src={imgSrc} alt={`${props.suit} ${props.number}`} /></div>
}