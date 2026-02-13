// FlowsList.jsx
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Button, SearchInput } from '@shared/ui';
import './FlowsList.css';

export default function FlowsList() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [selectedFlow, setSelectedFlow] = useState(null);

  // 获取流程列表
  const { data: apiResponse, isLoading, error } = useQuery({
    queryKey: ['flows'],
    queryFn: async () => {
      const response = await fetch('/api/flows');
      if (!response.ok) throw new Error('Failed to fetch flows');
      const result = await response.json();
      return result;
    }
  });

  // Extract flows from API response
  const flows = apiResponse?.data?.flows || [];

  // 删除流程
  const deleteMutation = useMutation({
    mutationFn: async (flowId) => {
      const response = await fetch(`/api/flows/${flowId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete flow');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['flows']);
    }
  });

  // 过滤流程
  const filteredFlows = flows?.filter(flow =>
    flow.flow_name?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || [];

  const handleCreateFlow = () => {
    navigate('/flows/create');
  };

  const handleEditFlow = (flowId) => {
    navigate(`/flows/${flowId}/edit`);
  };

  if (error) {
    return (
      <div className="flows-list-page">
        <div className="error-message">
          <span>⚠️</span>
          <p>加载流程列表失败: {error.message}</p>
          <Button onClick={() => window.location.reload()}>重新加载</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flows-list-page">
      <div className="page-header">
        <h1>HQL 流程管理</h1>
        <Button variant="primary" onClick={handleCreateFlow}>
          新建流程
        </Button>
      </div>

      <div className="search-bar">
        <SearchInput
          placeholder="搜索流程名称..."
          value={searchTerm}
          onChange={(value) => setSearchTerm(value)}
        />
      </div>

      {isLoading ? (
        <div className="loading-spinner">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">加载中...</span>
          </div>
          <p>正在加载流程列表...</p>
        </div>
      ) : filteredFlows.length === 0 ? (
        <div className="empty-state">
          <span>📊</span>
          <p>暂无流程</p>
          <Button variant="primary" onClick={handleCreateFlow}>
            创建第一个流程
          </Button>
        </div>
      ) : (
        <div className="flows-grid">
          {filteredFlows.map(flow => (
            <div key={flow.id} className="flow-card">
              <div className="flow-header">
                <h3>{flow.flow_name}</h3>
                <span className={`flow-status status-active`}>
                  已保存
                </span>
              </div>
              <div className="flow-body">
                <p>{flow.description || '暂无描述'}</p>
                <div className="flow-meta">
                  <span>
                    📊
                    {flow.flow_graph?.nodes?.length || 0} 个节点
                  </span>
                  <span>
                    🕐
                    {flow.updated_at ? new Date(flow.updated_at).toLocaleString('zh-CN') : '未更新'}
                  </span>
                </div>
              </div>
              <div className="flow-actions">
                <Button
                  variant="secondary"
                  onClick={() => handleEditFlow(flow.id)}
                  title="编辑流程"
                >
                  编辑
                </Button>
                <Button
                  variant="success"
                  onClick={() => {/* TODO: 实现执行功能 */}}
                  title="执行流程"
                >
                  执行
                </Button>
                <Button
                  variant="danger"
                  onClick={() => {
                    if (confirm(`确定要删除流程"${flow.flow_name}"吗？`)) {
                      deleteMutation.mutate(flow.id);
                    }
                  }}
                  title="删除流程"
                  disabled={deleteMutation.isLoading}
                >
                  {deleteMutation.isLoading ? '删除中...' : '删除'}
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
