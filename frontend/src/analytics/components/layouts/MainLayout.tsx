import { Outlet, useLocation, NavigateFunction, useNavigate } from 'react-router-dom';
import { useState, useEffect, Suspense, useMemo, useCallback } from 'react';
import { Sidebar } from '@analytics/components/sidebar/Sidebar';
import { GameSelectionSheet } from '@analytics/components/game-selection/GameSelectionSheet';
import GameManagementModal from '../../../features/games/GameManagementModal';
import AddGameModal from '../../../features/games/AddGameModal';
import { useGameStore } from '../../../stores/gameStore';
import { useGameContext } from '@/shared/hooks/useGameContext';
import Loading from '@shared/ui/Loading';
import Breadcrumb from '@shared/ui/Breadcrumb/Breadcrumb';
import { generateBreadcrumbs } from '@shared/config/breadcrumbConfig';
import './MainLayout.css';

interface GameData {
  id: number;
  gid: number;
  name: string;
  ods_db?: string;
}

interface OutletContextType {
  currentGame?: GameData | null;
  setCurrentGame: (game: GameData) => void;
}

export default function MainLayout(): React.JSX.Element {
  const location = useLocation();
  const navigate: NavigateFunction = useMemo(() => useNavigate(), []);

  const {
    isGameManagementModalOpen,
    closeGameManagementModal,
    isAddGameModalOpen,
    closeAddGameModal
  } = useGameStore();

  const { currentGame, selectGame } = useGameContext();
  const [isGameSheetOpen, setIsGameSheetOpen] = useState<boolean>(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);

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

    const handleSidebarToggle = (e: CustomEvent) => {
      setSidebarCollapsed(e.detail);
    };

    window.addEventListener('sidebarToggled', handleSidebarToggle as EventListener);

    return () => {
      window.removeEventListener('sidebarToggled', handleSidebarToggle as EventListener);
    };
  }, []);

  useEffect(() => {
    const sidebarWidth = sidebarCollapsed ? '60px' : '260px';
    document.documentElement.style.setProperty('--sidebar-current-width', sidebarWidth);
  }, [sidebarCollapsed]);

  const handleSelectGame = useCallback((game: GameData) => {
    selectGame({
      id: game.id,
      gid: game.gid,
      name: game.name,
      ods_db: game.ods_db
    });
  }, [selectGame]);

  const stableSetCurrentGame = useCallback((gameData: GameData) => {
    selectGame(gameData);
  }, [selectGame]);

  const contextValue = useMemo<OutletContextType>(() => ({
    currentGame,
    setCurrentGame: stableSetCurrentGame
  }), [currentGame, stableSetCurrentGame]);

  const outletKey = useMemo(() => location.pathname, [location.pathname]);

  const breadcrumbItems = useMemo(() => {
    return generateBreadcrumbs(location.pathname);
  }, [location.pathname]);

  return (
    <div className="app-shell" data-testid="main-layout">
      <div className="app-body">
        <Sidebar currentGame={currentGame} />
        <main className="app-content" data-testid="main-content">
          {breadcrumbItems.length > 1 && (
            <div className="breadcrumb-container">
              <Breadcrumb items={breadcrumbItems} />
            </div>
          )}
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
