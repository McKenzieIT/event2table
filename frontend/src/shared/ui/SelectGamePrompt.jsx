import './SelectGamePrompt.css';

/**
 * SelectGamePrompt Component
 *
 * Displays a prompt when no game is selected
 *
 * Props:
 * - message: string - Custom message to display (optional)
 */
export function SelectGamePrompt({ message }) {
  const handleSelectGame = () => {
    window.dispatchEvent(new CustomEvent('toggleGameSheet'));
  };

  return (
    <div className="select-game-prompt">
      <div className="prompt-container">
        <h2 className="prompt-title">请先选择游戏</h2>
        <p className="prompt-message">
          {message || '选择游戏后才能查看相关数据'}
        </p>
        <button className="btn btn-primary" onClick={handleSelectGame}>
          选择游戏
        </button>
      </div>
    </div>
  );
}
