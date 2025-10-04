export default function Card(props) {
    let imgSrc;
    if (props.suit == null)
        imgSrc = `/static/action_cards/back.png`;
    else
        imgSrc = `/static/action_cards/${props.suit}/${props.number}.jpg`;
    return <div className="card"><img src={imgSrc} alt={`${props?.suit} ${props?.number}`} /></div>
}