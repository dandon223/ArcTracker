import { Link } from "react-router-dom";

export default function Header(props) {
    return  <header> 
                <h3>ArcTracker</h3> 
                <nav>
                {props.user ? (
                    <button className="button" onClick={props.onLogout}>
                        Logout
                    </button>
                ) : (
                    <>
                    <Link className="button loginHeader" to="/login">Login</Link>
                    <Link className="button" to="/register">Register</Link>
                    </>
                )}
            </nav>
            </header>
}