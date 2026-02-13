import { useCallback, useRef } from 'react';

/**
 * Canvas History Hook
 * Manages undo/redo functionality for canvas operations
 *
 * Features:
 * - History stack with configurable limit
 * - Redo stack
 * - Action grouping
 * - History persistence (optional)
 *
 * @param {Function} onRestore - Callback when history is restored
 * @param {number} maxHistory - Maximum history entries (default: 50)
 * @returns {Object} History management functions and state
 *
 * @version 1.0.0
 * @date 2026-01-29
 */
export function useCanvasHistory(onRestore, maxHistory = 50) {
  const pastRef = useRef([]);
  const futureRef = useRef([]);

  /**
   * Push current state to history
   * @param {Object} state - Current canvas state {nodes, edges}
   */
  const pushHistory = useCallback((state) => {
    if (!state || !state.nodes || !state.edges) return;

    const historyEntry = {
      nodes: JSON.parse(JSON.stringify(state.nodes)),
      edges: JSON.parse(JSON.stringify(state.edges)),
      timestamp: Date.now()
    };

    pastRef.current.push(historyEntry);

    // Limit history size
    if (pastRef.current.length > maxHistory) {
      pastRef.current.shift();
    }

    // Clear future when new action is performed
    futureRef.current = [];

    console.log('[useCanvasHistory] History pushed. Total entries:', pastRef.current.length);
  }, [maxHistory]);

  /**
   * Undo last action
   * @returns {Object|null} Previous state or null if no history
   */
  const undo = useCallback(() => {
    if (pastRef.current.length === 0) {
      console.log('[useCanvasHistory] No history to undo');
      return null;
    }

    const current = pastRef.current.pop();

    // Get previous state
    const previous = pastRef.current.length > 0
      ? pastRef.current[pastRef.current.length - 1]
      : { nodes: [], edges: [] }; // Initial state

    // Save current to future for redo
    futureRef.current.push(current);

    console.log('[useCanvasHistory] Undo performed. Remaining:', pastRef.current.length);

    return {
      nodes: JSON.parse(JSON.stringify(previous.nodes)),
      edges: JSON.parse(JSON.stringify(previous.edges))
    };
  }, []);

  /**
   * Redo last undone action
   * @returns {Object|null} Next state or null if no future
   */
  const redo = useCallback(() => {
    if (futureRef.current.length === 0) {
      console.log('[useCanvasHistory] No future to redo');
      return null;
    }

    const next = futureRef.current.pop();
    pastRef.current.push(next);

    console.log('[useCanvasHistory] Redo performed. Future remaining:', futureRef.current.length);

    return {
      nodes: JSON.parse(JSON.stringify(next.nodes)),
      edges: JSON.parse(JSON.stringify(next.edges))
    };
  }, []);

  /**
   * Check if undo is available
   * @returns {boolean}
   */
  const canUndo = useCallback(() => {
    return pastRef.current.length > 0;
  }, []);

  /**
   * Check if redo is available
   * @returns {boolean}
   */
  const canRedo = useCallback(() => {
    return futureRef.current.length > 0;
  }, []);

  /**
   * Clear all history
   */
  const clearHistory = useCallback(() => {
    pastRef.current = [];
    futureRef.current = [];
    console.log('[useCanvasHistory] History cleared');
  }, []);

  /**
   * Get history statistics
   * @returns {Object} History stats
   */
  const getHistoryStats = useCallback(() => {
    return {
      past: pastRef.current.length,
      future: futureRef.current.length,
      total: pastRef.current.length + futureRef.current.length,
      canUndo: canUndo(),
      canRedo: canRedo()
    };
  }, [canUndo, canRedo]);

  return {
    pushHistory,
    undo,
    redo,
    canUndo,
    canRedo,
    clearHistory,
    getHistoryStats
  };
}
