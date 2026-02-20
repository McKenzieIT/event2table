/**
 * ConfigListModal Component
 * 配置列表模态框组件
 */
import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchConfigList, deleteConfig, copyNode } from '@shared/api/eventNodeBuilder';
import toast from 'react-hot-toast';

export default function ConfigListModal({ gameGid, onSelect, onClose }) {
  const [page, setPage] = useState(1);
  const [selectedConfigId, setSelectedConfigId] = useState(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['config-list', gameGid, page],
    queryFn: () => fetchConfigList(gameGid, page),
    enabled: !!gameGid,
  });

  const configs = data?.data?.configs || [];
  const hasMore = data?.data?.has_more || false;

  const handleSelect = (config) => {
    onSelect(config);
    onClose();
  };

  const handleDelete = async (configId, e) => {
    e.stopPropagation();
    if (!confirm('确定要删除这个配置吗？')) {
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

  const handleCopy = async (nodeId, e) => {
    e.stopPropagation();
    const result = await copyNode(nodeId);
    if (result.success) {
      toast.success('复制成功');
      refetch();
    } else {
      toast.error('复制失败: ' + (result.error || '未知错误'));
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal-content glass-card config-list-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>配置列表</h3>
          <button className="modal-close" onClick={onClose}>
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
              {configs.map(config => (
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
                    >
                      复制
                    </button>
                    <button
                      className="btn btn-sm btn-outline-danger"
                      onClick={(e) => handleDelete(config.id, e)}
                      title="删除"
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
              onClick={() => setPage(p => p + 1)}
            >
              加载更多
            </button>
          )}
          <button className="btn btn-secondary" onClick={onClose}>
            关闭
          </button>
        </div>
      </div>
    </div>
  );
}
