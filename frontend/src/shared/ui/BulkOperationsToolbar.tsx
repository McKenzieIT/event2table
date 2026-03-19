import React, { useState } from 'react';
import {
  bulkDeleteEvents,
  bulkExportEvents,
  bulkValidateParameters,
  type ValidationResult,
} from '@shared/api/bulkApi';
import './BulkOperationsToolbar.css';

interface BulkOperationsToolbarProps {
  selectedIds: number[];
  selectedCount: number;
  onDeleteSuccess?: () => void;
  onExportSuccess?: (data: unknown) => void;
  onValidateSuccess?: (results: ValidationResult[]) => void;
  disabled?: boolean;
}

/**
 * 批量操作工具栏组件
 *
 * 提供批量删除、导出、验证等功能
 *
 * @param selectedIds - 选中的ID列表
 * @param selectedCount - 选中的数量
 * @param onDeleteSuccess - 删除成功回调
 * @param onExportSuccess - 导出成功回调
 * @param onValidateSuccess - 验证成功回调
 * @param disabled - 是否禁用
 */
export const BulkOperationsToolbar: React.FC<BulkOperationsToolbarProps> = ({
  selectedIds,
  selectedCount,
  onDeleteSuccess,
  onExportSuccess,
  onValidateSuccess,
  disabled = false,
}) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [isValidating, setIsValidating] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) return;

    setIsDeleting(true);
    try {
      const response = await bulkDeleteEvents({ event_ids: selectedIds });
      if (response.success) {
        setShowDeleteConfirm(false);
        onDeleteSuccess?.();
        alert(`成功删除 ${response.data?.deleted_count} 个事件`);
      }
    } catch (error) {
      console.error('批量删除失败:', error);
      alert('批量删除失败，请重试');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleBulkExport = async () => {
    if (selectedIds.length === 0) return;

    setIsExporting(true);
    try {
      const response = await bulkExportEvents({
        event_ids: selectedIds,
        format: 'json',
      });
      if (response.success) {
        onExportSuccess?.(response.data);
        
        // 下载JSON文件
        const blob = new Blob([JSON.stringify(response.data?.events, null, 2)], {
          type: 'application/json',
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `events_export_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        alert(`成功导出 ${response.data?.count} 个事件`);
      }
    } catch (error) {
      console.error('批量导出失败:', error);
      alert('批量导出失败，请重试');
    } finally {
      setIsExporting(false);
    }
  };

  const handleBulkValidate = async () => {
    if (selectedIds.length === 0) return;

    setIsValidating(true);
    try {
      const response = await bulkValidateParameters({ event_ids: selectedIds });
      if (response.success) {
        onValidateSuccess?.(response.data?.results || []);
        
        const { valid_events, invalid_events } = response.data || {};
        alert(
          `验证完成：\n有效事件: ${valid_events} 个\n无效事件: ${invalid_events} 个`
        );
      }
    } catch (error) {
      console.error('批量验证失败:', error);
      alert('批量验证失败，请重试');
    } finally {
      setIsValidating(false);
    }
  };

  if (selectedCount === 0) {
    return null;
  }

  return (
    <>
      <div className="bulk-operations-toolbar">
        <div className="bulk-operations-info">
          <span className="bulk-operations-count">已选 {selectedCount} 项</span>
        </div>
        
        <div className="bulk-operations-actions">
          <button
            className="bulk-operations-button bulk-operations-button-validate"
            onClick={handleBulkValidate}
            disabled={disabled || isValidating}
            title="验证选中事件的参数"
          >
            {isValidating ? '验证中...' : '批量验证'}
          </button>

          <button
            className="bulk-operations-button bulk-operations-button-export"
            onClick={handleBulkExport}
            disabled={disabled || isExporting}
            title="导出选中事件的配置"
          >
            {isExporting ? '导出中...' : '批量导出'}
          </button>

          <button
            className="bulk-operations-button bulk-operations-button-delete"
            onClick={() => setShowDeleteConfirm(true)}
            disabled={disabled || isDeleting}
            title="删除选中事件"
          >
            {isDeleting ? '删除中...' : '批量删除'}
          </button>
        </div>
      </div>

      {/* 删除确认对话框 */}
      {showDeleteConfirm && (
        <div className="bulk-operations-modal-overlay">
          <div className="bulk-operations-modal">
            <div className="bulk-operations-modal-header">
              <h3>确认删除</h3>
            </div>
            <div className="bulk-operations-modal-body">
              <p>
                您确定要删除选中的 <strong>{selectedCount}</strong> 个事件吗？
              </p>
              <p className="bulk-operations-modal-warning">
                此操作不可恢复，请谨慎操作！
              </p>
            </div>
            <div className="bulk-operations-modal-footer">
              <button
                className="bulk-operations-button bulk-operations-button-cancel"
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
              >
                取消
              </button>
              <button
                className="bulk-operations-button bulk-operations-button-confirm-delete"
                onClick={handleBulkDelete}
                disabled={isDeleting}
              >
                {isDeleting ? '删除中...' : '确认删除'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default BulkOperationsToolbar;
