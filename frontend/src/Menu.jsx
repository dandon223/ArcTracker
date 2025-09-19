import { Link } from "react-router-dom";

export default function Menu() {
    return  <section>
        <Link className="button" to="/players">Players</Link>
        <Link className="button" to="/games">Games</Link>
    </section>
}