import { Outlet, useLocation } from 'react-router-dom';
import { useState, useEffect, Suspense, useMemo, useCallback } from 'react';
import { Sidebar } from '@analytics/components/sidebar/Sidebar';
import { GameSelectionSheet } from '@analytics/components/game-selection/GameSelectionSheet';
import GameManagementModal from '../../../features/games/GameManagementModal';
import AddGameModal from '../../../features/games/AddGameModal';
import { useGameStore } from '../../../stores/gameStore';
import { useGameContext } from '@/shared/hooks/useGameContext';
import Loading from '@shared/ui/Loading';
import './MainLayout.css';

export default function MainLayout() {
  const location = useLocation();

  const {
    isGameManagementModalOpen,
    closeGameManagementModal,
    isAddGameModalOpen,
    closeAddGameModal
  } = useGameStore();

  const { currentGame, selectGame } = useGameContext();
  const [isGameSheetOpen, setIsGameSheetOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    const handleToggle = () => setIsGameSheetOpen(prev => !prev);

    window.addEventListener('toggleGameSheet', handleToggle);

    return () => {
      window.removeEventListener('toggleGameSheet', handleToggle);
    };
  }, []);

  useEffect(() => {
    try {
      const savedCollapsed = localStorage.getItem('sidebarCollapsed');
      if (savedCollapsed !== null) {
        setSidebarCollapsed(JSON.parse(savedCollapsed));
      }
    } catch (error) {
      console.error('[MainLayout] Failed to load sidebar state:', error);
    }

    const handleSidebarToggle = (e) => {
      setSidebarCollapsed(e.detail);
    };

    window.addEventListener('sidebarToggled', handleSidebarToggle);

    return () => {
      window.removeEventListener('sidebarToggled', handleSidebarToggle);
    };
  }, []);

  useEffect(() => {
    const sidebarWidth = sidebarCollapsed ? '60px' : '260px';
    document.documentElement.style.setProperty('--sidebar-current-width', sidebarWidth);
  }, [sidebarCollapsed]);

  const handleSelectGame = useCallback((game) => {
    selectGame({
      id: game.id,
      gid: game.gid,
      name: game.name,
      ods_db: game.ods_db
    });
  }, [selectGame]);

  const stableSetCurrentGame = useCallback((gameData) => {
    selectGame(gameData);
  }, [selectGame]);

  const contextValue = useMemo(() => ({ 
    currentGame, 
    setCurrentGame: stableSetCurrentGame 
  }), [currentGame, stableSetCurrentGame]);

  const outletKey = useMemo(() => location.pathname, [location.pathname]);

  return (
    <div className="app-shell" data-testid="main-layout">
      <div className="app-body">
        <Sidebar currentGame={currentGame} />
        <main className="app-content" data-testid="main-content">
          <Suspense fallback={<Loading />}>
            <Outlet key={outletKey} context={contextValue} />
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
