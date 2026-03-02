// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * ConfigListModal Component
 * 配置列表模态框组件
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchConfigList, deleteConfig, copyNode } from '@shared/api/eventNodeBuilder';
import { usePromiseConfirm } from '@shared/hooks/usePromiseConfirm';
import toast from 'react-hot-toast';
import type { EventNode } from '@shared/types/eventNodes';

/**
 * 组件Props接口
 */
interface ConfigListModalProps {
  gameGid?: number;
  onSelect: (config: EventNode) => void;
  onClose: () => void;
}

/**
 * 配置列表项接口
 */
interface ConfigListItem {
  id: number;
  name_en: string;
  name_cn?: string;
  event_name?: string;
  event_name_cn?: string;
  field_count?: number;
}

/**
 * API响应接口
 */
interface ConfigListResponse {
  configs: ConfigListItem[];
  has_more: boolean;
  total: number;
}

/**
 * 组件类型定义
 */
type ConfigListModalComponent = React.FC<ConfigListModalProps>;

/**
 * ConfigListModal: 配置列表模态框组件
 *
 * 功能：
 * - 显示保存的配置列表
 * - 支持分页加载
 * - 支持选择、复制、删除配置
 */
const ConfigListModal: ConfigListModalComponent = ({ gameGid, onSelect, onClose }) => {
  const [page, setPage] = useState(1);
  const [selectedConfigId, setSelectedConfigId] = useState<number | null>(null);

  // Promise-based confirm dialog
  const { confirm, ConfirmDialogComponent } = usePromiseConfirm();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['config-list', gameGid, page],
    queryFn: () => fetchConfigList(gameGid, page),
    enabled: !!gameGid,
  });

  const configs = data?.data?.configs || [];
  const hasMore = data?.data?.has_more || false;

  /**
   * 处理配置选择
   */
  const handleSelect = (config: ConfigListItem): void => {
    onSelect(config as EventNode);
    onClose();
  };

  /**
   * 处理配置删除
   */
  const handleDelete = async (configId: number, e: React.MouseEvent): Promise<void> => {
    e.stopPropagation();
    const confirmed = await confirm('确定要删除这个配置吗？');
    if (!confirmed) {
      return;
    }

    const result = await deleteConfig(configId);
    if (result.success) {
      refetch();
      toast.success('删除成功');
    } else {
      toast.error('删除失败: ' + (result.error || '未知错误'));
    }
  };

  /**
   * 处理配置复制
   */
  const handleCopy = async (nodeId: number, e: React.MouseEvent): Promise<void> => {
    e.stopPropagation();
    const result = await copyNode(nodeId);
    if (result.success) {
      toast.success('复制成功');
      refetch();
    } else {
      toast.error('复制失败: ' + (result.error || '未知错误'));
    }
  };

  /**
   * 处理键盘事件
   */
  const handleKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClose();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  };

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      tabIndex={0}
      role="button"
      aria-label="关闭"
      onKeyDown={handleKeyDown}
    >
      <div
        className="modal-content glass-card config-list-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>配置列表</h3>
          <button className="modal-close" onClick={onClose} aria-label="关闭对话框">
            ✕
          </button>
        </div>
        <div className="modal-body">
          {isLoading ? (
            <div className="modal-loading">
              <div className="spinner-border" role="status"></div>
              <p>加载中...</p>
            </div>
          ) : configs.length === 0 ? (
            <div className="modal-empty">
              <p>暂无保存的配置</p>
            </div>
          ) : (
            <div className="config-list">
              {configs.map((config: ConfigListItem) => (
                <div
                  key={config.id}
                  className="config-list-item"
                  onClick={() => handleSelect(config)}
                >
                  <div className="config-info">
                    <div className="config-name">{config.name_cn || config.name_en}</div>
                    <div className="config-meta">
                      <span>{config.name_en}</span>
                      <span>•</span>
                      <span>{config.event_name_cn || config.event_name}</span>
                      <span>•</span>
                      <span>{config.field_count || 0} 个字段</span>
                    </div>
                  </div>
                  <div className="config-actions">
                    <button
                      className="btn btn-sm btn-outline-primary"
                      onClick={(e) => handleCopy(config.id, e)}
                      title="复制"
                      type="button"
                    >
                      复制
                    </button>
                    <button
                      className="btn btn-sm btn-outline-danger"
                      onClick={(e) => handleDelete(config.id, e)}
                      title="删除"
                      type="button"
                    >
                      删除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="modal-footer">
          {hasMore && (
            <button
              className="btn btn-secondary"
              onClick={() => setPage((p) => p + 1)}
              type="button"
            >
              加载更多
            </button>
          )}
          <button className="btn btn-secondary" onClick={onClose} type="button">
            关闭
          </button>
        </div>
      </div>

      {/* Promise-based confirm dialog */}
      <ConfirmDialogComponent />
    </div>
  );
};

export default ConfigListModal;
