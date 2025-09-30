export default function PlayOptions(props) {

  const options = ["Play", "Add", "Retrieve", "Reveal", "Unreveal"];

  return (
    <div className="play-options">
      {options.map((option, index) => (
        <button
          key={index}
          type="button"
          className={`button ${props.selected === option ? "chosen" : ""}`}
          onClick={() => props.setSelected(option)}
        >
          {option}
        </button>
      ))}
    </div>
  );
}