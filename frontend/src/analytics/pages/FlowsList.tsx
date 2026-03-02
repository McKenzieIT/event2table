// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import { useState, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button, SearchInput, Spinner, EmptyState } from '@shared/ui';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import './FlowsList.css';

/**
 * Type Definitions
 */

/**
 * Flow graph structure
 */
interface FlowGraph {
  nodes: unknown[];
  edges: unknown[];
}

/**
 * Flow entity from API
 */
interface Flow {
  id: number;
  flow_name: string;
  description?: string | null;
  flow_graph?: FlowGraph | null;
  created_at?: string;
  updated_at?: string;
}

/**
 * API Response wrapper for flows
 */
interface FlowsAPIResponse {
  data: {
    flows: Flow[];
  };
  success: boolean;
  message?: string;
}

/**
 * Confirmation dialog state
 */
interface ConfirmState {
  open: boolean;
  onConfirm: () => void;
  title: string;
  message: string;
}

/**
 * Flows List Page
 * Displays HQL flow templates with search and CRUD operations
 *
 * Requires: game_gid URL parameter (enforced by backend API)
 */
export default function FlowsList(): JSX.Element {
  const navigate = useNavigate();
  const location = useLocation();
  const queryClient = useQueryClient();

  // Local state
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [isDrawerOpen, setIsDrawerOpen] = useState<boolean>(false);
  const [selectedFlow, setSelectedFlow] = useState<Flow | null>(null);
  const [confirmState, setConfirmState] = useState<ConfirmState>({
    open: false,
    onConfirm: () => {},
    title: '',
    message: ''
  });

  // Read game_gid from URL parameters
  const gameGid: string | null = new URLSearchParams(location.search).get('game_gid');

  // 获取流程列表（requires game_gid）
  const { data: apiResponse, isLoading, error } = useQuery<FlowsAPIResponse>({
    queryKey: ['flows', gameGid],
    queryFn: async (): Promise<FlowsAPIResponse> => {
      if (!gameGid) {
        throw new Error('game_gid is required');
      }

      const response = await fetch(`/api/flows?game_gid=${gameGid}`);
      if (!response.ok) {
        if (response.status === 400) {
          throw new Error('game_gid is required');
        }
        if (response.status === 404) {
          throw new Error(`Game ${gameGid} not found`);
        }
        throw new Error('Failed to fetch flows');
      }
      const result = await response.json();
      return result;
    },
    enabled: !!gameGid // Only run query if gameGid exists
  });

  // Extract flows from API response
  const flows: Flow[] = apiResponse?.data?.flows || [];

  // 删除流程
  const deleteMutation = useMutation({
    mutationFn: async (flowId: number) => {
      const response = await fetch(`/api/flows/${flowId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete flow');
      return response.json();
    },
    onSuccess: () => {
      // ✅ Fix: Use complete cache key with gameGid for precise invalidation
      queryClient.invalidateQueries({ queryKey: ['flows', gameGid] });
    }
  });

  // Handle delete flow confirmation
  const handleDeleteFlow = (flow: Flow): void => {
    setConfirmState({
      open: true,
      title: '确认删除',
      message: `确定要删除流程"${flow.flow_name}"吗？`,
      onConfirm: () => {
        setConfirmState(s => ({ ...s, open: false }));
        deleteMutation.mutate(flow.id);
      }
    });
  };

  // FIX: 使用useMemo优化过滤逻辑
  const filteredFlows = useMemo(() =>
    flows?.filter(flow =>
      flow.flow_name?.toLowerCase().includes(searchTerm.toLowerCase())
    ) || [],
    [flows, searchTerm]
  );

  const handleEditFlow = (flowId: number): void => {
    navigate(`/flows/${flowId}/edit?game_gid=${gameGid}`);
  };

  const handleCreateFlow = (): void => {
    navigate('/flows/create' + (gameGid ? `?game_gid=${gameGid}` : ''));
  };

  // Show error if game_gid is missing
  if (!gameGid) {
    return (
      <div className="flows-list-page">
        <div className="error-message">
          <h2>请先选择游戏</h2>
          <p>流程管理需要选择一个游戏才能查看。</p>
          <Button onClick={() => navigate('/')}>
            返回首页选择游戏
          </Button>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flows-list-page">
        <div className="error-message">
          <span>⚠️</span>
          <p>加载流程列表失败: {(error as Error).message}</p>
          <Button onClick={() => queryClient.invalidateQueries({ queryKey: ['flows', gameGid] })}>重新加载</Button>
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
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
          <Spinner size="lg" label="正在加载流程列表..." />
        </div>
      ) : filteredFlows.length === 0 ? (
        <EmptyState
          icon={<span style={{ fontSize: '48px' }}>📊</span>}
          title="暂无流程"
          action={{
            label: '创建第一个流程',
            onClick: handleCreateFlow
          }}
        />
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
                  onClick={() => handleDeleteFlow(flow)}
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

      <ConfirmDialog
        open={confirmState.open}
        title={confirmState.title}
        message={confirmState.message}
        confirmText="删除"
        cancelText="取消"
        variant="danger"
        onConfirm={confirmState.onConfirm}
        onCancel={() => setConfirmState(s => ({ ...s, open: false }))}
      />
    </div>
  );
}
