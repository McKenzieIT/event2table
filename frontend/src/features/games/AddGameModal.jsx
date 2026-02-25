/**
 * AddGameModal - Add Game Modal Component
 *
 * 使用共享的 GameForm 组件,消除代码重复
 * Two-layer slide-out animation (on top of game management modal)
 */

import React from 'react';
import { BaseModal } from '@shared/ui/BaseModal/BaseModal';
import { GameForm } from '@shared/components/GameForm';
import './AddGameModal.css';

const AddGameModal = ({ isOpen, onClose }) => {
  // Handle successful game creation
  const handleSuccess = () => {
    handleClose();
  };

  // Handle close - close this modal only, don't reopen parent
  const handleClose = () => {
    onClose();
  };

  // Handle cancel
  const handleCancel = () => {
    handleClose();
  };

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={handleClose}
      title="添加游戏"
      animation="slideUp"
      glassmorphism
      size="full"
      variant="default"
      className="add-game-modal"
      enableEscClose={true}
    >
      {/* 添加关闭按钮 */}
      <div className="add-game-modal-header">
        <h3>添加游戏</h3>
        <button 
          className="modal-close" 
          onClick={handleClose}
          aria-label="关闭对话框"
          type="button"
        >
          ✕
        </button>
      </div>
      {/* 使用共享的 GameForm 组件 */}
      <GameForm
        mode="modal"
        onSuccess={handleSuccess}
        onCancel={handleCancel}
        submitButtonText="保存"
        cancelButtonText="取消"
      />
    </BaseModal>
  );
};

export { AddGameModal };
export default React.memo(AddGameModal);
