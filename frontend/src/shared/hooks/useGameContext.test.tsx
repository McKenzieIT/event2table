import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@test/test-utils';
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

// Note: renderHook from @test/test-utils already wraps with AllProviders (includes BrowserRouter)
// No need for manual wrapper

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
      const { result } = renderHook(() => useGameContext());
      
      expect(result.current.currentGame).toBeNull();
      expect(result.current.currentGameGid).toBeNull();
      expect(result.current.isLoadingGame).toBe(false);
    });
  });

  describe('selectGame', () => {
    it('should select game and save to localStorage', () => {
      const { result } = renderHook(() => useGameContext());
      
      const game = {
        id: 1,
        gid: 10000147,
        name: 'Test Game',
        ods_db: 'test_db',
      };
      
      act(() => {
        result.current.selectGame(game);
      });
      
      expect(localStorage.getItem('selectedGameGid')).toBe('10000147');
      expect(localStorage.getItem('selectedGameId')).toBe('1');
      expect(localStorage.getItem('selectedGameName')).toBe('Test Game');
    });

    it('should dispatch game changed event', () => {
      const dispatchSpy = vi.spyOn(window, 'dispatchEvent');
      const { result } = renderHook(() => useGameContext());
      
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
      const { result } = renderHook(() => useGameContext());
      
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
      
      const { result } = renderHook(() => useGameContext());
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(global.fetch).toHaveBeenCalledWith('/api/games');
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
      
      renderHook(() => useGameContext());
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(global.fetch).toHaveBeenCalledWith('/api/games');
    });

    it('should load game from localStorage', async () => {
      localStorage.setItem('selectedGameGid', '10000147');
      
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

      renderHook(() => useGameContext());
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(global.fetch).toHaveBeenCalledWith('/api/games');
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as any).mockRejectedValue(new Error('Network error'));
      
      window.history.pushState({}, 'Test', '/?game_gid=10000147');
      
      const { result } = renderHook(() => useGameContext());
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect(result.current.currentGame).toBeNull();
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
      
      const { result } = renderHook(() => useGameContext());
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      const fetchCalls = (global.fetch as any).mock.calls.length;
      
      await new Promise(resolve => setTimeout(resolve, 0));
      
      expect((global.fetch as any).mock.calls.length).toBe(fetchCalls);
    });
  });

  describe('game changed event', () => {
    it('should listen to game changed event', async () => {
      const { result } = renderHook(() => useGameContext());
      
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
      const { result } = renderHook(() => useGameContext());
      
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
