/**
 * GameManagementModal 使用示例
 *
 * 展示如何在应用中使用 GameManagementModal 组件
 */

import React, { useState } from 'react';
import { Button } from '@shared/ui';
import GameManagementModal from './GameManagementModal';

function ExampleUsage() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleOpenModal = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  return (
    <div>
      {/* 触发按钮 */}
      <Button variant="primary" onClick={handleOpenModal}>
        游戏管理
      </Button>

      {/* 模态框组件 */}
      <GameManagementModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
}

// ===== 从导航栏触发示例 =====
function NavigationExample() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <nav className="navigation">
      {/* 其他导航项... */}

      <Button
        variant="outline-primary"
        onClick={() => setIsModalOpen(true)}
      >
        游戏管理
      </Button>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </nav>
  );
}

// ===== 从Dashboard触发示例 =====
function DashboardExample() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <div className="dashboard">
      {/* Dashboard内容 */}

      {/* 浮动操作按钮 */}
      <div className="fab">
        <Button
          variant="primary"
          size="lg"
          onClick={() => setIsModalOpen(true)}
        >
          管理游戏
        </Button>
      </div>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
}

// ===== 与现有系统集成 =====
function IntegratedExample() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { currentGame, setCurrentGame } = useGameStore();

  // 当模态框关闭时，刷新当前游戏数据
  const handleCloseModal = () => {
    setIsModalOpen(false);

    // 如果有选中的游戏，刷新其数据
    if (currentGame) {
      fetch(`/api/games/${currentGame.gid}`)
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            setCurrentGame(data.data);
          }
        });
    }
  };

  return (
    <div>
      <Button onClick={() => setIsModalOpen(true)}>
        游戏设置
      </Button>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
}

export {
  ExampleUsage,
  NavigationExample,
  DashboardExample,
  IntegratedExample
};
