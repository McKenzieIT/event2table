// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import { GameSelectionSheet } from '@analytics/components/game-selection/GameSelectionSheet';
import { Sidebar } from '@analytics/components/sidebar/Sidebar';
import { generateBreadcrumbs } from '@shared/config/breadcrumbConfig';
import Breadcrumb from '@shared/ui/Breadcrumb/Breadcrumb';
import Loading from '@shared/ui/Loading';
import { useState, useEffect, Suspense, useMemo, useCallback } from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import AddGameModal from '../../../features/games/AddGameModal';
import GameManagementModal from '../../../features/games/GameManagementModalGraphQL';
import { useGameStore } from '../../../stores/gameStore';

import { useGameContext } from '@/shared/hooks/useGameContext';

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

  const {
    isGameManagementModalOpen,
    closeGameManagementModal,
    isAddGameModalOpen,
    closeAddGameModal
  } = useGameStore();

  const { currentGame, selectGame } = useGameContext();
  const [isGameSheetOpen, setIsGameSheetOpen] = useState<boolean>(false);

  useEffect(() => {
    const handleToggle = () => setIsGameSheetOpen(prev => !prev);

    window.addEventListener('toggleGameSheet', handleToggle);

    return () => {
      window.removeEventListener('toggleGameSheet', handleToggle);
    };
  }, []);

  // 使用 useMemo 计算初始 sidebar 状态
  const initialSidebarCollapsed = useMemo(() => {
    try {
      const savedCollapsed = localStorage.getItem('sidebarCollapsed');
      if (savedCollapsed !== null) {
        return JSON.parse(savedCollapsed);
      }
    } catch (error) {
      console.error('[MainLayout] Failed to load sidebar state:', error);
    }
    return false; // 默认展开
  }, []);

  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(initialSidebarCollapsed);

  useEffect(() => {
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
  }, [sidebarCollapsed, setSidebarCollapsed]);

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
          {/* NOTE: Suspense removed to fix double-nesting issue with App.tsx global Suspense boundary.
           * The outer Suspense in App.tsx handles lazy-loaded route components.
           * This prevents Playwright test timeout issues caused by nested Suspense boundaries. */}
          <Outlet key={outletKey} context={contextValue} />
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
