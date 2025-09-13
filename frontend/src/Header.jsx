export default function Header(props) {
    return  <header> 
                <h3>ArcTracker</h3> 
                <nav>
                {props.user ? (
                <div>
                    <span>Welcome, {props.user}!</span>
                    <button onClick={props.onLogout}>
                        Logout
                    </button>
                </div>
                ) : null}
            </nav>
            </header>
}