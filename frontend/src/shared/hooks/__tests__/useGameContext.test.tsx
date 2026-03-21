// @ts-nocheck - TypeScript strict mode disabled for test files
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { useGameContext } from '../useGameContext';

// Mock zustand store
const mockSetCurrentGame = vi.fn();
const mockClearGame = vi.fn();

vi.mock('@/stores/gameStore', () => ({
  useGameStore: vi.fn(() => ({
    currentGame: null,
    gameGid: null,
    setCurrentGame: mockSetCurrentGame,
    clearGame: mockClearGame
  }))
}));

// Wrapper component to provide Router context
const wrapper = ({ children }: { children: React.ReactNode }) => {
  return <MemoryRouter>{children}</MemoryRouter>;
};

describe('useGameContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    delete (window as unknown as { gameData?: unknown }).gameData;
  });

  it('should update store when selectGame is called', () => {
    const { result } = renderHook(() => useGameContext(), { wrapper });
    const testGame = { id: 1, gid: 10000147, name: 'Test', ods_db: 'ieu_ods' };

    act(() => {
      result.current.selectGame(testGame);
    });

    expect(mockSetCurrentGame).toHaveBeenCalledWith(testGame);
  });

  it('should NOT update window.gameData when selectGame is called', () => {
    const { result } = renderHook(() => useGameContext(), { wrapper });
    const testGame = { id: 1, gid: 10000147, name: 'Test', ods_db: 'ieu_ods' };

    act(() => {
      result.current.selectGame(testGame);
    });

    // window.gameData不再被设置
    expect(window.gameData).toBeUndefined();
  });

  it('should clear all game state when clearGame is called', () => {
    const { result } = renderHook(() => useGameContext(), { wrapper });

    act(() => {
      result.current.clearGame();
    });

    expect(mockClearGame).toHaveBeenCalled();
  });

  it('should NOT update window.gameData when clearGame is called', () => {
    const { result } = renderHook(() => useGameContext(), { wrapper });

    act(() => {
      result.current.clearGame();
    });

    // window.gameData不再被设置
    expect(window.gameData).toBeUndefined();
  });

  it('should return currentGame and gameGid from store', () => {
    const { result } = renderHook(() => useGameContext(), { wrapper });
    
    expect(result.current.currentGame).toBeNull();
    expect(result.current.currentGameGid).toBeNull();
  });

  it('should return gameData as alias for currentGame', () => {
    const { result } = renderHook(() => useGameContext(), { wrapper });
    
    expect(result.current.gameData).toBeNull();
  });
});
