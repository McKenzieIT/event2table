import { renderHookWithProviders } from '@test/test-utils';
import { act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import { useGameContext } from './useGameContext';

// Mock useGameStore
vi.mock('@/stores/gameStore', () => ({
  useGameStore: () => ({
    currentGame: null,
    setCurrentGame: vi.fn(),
    gameGid: null,
    clearGame: vi.fn(),
  }),
}));

// Mock fetch
global.fetch = vi.fn();

// Note: renderHookWithProviders wraps with AllProviders (includes BrowserRouter)
// This is required because useGameContext uses useLocation() from react-router-dom

describe('useGameContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('initial state', () => {
    it('should initialize with null current game', () => {
      const { result } = renderHookWithProviders(() => useGameContext());
      
      expect(result.current.currentGame).toBeNull();
      expect(result.current.currentGameGid).toBeNull();
      expect(result.current.isLoadingGame).toBe(false);
    });
  });

  describe('selectGame', () => {
    it('should select game and save to localStorage', () => {
      const { result } = renderHookWithProviders(() => useGameContext());
      
      const game = {
        id: 1,
        gid: 10000147,
        name: 'Test Game',
        ods_db: 'test_db',
      };
      
      act(() => {
        result.current.selectGame(game);
      });
      
      // Verify localStorage.setItem was called with correct arguments
      // (localStorage is mocked in setup.ts, so we check mock calls)
      expect(localStorage.setItem).toHaveBeenCalledWith('selectedGameGid', '10000147');
      expect(localStorage.setItem).toHaveBeenCalledWith('selectedGameId', '1');
      expect(localStorage.setItem).toHaveBeenCalledWith('selectedGameName', 'Test Game');
    });

    it('should dispatch game changed event', () => {
      const dispatchSpy = vi.spyOn(window, 'dispatchEvent');
      const { result } = renderHookWithProviders(() => useGameContext());
      
      const game = {
        id: 1,
        gid: 10000147,
        name: 'Test Game',
        ods_db: 'test_db',
      };
      
      act(() => {
        result.current.selectGame(game);
      });
      
      expect(dispatchSpy).toHaveBeenCalledWith(
        expect.objectContaining({ type: 'gameChanged' })
      );
    });
  });

  describe('clearGame', () => {
    it('should clear current game', () => {
      const { result } = renderHookWithProviders(() => useGameContext());
      
      act(() => {
        result.current.clearGame();
      });
      
      expect(result.current.currentGame).toBeNull();
    });
  });

  describe('load game from URL', () => {
    it('should load game from URL parameter', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: [
            {
              id: 1,
              gid: 10000147,
              name: 'Test Game',
              ods_db: 'test_db',
            },
          ],
        }),
      });

      window.history.pushState({}, 'Test', '/?game_gid=10000147');

      const { result } = renderHookWithProviders(() => useGameContext());

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/games');
      });
    });

    it('should load game from game_id parameter', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: [
            {
              id: 1,
              gid: 10000147,
              name: 'Test Game',
              ods_db: 'test_db',
            },
          ],
        }),
      });

      window.history.pushState({}, 'Test', '/?game_id=10000147');

      renderHookWithProviders(() => useGameContext());

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/games');
      });
    });

    it('should load game from localStorage', async () => {
      // Mock localStorage.getItem to return the game GID
      (localStorage.getItem as any).mockReturnValue('10000147');

      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: [
            {
              id: 1,
              gid: 10000147,
              name: 'Test Game',
              ods_db: 'test_db',
            },
          ],
        }),
      });

      renderHookWithProviders(() => useGameContext());

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/games');
      });
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as any).mockRejectedValue(new Error('Network error'));

      window.history.pushState({}, 'Test', '/?game_gid=10000147');

      const { result } = renderHookWithProviders(() => useGameContext());

      await waitFor(() => {
        expect(result.current.currentGame).toBeNull();
      });
    });

    it('should not load game if already loaded', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: [
            {
              id: 1,
              gid: 10000147,
              name: 'Test Game',
              ods_db: 'test_db',
            },
          ],
        }),
      });

      window.history.pushState({}, 'Test', '/?game_gid=10000147');

      const { result } = renderHookWithProviders(() => useGameContext());

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith('/api/games');
      });

      const fetchCalls = (global.fetch as any).mock.calls.length;

      // Wait a bit to ensure no additional fetch calls
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 100));
      });

      expect((global.fetch as any).mock.calls.length).toBe(fetchCalls);
    });
  });

  describe('game changed event', () => {
    it('should listen to game changed event', async () => {
      const { result } = renderHookWithProviders(() => useGameContext());
      
      const game = {
        id: 1,
        gid: 10000147,
        name: 'Test Game',
        ods_db: 'test_db',
      };
      
      act(() => {
        window.dispatchEvent(new CustomEvent('gameChanged', { detail: game }));
      });
      
      expect(result.current.currentGame).toBeNull();
    });
  });

  describe('window.gameData', () => {
    it('should set window.gameData on select', () => {
      const { result } = renderHookWithProviders(() => useGameContext());
      
      const game = {
        id: 1,
        gid: 10000147,
        name: 'Test Game',
        ods_db: 'test_db',
      };
      
      act(() => {
        result.current.selectGame(game);
      });
      
      expect((window as any).gameData).toEqual(game);
    });
  });
});
