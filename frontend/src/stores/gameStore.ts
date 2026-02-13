import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * 游戏信息接口
 * Game Information Interface
 */
export interface Game {
  id: number;
  gid: number;
  name: string;
  ods_db: string;
  dwd_prefix?: string;
}

/**
 * 游戏状态管理Store (Zustand)
 * 替代原有的 GameContext，提供更好的性能和开发体验
 * Game State Management Store (Zustand)
 * Replaces the original GameContext with better performance and DX
 */
interface GameStore {
  // 当前游戏数据
  currentGame: Game | null;

  // 游戏GID (用于向后兼容)
  gameGid: number | null;

  // 设置当前游戏
  setCurrentGame: (game: Game | null) => void;

  // 设置游戏数据 (别名，向后兼容)
  setGameData: (game: Game | null) => void;

  // 设置游戏GID (向后兼容)
  setGameGid: (gid: number | null) => void;

  // 清除游戏数据
  clearGame: () => void;

  // 清除当前游戏 (别名，向后兼容)
  clearCurrentGame: () => void;

  // 游戏管理模态框状态
  isGameManagementModalOpen: boolean;
  openGameManagementModal: () => void;
  closeGameManagementModal: () => void;

  // 添加游戏模态框状态
  isAddGameModalOpen: boolean;
  openAddGameModal: () => void;
  closeAddGameModal: () => void;
}

export const useGameStore = create<GameStore>()(
  persist(
    (set) => ({
      currentGame: null,
      gameGid: null,

      setCurrentGame: (game) => set({
        currentGame: game,
        gameGid: game?.gid || null
      }),

      setGameData: (game) => set({
        currentGame: game,
        gameGid: game?.gid || null
      }),

      setGameGid: (gid) => set({ gameGid: gid }),

      clearGame: () => set({
        currentGame: null,
        gameGid: null
      }),

      clearCurrentGame: () => set({
        currentGame: null,
        gameGid: null
      }),

      // Modal states
      isGameManagementModalOpen: false,
      openGameManagementModal: () => set({ isGameManagementModalOpen: true }),
      closeGameManagementModal: () => set({ isGameManagementModalOpen: false }),

      isAddGameModalOpen: false,
      openAddGameModal: () => set({ isAddGameModalOpen: true }),
      closeAddGameModal: () => set({ isAddGameModalOpen: false }),
    }),
    {
      name: 'game-storage',
      // 只持久化必要的状态
      partialize: (state) => ({
        currentGame: state.currentGame,
        gameGid: state.gameGid,
      }),
    }
  )
);
