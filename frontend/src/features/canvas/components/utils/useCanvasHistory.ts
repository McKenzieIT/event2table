import { useCallback, useRef } from 'react';
import { Node, Edge } from 'reactflow';

export interface CanvasState {
  nodes: Node[];
  edges: Edge[];
}

export interface HistoryEntry {
  nodes: Node[];
  edges: Edge[];
  timestamp: number;
}

export interface HistoryStats {
  past: number;
  future: number;
  total: number;
  canUndo: boolean;
  canRedo: boolean;
}

export interface UseCanvasHistoryReturn {
  pushHistory: (state: CanvasState) => void;
  undo: () => CanvasState | null;
  redo: () => CanvasState | null;
  canUndo: () => boolean;
  canRedo: () => boolean;
  clearHistory: () => void;
  getHistoryStats: () => HistoryStats;
}

export function useCanvasHistory(
  onRestore?: (state: CanvasState) => void,
  maxHistory: number = 50
): UseCanvasHistoryReturn {
  const pastRef = useRef<HistoryEntry[]>([]);
  const futureRef = useRef<HistoryEntry[]>([]);

  const pushHistory = useCallback((state: CanvasState) => {
    if (!state || !state.nodes || !state.edges) return;

    const historyEntry: HistoryEntry = {
      nodes: JSON.parse(JSON.stringify(state.nodes)),
      edges: JSON.parse(JSON.stringify(state.edges)),
      timestamp: Date.now()
    };

    pastRef.current.push(historyEntry);

    if (pastRef.current.length > maxHistory) {
      pastRef.current.shift();
    }

    futureRef.current = [];
  }, [maxHistory]);

  const undo = useCallback((): CanvasState | null => {
    if (pastRef.current.length === 0) {
      return null;
    }

    const current = pastRef.current.pop();

    const previous = pastRef.current.length > 0
      ? pastRef.current[pastRef.current.length - 1]
      : { nodes: [], edges: [] };

    if (current) {
      futureRef.current.push(current);
    }

    const result = {
      nodes: JSON.parse(JSON.stringify(previous.nodes)),
      edges: JSON.parse(JSON.stringify(previous.edges))
    };

    if (onRestore) {
      onRestore(result);
    }

    return result;
  }, [onRestore]);

  const redo = useCallback((): CanvasState | null => {
    if (futureRef.current.length === 0) {
      return null;
    }

    const next = futureRef.current.pop();

    if (next) {
      pastRef.current.push(next);
    }

    const result = {
      nodes: JSON.parse(JSON.stringify(next.nodes)),
      edges: JSON.parse(JSON.stringify(next.edges))
    };

    if (onRestore) {
      onRestore(result);
    }

    return result;
  }, [onRestore]);

  const canUndo = useCallback((): boolean => {
    return pastRef.current.length > 0;
  }, []);

  const canRedo = useCallback((): boolean => {
    return futureRef.current.length > 0;
  }, []);

  const clearHistory = useCallback(() => {
    pastRef.current = [];
    futureRef.current = [];
  }, []);

  const getHistoryStats = useCallback((): HistoryStats => {
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
