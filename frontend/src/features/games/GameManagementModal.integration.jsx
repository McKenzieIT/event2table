/**
 * GameManagementModal 集成示例
 *
 * 展示如何在现有应用中集成 GameManagementModal
 */

import React, { useState, useEffect } from 'react';
import { Button } from '@shared/ui';
import { GameManagementModal } from '@/features/games';

// ===== 示例 1: 在导航栏中集成 =====
function NavigationWithGameManager() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <h1>Event2Table</h1>
      </div>

      <div className="nav-menu">
        <a href="/dashboard">Dashboard</a>
        <a href="/canvas">Canvas</a>
        <a href="/events">Events</a>
      </div>

      <div className="nav-actions">
        <Button
          variant="outline-primary"
          size="sm"
          onClick={() => setIsModalOpen(true)}
        >
          游戏管理
        </Button>
      </div>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </nav>
  );
}

// ===== 示例 2: 在Dashboard页面集成 =====
function DashboardWithGameManager() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { currentGame, setCurrentGame } = useGameStore();

  // 当模态框关闭时，刷新当前游戏数据
  const handleModalClose = () => {
    setIsModalOpen(false);

    // 如果有选中的游戏，刷新其数据
    if (currentGame) {
      fetch(`/api/games/${currentGame.gid}`)
        .then(res => res.json())
        .then(result => {
          if (result.success) {
            setCurrentGame(result.data);
          }
        })
        .catch(err => {
          console.error('Failed to refresh game data:', err);
        });
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>数据看板</h1>
        <div className="header-actions">
          <Button
            variant="primary"
            onClick={() => setIsModalOpen(true)}
          >
            管理游戏
          </Button>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Dashboard 内容 */}
      </div>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
      />
    </div>
  );
}

// ===== 示例 3: 作为设置页面 =====
function SettingsPage() {
  return (
    <div className="settings-page">
      <div className="settings-header">
        <h1>系统设置</h1>
      </div>

      <div className="settings-sections">
        <section className="settings-section">
          <h2>游戏管理</h2>
          <p>管理系统中的游戏配置</p>
          <Button
            variant="primary"
            onClick={() => {
              // 直接导航到游戏管理页面
              // 或者打开模态框
            }}
          >
            打开游戏管理
          </Button>
        </section>

        {/* 其他设置部分 */}
      </div>
    </div>
  );
}

// ===== 示例 4: 与现有游戏列表集成 =====
function GamesListWithManager() {
  const [showManager, setShowManager] = useState(false);

  return (
    <div className="games-page">
      <div className="page-header">
        <h1>游戏列表</h1>
        <div className="header-actions">
          <Button
            variant="primary"
            onClick={() => setShowManager(true)}
          >
            游戏管理
          </Button>
        </div>
      </div>

      {/* 现有的游戏列表 */}
      <div className="games-list">
        {/* ... */}
      </div>

      {/* 管理模态框 */}
      <GameManagementModal
        isOpen={showManager}
        onClose={() => setShowManager(false)}
      />
    </div>
  );
}

// ===== 示例 5: 使用快捷键触发 =====
function AppWithKeyboardShortcuts() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl/Cmd + G 打开游戏管理
      if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
        e.preventDefault();
        setIsModalOpen(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="app">
      {/* 应用内容 */}

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}

// ===== 示例 6: 带状态同步的集成 =====
function AppWithGameSync() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { currentGame, setCurrentGame } = useGameStore();
  const queryClient = useQueryClient();

  const handleModalClose = () => {
    setIsModalOpen(false);

    // 刷新所有相关查询
    queryClient.invalidateQueries(['games']);

    // 如果有当前游戏，刷新其数据
    if (currentGame) {
      queryClient.invalidateQueries(['game', currentGame.gid]);
    }
  };

  return (
    <div className="app">
      <Button onClick={() => setIsModalOpen(true)}>
        游戏设置
      </Button>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={handleModalClose}
      />
    </div>
  );
}

export {
  NavigationWithGameManager,
  DashboardWithGameManager,
  SettingsPage,
  GamesListWithManager,
  AppWithKeyboardShortcuts,
  AppWithGameSync
};
