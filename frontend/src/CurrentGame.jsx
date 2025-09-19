import { useParams } from "react-router-dom";

export default function CurrentGame() {
    const { id } = useParams();
    return <h2>CURRENT GAME {id}</h2>
}