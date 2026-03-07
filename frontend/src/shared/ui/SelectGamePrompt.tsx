// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

import React from 'react';
import './SelectGamePrompt.css';

/**
 * Props for SelectGamePrompt component
 */
export interface SelectGamePromptProps {
  /** Custom message to display */
  message?: string;
}

/**
 * SelectGamePrompt Component
 *
 * Displays a prompt when no game is selected
 *
 * @example
 * <SelectGamePrompt message="请选择游戏以继续" />
 */
export function SelectGamePrompt({ message }: SelectGamePromptProps): React.JSX.Element {
  const handleSelectGame = (): void => {
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

// Memoize SelectGamePrompt - only re-render when message changes
const MemoizedSelectGamePrompt = React.memo(SelectGamePrompt, (prevProps, nextProps) => {
  return prevProps.message === nextProps.message;
});

MemoizedSelectGamePrompt.displayName = 'MemoizedSelectGamePrompt';

export default MemoizedSelectGamePrompt;
