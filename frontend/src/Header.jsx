import { Link, useNavigate } from "react-router-dom";
import { getCookie } from "./csrf";

const API_URL = import.meta.env.VITE_API_URL;

export default function Header(props) {
  const navigate = useNavigate();
  const handleLogout = async () => {
    await fetch(`${API_URL}/api/logout/`, {
      method: "POST",
      credentials: "include",
      headers:{
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        "Accept": "application/json"}
    });
    props.setUser(null);
    navigate("/");
  };
    return  <header> 
                <h3>ArcTracker</h3> 
                <nav>
                {props.user ? (
                    <>
                    <button className="button" onClick={handleLogout}>
                        Logout
                    </button>
                    </>
                ) : (
                    <>
                    <Link className="button loginHeader" to="/login">Login</Link>
                    <Link className="button" to="/register">Register</Link>
                    </>
                )}
            </nav>
            </header>
}