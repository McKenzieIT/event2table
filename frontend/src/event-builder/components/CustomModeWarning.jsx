/**
 * CustomModeWarning Component
 * 自定义编辑模式智能提醒对话框组件
 */
import React from 'react';
import PropTypes from 'prop-types';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';

export default function CustomModeWarning({
  isOpen,
  onClose,
  onConfirm,
  actionType = 'add', // 'add' | 'modify'
  itemType = 'field' // 'field' | 'condition'
}) {
  const getTitle = () => {
    return '⚠️ 自定义编辑模式警告';
  };

  const getMessage = () => {
    const itemText = itemType === 'field' ? '字段' : 'WHERE条件';
    const actionText = actionType === 'add' ? '添加' : '修改';

    return (
      <div style={{ textAlign: 'left', lineHeight: '1.6' }}>
        <p style={{ marginBottom: '12px', fontSize: '14px', color: 'rgba(255, 255, 255, 0.9)' }}>
          <strong style={{ color: '#06B6D4' }}>您正在自定义编辑HQL内容</strong>
        </p>
        <p style={{ marginBottom: '12px', fontSize: '13px', color: 'rgba(255, 255, 255, 0.8)' }}>
          {actionText}{itemText}后，自动生成的HQL将会被覆盖，您的自定义编辑内容将会丢失。
        </p>
        <p style={{ marginBottom: '12px', fontSize: '13px', color: 'rgba(255, 255, 255, 0.8)' }}>
          建议您：
        </p>
        <ul style={{
          marginLeft: '20px',
          marginBottom: '12px',
          fontSize: '13px',
          color: 'rgba(255, 255, 255, 0.7)',
          listStyleType: 'disc'
        }}>
          <li style={{ marginBottom: '6px' }}>先保存当前的自定义HQL内容</li>
          <li style={{ marginBottom: '6px' }}>然后再{actionText}{itemText}</li>
          <li>或者退出自定义编辑模式，使用自动生成功能</li>
        </ul>
        <p style={{ fontSize: '13px', color: 'rgba(6, 182, 212, 0.9)', fontWeight: '500' }}>
          是否继续{actionText}{itemText}？（自定义内容将丢失）
        </p>
      </div>
    );
  };

  const handleConfirm = () => {
    if (onConfirm) {
      onConfirm();
    }
    onClose();
  };

  return (
    <ConfirmDialog
      isOpen={isOpen}
      title={getTitle()}
      message={getMessage()}
      confirmText={`继续${actionType === 'add' ? '添加' : '修改'}`}
      cancelText="取消"
      onConfirm={handleConfirm}
      onCancel={onClose}
      type="warning"
    />
  );
}

CustomModeWarning.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onConfirm: PropTypes.func.isRequired,
  actionType: PropTypes.oneOf(['add', 'modify']),
  itemType: PropTypes.oneOf(['field', 'condition'])
};
