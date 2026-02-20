// @ts-nocheck - TypeScript检查暂禁用
import { useGameStore } from '@/stores/gameStore';
import { useCallback, useEffect, useRef, useTransition } from 'react';
import { useLocation } from 'react-router-dom';

interface Game {
  id: number;
  gid: number;
  name: string;
  ods_db: string;
  dwd_prefix?: string;
}

interface UseGameContextReturn {
  currentGame: Game | null;
  currentGameGid: number | null;
  selectGame: (game: Game) => void;
  clearGame: () => void;
  gameData: Game | null;
  isLoadingGame: boolean;
}

export function useGameContext(): UseGameContextReturn {
  const location = useLocation();
  const [isPending, startTransition] = useTransition();
  const isLoadingRef = useRef(false);
  const isMounted = useRef(true);

  const { 
    currentGame, 
    setCurrentGame, 
    gameGid,
    clearGame: clearStoreGame 
  } = useGameStore();

  const selectGame = useCallback((game: Game) => {
    setCurrentGame(game);
    localStorage.setItem('selectedGameGid', game.gid);
    localStorage.setItem('selectedGameId', game.id);
    localStorage.setItem('selectedGameName', game.name);
    window.gameData = game;
    window.dispatchEvent(new CustomEvent('gameChanged', { detail: game }));
  }, [setCurrentGame]);

  const clearGame = useCallback(() => {
    clearStoreGame();
  }, [clearStoreGame]);

  useEffect(() => {
    const loadGameFromUrl = async () => {
      const params = new URLSearchParams(location.search);
      const urlGameGid = params.get('game_gid') || params.get('game_id');
      const storedGameGid = localStorage.getItem('selectedGameGid');
      const targetGid = urlGameGid || storedGameGid;

      if (!targetGid || isLoadingRef.current) {
        return;
      }

      if (currentGame && String(currentGame.gid) === String(targetGid)) {
        return;
      }

      isLoadingRef.current = true;

      try {
        const response = await fetch('/api/games');
        const result = await response.json();
        
        if (result.success && Array.isArray(result.data)) {
          const game = result.data.find(g => 
            String(g.gid) === String(targetGid) || String(g.id) === String(targetGid)
          );
          
          if (game) {
            const gameData: Game = {
              id: game.id,
              gid: game.gid,
              name: game.name,
              ods_db: game.ods_db,
              dwd_prefix: game.dwd_prefix
            };

            localStorage.setItem('selectedGameGid', game.gid);
            window.gameData = gameData;

            if (isMounted.current) {
              startTransition(() => {
                setCurrentGame(gameData);
              });
            }
          }
        }
      } catch (error) {
        console.error('[useGameContext] Failed to load game:', error);
      } finally {
        isLoadingRef.current = false;
      }
    };

    loadGameFromUrl();

    return () => {
      isMounted.current = false;
    };
  }, [location.search, location.pathname, currentGame, setCurrentGame]);

  useEffect(() => {
    const handleGameChange = (e: CustomEvent) => {
      setCurrentGame(e.detail);
    };

    window.addEventListener('gameChanged', handleGameChange as EventListener);

    return () => {
      window.removeEventListener('gameChanged', handleGameChange as EventListener);
    };
  }, [setCurrentGame]);

  return {
    currentGame,
    currentGameGid: gameGid,
    selectGame,
    clearGame,
    gameData: currentGame,
    isLoadingGame: isPending,
  };
}
