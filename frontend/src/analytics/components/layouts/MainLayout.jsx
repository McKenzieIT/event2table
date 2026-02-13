import { Outlet, useLocation } from 'react-router-dom';
import { useState, useEffect, useTransition, useRef, Suspense, useMemo, useCallback } from 'react';
import { Sidebar } from '@analytics/components/sidebar/Sidebar';
import { GameSelectionSheet } from '@analytics/components/game-selection/GameSelectionSheet';
import GameManagementModal from '../../../features/games/GameManagementModal';
import AddGameModal from '../../../features/games/AddGameModal';
import { useGameStore } from '../../../stores/gameStore';
import Loading from '@shared/ui/Loading';
import './MainLayout.css';

export default function MainLayout() {
  console.log('[MainLayout] RENDER START - Component mounting/updating');

  const location = useLocation();
  const [isPending, startTransition] = useTransition();

  console.log('[MainLayout] useLocation and useTransition hooks called');

  const {
    isGameManagementModalOpen,
    closeGameManagementModal,
    isAddGameModalOpen,
    closeAddGameModal
  } = useGameStore();

  const [currentGame, setCurrentGame] = useState(null);
  const [isGameSheetOpen, setIsGameSheetOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isLoadingGame, setIsLoadingGame] = useState(false);

  // Use ref to track component mount status and loading state
  const isMounted = useRef(true);
  const isLoadingRef = useRef(false);

  useEffect(() => {
    // Load game context from URL or localStorage
    const loadGameContext = async () => {
      // HashRouter provides query params in location.search
      const params = new URLSearchParams(location.search);
      const gameGid = params.get('game_gid') || params.get('game_id') || localStorage.getItem('selectedGameGid');

      console.log('[MainLayout] Loading game context:', { search: location.search, pathname: location.pathname, gameGid, isLoading: isLoadingRef.current });

      // Guard clause: prevent redundant calls
      if (!gameGid || isLoadingRef.current) {
        console.log('[MainLayout] Skipping load:', { gameGid, isLoading: isLoadingRef.current });
        return;
      }

      // Convert current game GID to string for comparison
      const currentGidStr = currentGame?.gid?.toString();
      if (currentGidStr && currentGidStr === String(gameGid)) {
        return;  // Already the current game, no need to reload
      }

      // Update loading state
      isLoadingRef.current = true;
      setIsLoadingGame(true);

      try {
        const response = await fetch('/api/games');
        const result = await response.json();
        // Only log in development or when there's an actual error
        if (process.env.NODE_ENV === 'development' && !result.success) {
          console.log('[MainLayout] API result:', result);
        }
        if (result.success && Array.isArray(result.data)) {
          const game = result.data.find(g => String(g.gid) === String(gameGid) || String(g.id) === String(gameGid));
          if (game) {
            const gameData = {
              id: game.id,
              gid: game.gid,
              name: game.name,
              ods_db: game.ods_db
            };
            // Update localStorage and window.gameData immediately (sync operations)
            localStorage.setItem('selectedGameGid', game.gid);
            window.gameData = gameData;

            // Use startTransition only for React state update
            // This prevents it from blocking React Router's route transition
            if (isMounted.current) {
              startTransition(() => {
                setCurrentGame(gameData);
              });
            }
          }
        }
      } catch (error) {
        console.error('[MainLayout] Failed to load game context:', error);
      } finally {
        // Only update state if component is still mounted
        isLoadingRef.current = false;
        if (isMounted.current) {
          setIsLoadingGame(false);
        }
      }
    };

    loadGameContext();

    // Cleanup function: Mark component as unmounted
    return () => {
      isMounted.current = false;
    };
  }, [location.search, location.pathname]);  // Depend on search and path only (removed currentGame?.gid to prevent infinite loop)

  // Listen for game selection events
  useEffect(() => {
    const handleToggle = () => setIsGameSheetOpen(prev => !prev);
    const handleGameChange = (e) => setCurrentGame(e.detail);

    window.addEventListener('toggleGameSheet', handleToggle);
    window.addEventListener('gameChanged', handleGameChange);

    return () => {
      window.removeEventListener('toggleGameSheet', handleToggle);
      window.removeEventListener('gameChanged', handleGameChange);
    };
  }, []);

  // Listen for sidebar state changes and update CSS variable
  useEffect(() => {
    // Load initial state from localStorage
    try {
      const savedCollapsed = localStorage.getItem('sidebarCollapsed');
      if (savedCollapsed !== null) {
        setSidebarCollapsed(JSON.parse(savedCollapsed));
      }
    } catch (error) {
      console.error('[MainLayout] Failed to load sidebar state:', error);
    }

    // Listen for sidebar toggle events
    const handleSidebarToggle = (e) => {
      setSidebarCollapsed(e.detail);
    };

    window.addEventListener('sidebarToggled', handleSidebarToggle);

    return () => {
      window.removeEventListener('sidebarToggled', handleSidebarToggle);
    };
  }, []);

  // Update CSS variable when sidebar state changes
  useEffect(() => {
    const sidebarWidth = sidebarCollapsed ? '60px' : '260px';
    document.documentElement.style.setProperty('--sidebar-current-width', sidebarWidth);
  }, [sidebarCollapsed]);

  const handleSelectGame = (game) => {
    const gameData = {
      id: game.id,
      gid: game.gid,
      name: game.name,
      ods_db: game.ods_db
    };
    setCurrentGame(gameData);
    localStorage.setItem('selectedGameGid', game.gid);
    localStorage.setItem('selectedGameId', game.id);
    localStorage.setItem('selectedGameName', game.name);

    // Set window.gameData for backward compatibility and tests
    window.gameData = gameData;

    // Dispatch event for other components
    window.dispatchEvent(new CustomEvent('gameChanged', { detail: gameData }));
  };

  // Stable setCurrentGame reference using useCallback
  const stableSetCurrentGame = useCallback((gameData) => {
    setCurrentGame(gameData);
  }, []);

  // Memoize context value to prevent unnecessary re-renders
  const contextValue = useMemo(() => ({ currentGame, setCurrentGame: stableSetCurrentGame }), [currentGame, stableSetCurrentGame]);

  return (
    <div className="app-shell" data-testid="main-layout">
      <div className="app-body">
        <Sidebar currentGame={currentGame} />
        <main className="app-content" data-testid="main-content">
          <Suspense fallback={<Loading />}>
            <Outlet key={currentGame?.gid || 'no-game'} context={contextValue} />
          </Suspense>
        </main>
      </div>

      <GameSelectionSheet
        isOpen={isGameSheetOpen}
        onClose={() => setIsGameSheetOpen(false)}
        onSelect={handleSelectGame}
      />

      <GameManagementModal
        isOpen={isGameManagementModalOpen}
        onClose={closeGameManagementModal}
      />

      <AddGameModal
        isOpen={isAddGameModalOpen}
        onClose={closeAddGameModal}
      />
    </div>
  );
}
