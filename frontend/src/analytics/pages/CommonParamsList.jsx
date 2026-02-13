import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, SearchInput } from '@shared/ui';
import './CommonParamsList.css';

/**
 * Common Parameters Management Page
 * Displays common parameter cards with search and CRUD operations
 */
export default function CommonParamsList() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIds, setSelectedIds] = useState(new Set());

  // Fetch common parameters with React Query
  const { data: params = [], isLoading, error } = useQuery({
    queryKey: ['common-params'],
    queryFn: async () => {
      const res = await fetch('/api/common-params');
      if (!res.ok) throw new Error('Failed to fetch common parameters');
      const result = await res.json();
      return result.data || [];
    }
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: async (id) => {
      const res = await fetch(`/api/common-params/${id}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Failed to delete parameter');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['common-params'] });
    }
  });

  // Batch delete mutation
  const batchDeleteMutation = useMutation({
    mutationFn: async (ids) => {
      const res = await fetch('/api/common-params/batch', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: Array.from(ids) })
      });
      if (!res.ok) throw new Error('Failed to batch delete parameters');
      return res.json();
    },
    onSuccess: () => {
      setSelectedIds(new Set());
      queryClient.invalidateQueries({ queryKey: ['common-params'] });
    }
  });

  // Sync common params mutation
  const syncMutation = useMutation({
    mutationFn: async () => {
      const gameGid = localStorage.getItem('selectedGameGid');
      if (!gameGid) {
        throw new Error('Please select a game first');
      }

      const res = await fetch('/common-params/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ game_gid: parseInt(gameGid) })
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.message || 'Failed to sync common parameters');
      }

      return res.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['common-params'] });
      alert(`同步成功！\n分析了 ${data.data.analyzed} 个参数\n添加了 ${data.data.added} 个新公参（来自 ${data.data.total_events} 个事件）`);
    },
    onError: (error) => {
      alert(`同步失败：${error.message}`);
    }
  });

  const handleSync = () => {
    const gameGid = localStorage.getItem('selectedGameGid');
    if (!gameGid) {
      alert('请先选择一个游戏');
      return;
    }

    if (confirm('确定要同步公共参数吗？\n\n系统将自动分析该游戏的所有事件，找出在90%以上事件中出现的参数并标记为公共参数。')) {
      syncMutation.mutate();
    }
  };

  // Filter parameters
  const filteredParams = params.filter(param => {
    return param.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
           param.key?.toLowerCase().includes(searchTerm.toLowerCase()) ||
           param.data_type?.toLowerCase().includes(searchTerm.toLowerCase());
  });

  // Selection handlers
  const toggleSelect = (id) => {
    setSelectedIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === filteredParams.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(filteredParams.map(p => p.id)));
    }
  };

  const handleBatchDelete = () => {
    if (selectedIds.size === 0) return;
    if (confirm(`确定删除选中的 ${selectedIds.size} 个公参吗？`)) {
      batchDeleteMutation.mutate(selectedIds);
    }
  };

  const handleDelete = (id) => {
    if (confirm('确定删除此公参吗？')) {
      deleteMutation.mutate(id);
    }
  };

  const getDataTypeBadge = (dataType) => {
    const badges = {
      string: { color: '#60a5fa', label: '字符串' },
      int: { color: '#34d399', label: '整数' },
      float: { color: '#f472b6', label: '浮点' },
      boolean: { color: '#a78bfa', label: '布尔' },
      json: { color: '#fbbf24', label: 'JSON' }
    };
    return badges[dataType] || { color: '#9ca3af', label: dataType };
  };

  if (isLoading) return <div className="loading-state">加载中...</div>;
  if (error) return <div className="error-state">加载失败: {error.message}</div>;

  return (
    <div className="common-params-page">
      <div className="page-header">
        <div className="header-left">
          <h1>公参管理</h1>
          <span className="param-count">共 {filteredParams.length} 个公参</span>
        </div>
        <div className="header-actions">
          <Button
            variant="secondary"
            onClick={handleSync}
            disabled={syncMutation.isPending}
            className="sync-button"
          >
            {syncMutation.isPending ? (
              <>
                <i className="bi bi-arrow-clockwise spinning"></i>
                同步中...
              </>
            ) : (
              <>
                <i className="bi bi-arrow-repeat"></i>
                同步公共参数
              </>
            )}
          </Button>
          <Button
            variant="primary"
            onClick={() => navigate('/common-params/create')}
          >
            新建公参
          </Button>
        </div>
      </div>

      {/* Selection Bar */}
      {selectedIds.size > 0 && (
        <div className="selection-bar">
          <span className="selection-count">已选择 {selectedIds.size} 个公参</span>
          <div className="selection-actions">
            <Button
              variant="danger"
              onClick={handleBatchDelete}
              disabled={batchDeleteMutation.isPending}
            >
              批量删除
            </Button>
            <Button
              variant="secondary"
              onClick={() => setSelectedIds(new Set())}
            >
              取消选择
            </Button>
          </div>
        </div>
      )}

      {/* Search Bar */}
      <div className="params-toolbar">
        <div className="search-box">
          <SearchInput
            placeholder="搜索参数名称、键名或类型..."
            value={searchTerm}
            onChange={(value) => setSearchTerm(value)}
          />
        </div>
      </div>

      {/* Parameter Cards Grid */}
      <div className="params-grid">
        {filteredParams.length === 0 ? (
          <div className="empty-state">
            <span>📥</span>
            <p>没有找到公参</p>
          </div>
        ) : (
          filteredParams.map(param => (
            <div key={param.id} className="param-card">
              <div className="card-header">
                <input
                  type="checkbox"
                  checked={selectedIds.has(param.id)}
                  onChange={() => toggleSelect(param.id)}
                />
                <h3>{param.name || param.key}</h3>
                <span
                  className="data-type-badge"
                  style={{ backgroundColor: getDataTypeBadge(param.data_type).color }}
                >
                  {getDataTypeBadge(param.data_type).label}
                </span>
              </div>
              <div className="card-body">
                <div className="param-key">
                  <span className="label">参数键:</span>
                  <span className="value">{param.key}</span>
                </div>
                {param.description && (
                  <p className="param-description">{param.description}</p>
                )}
                {param.default_value !== undefined && (
                  <div className="param-value">
                    <span className="label">默认值:</span>
                    <span className="value">{String(param.default_value)}</span>
                  </div>
                )}
              </div>
              <div className="card-footer">
                <Button
                  variant="secondary"
                  onClick={() => navigate(`/common-params/${param.id}/edit`)}
                >
                  编辑
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleDelete(param.id)}
                  disabled={deleteMutation.isPending}
                >
                  删除
                </Button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
