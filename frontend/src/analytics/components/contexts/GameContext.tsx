/**
 * 游戏上下文 - 全局游戏状态管理
 * Game Context - Global Game State Management
 *
 * ⚠️ DEPRECATED - 已废弃
 *
 * 此文件已被 @/stores/gameStore (Zustand) 替代
 * This file has been replaced by @/stores/gameStore (Zustand)
 *
 * 迁移指南 Migration Guide:
 * ------------------------
 * 旧代码 Old Code:
 *   import { useGameContext } from '@analytics/components/contexts/GameContext';
 *   const { currentGame, setGameData } = useGameContext();
 *
 * 新代码 New Code:
 *   import { useGameStore } from '@/stores/gameStore';
 *   const { currentGame, setGameData } = useGameStore();
 *
 * 优势 Advantages:
 * - 更好的性能 Better performance
 * - 更简洁的API Simpler API
 * - 更好的TypeScript支持 Better TypeScript support
 * - 自动持久化 Automatic persistence
 * - 无需Provider包装 No Provider wrapper needed
 *
 * 最后迁移完成: 2026-02-12 (ParametersList.jsx)
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

/**
 * 游戏信息接口
 */
export interface Game {
  id: number;
  gid: number;
  name: string;
  ods_db: string;
  dwd_prefix?: string;
}

/**
 * 游戏上下文值接口
 */
interface GameContextValue {
  gameGid: number | null;
  setGameGid: (gid: number | null) => void;
  gameData: Game | null;
  setGameData: (game: Game | null) => void;
  clearGame: () => void;
}

/**
 * 游戏上下文
 */
const GameContext = createContext<GameContextValue | null>(null);

/**
 * 游戏上下文Provider属性
 */
interface GameProviderProps {
  children: ReactNode;
}

/**
 * 游戏上下文Provider组件
 */
export function GameProvider({ children }: GameProviderProps) {
  const [gameGid, setGameGid] = useState<number | null>(null);
  const [gameData, setGameData] = useState<Game | null>(null);

  // 从localStorage恢复游戏上下文
  useEffect(() => {
    const savedGid = localStorage.getItem('selectedGameGid');
    const savedGameData = localStorage.getItem('selectedGameData');

    if (savedGid) {
      setGameGid(parseInt(savedGid));
    }

    if (savedGameData) {
      try {
        setGameData(JSON.parse(savedGameData));
      } catch (error) {
        console.error('Failed to parse saved game data:', error);
      }
    }
  }, []);

  // 保存游戏上下文到localStorage
  useEffect(() => {
    if (gameGid !== null) {
      localStorage.setItem('selectedGameGid', gameGid.toString());
    } else {
      localStorage.removeItem('selectedGameGid');
    }
  }, [gameGid]);

  useEffect(() => {
    if (gameData !== null) {
      localStorage.setItem('selectedGameData', JSON.stringify(gameData));
    } else {
      localStorage.removeItem('selectedGameData');
    }
  }, [gameData]);

  // 清除游戏上下文
  const clearGame = () => {
    setGameGid(null);
    setGameData(null);
    localStorage.removeItem('selectedGameGid');
    localStorage.removeItem('selectedGameData');
  };

  const value: GameContextValue = {
    gameGid,
    setGameGid,
    gameData,
    setGameData,
    clearGame,
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

/**
 * 使用游戏上下文的Hook
 */
export function useGameContext(): GameContextValue {
  const context = useContext(GameContext);

  if (!context) {
    throw new Error('useGameContext must be used within a GameProvider');
  }

  return context;
}
