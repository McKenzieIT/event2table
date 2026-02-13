/**
 * DeleteConfirmModal Component - 自定义删除确认弹窗
 *
 * 替代 window.confirm()，提供更好的用户体验
 *
 * @example
 * <DeleteConfirmModal
 *   itemName="字段"
 *   itemDetails={{ name: 'user_id', type: '参数' }}
 *   onConfirm={() => handleDelete()}
 *   onClose={() => setShowModal(false)}
 * />
 *
 * Props:
 * @param {string} itemName - 要删除的项目名称（如"字段"、"事件"）
 * @param {Object} itemDetails - 项目详情对象
 * @param {string} itemDetails.name - 项目名称
 * @param {string} [itemDetails.type] - 项目类型（可选）
 * @param {Function} onConfirm - 确认删除回调
 * @param {Function} onClose - 关闭弹窗回调
 */

import React from 'react';
import { Button } from '../ui/Button';

export function DeleteConfirmModal({ itemName, itemDetails, onConfirm, onClose }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h4>确认删除</h4>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <p>确定要删除此{itemName}吗？</p>
          {itemDetails && (
            <div className="delete-item-details">
              <strong>名称:</strong> {itemDetails.name}<br />
              {itemDetails.type && <><strong>类型:</strong> {itemDetails.type}</>}
            </div>
          )}
          <p className="text-warning">此操作不可恢复。</p>
        </div>
        <div className="modal-footer">
          <Button variant="secondary" onClick={onClose}>
            取消
          </Button>
          <Button variant="danger" onClick={onConfirm}>
            确认删除
          </Button>
        </div>
      </div>
    </div>
  );
}
