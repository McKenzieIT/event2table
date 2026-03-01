import React, { useState, useMemo, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Button, SearchInput, Spinner, useToast, EmptyState } from '@shared/ui';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import './HqlManage.css';

/**
 * HQL管理页面
 *
 * 查看、编辑和管理已生成的HQL语句
 * 迁移自: templates/hql_manage.html
 * 最佳实践: useMemo + useCallback + 所有Hooks在顶层（修复React Hooks顺序错误）
 */

// Type Definitions
interface HqlRecord {
  id: number;
  hql_type: 'create' | 'join' | 'union_all';
  event_name: string;
  event_name_cn: string;
  game_name: string;
  hql_version: number;
  is_active: boolean;
  is_user_edited: boolean;
  updated_at: string;
}

interface ConfirmState {
  open: boolean;
  onConfirm: () => void;
  title: string;
  message: string;
}

interface HqlListResponse {
  success: boolean;
  data: {
    data: HqlRecord[];
  };
}

function HqlManage(): React.JSX.Element {
  // 1. 状态声明（5个 Hooks）
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [editedOnly, setEditedOnly] = useState<boolean>(false);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [confirmState, setConfirmState] = useState<ConfirmState>({
    open: false,
    onConfirm: () => {},
    title: '',
    message: ''
  });
  const { info } = useToast();

  // 2. 数据获取（1个 Hook）
  const { data: hqlData, isLoading } = useQuery<HqlListResponse>({
    queryKey: ['hql-list', typeFilter, editedOnly],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (typeFilter) params.append('hql_type', typeFilter);
      if (editedOnly) params.append('edited_only', 'true');

      const response = await fetch(`/api/hql?${params}`);
      if (!response.ok) throw new Error('加载HQL失败');
      return response.json();
    }
  });

  // 3. 计算值和事件处理（必须在所有渲染时调用）
  const hqlList: HqlRecord[] = hqlData?.data?.data || [];

  const filteredHql = useMemo(() => {
    if (!searchTerm) return hqlList;
    return hqlList.filter(hql =>
      hql.event_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [hqlList, searchTerm]);

  const handleToggleActive = useCallback(async (hqlId: number) => {
    // 切换激活状态
    info(`切换HQL \${hqlId} 激活状态 - 待实现`);
  }, [info]);

  const handleDelete = useCallback(async (hqlId: number) => {
    setConfirmState({
      open: true,
      title: '确认删除',
      message: '确定要删除这个HQL吗？',
      onConfirm: () => {
        setConfirmState(s => ({ ...s, open: false }));
        info(`删除HQL \${hqlId} - 待实现`);
      }
    });
  }, [info]);

  // 4. 条件返回 - 放在所有Hooks之后
  if (isLoading) {
    return (
      <div className="loading-container">
        <Spinner size="lg" label="加载中..." />
      </div>
    );
  }

  return (
    <div className="hql-manage-container" data-testid="hql-manage">
      {/* Page Header */}
      <div className="page-header glass-card">
        <div className="header-content">
          <div className="icon-box">
            <span>📄</span>
          </div>
          <div>
            <h1>HQL管理</h1>
            <p>查看、编辑和管理所有已生成的HQL语句</p>
          </div>
        </div>
        <Link to="/generate">
          <Button variant="primary">
            生成新HQL
          </Button>
        </Link>
      </div>

      {/* Filter Toolbar */}
      <div className="filter-toolbar glass-card">
        <select
          className="glass-select"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
        >
          <option value="">全部类型</option>
          <option value="create">建表 (CREATE)</option>
          <option value="join">关联 (JOIN)</option>
        </select>

        <select
          className="glass-select"
          value={editedOnly ? 'true' : 'false'}
          onChange={(e) => setEditedOnly(e.target.value === 'true')}
        >
          <option value="false">全部</option>
          <option value="true">仅已编辑</option>
        </select>

        <SearchInput
          placeholder="搜索事件名..."
          value={searchTerm}
          onChange={(value) => setSearchTerm(value)}
        />
      </div>

      {/* HQL Table */}
      <div className="hql-table-card glass-card">
        <table className="oled-table">
          <thead>
            <tr>
              <th>类型</th>
              <th>事件名</th>
              <th>游戏</th>
              <th>版本</th>
              <th>状态</th>
              <th>编辑状态</th>
              <th>最后更新</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {filteredHql.length === 0 ? (
              <tr>
                <td colSpan={8}>
                  <EmptyState
                    icon={<span style={{ fontSize: '48px' }}>📥</span>}
                    title="未找到HQL记录"
                  />
                </td>
              </tr>
            ) : (
              filteredHql.map(hql => (
                <tr key={hql.id} className={hql.is_user_edited ? 'user-edited-row' : ''}>
                  <td>
                    <span className={`badge badge-\${hql.hql_type === 'create' ? 'primary' : 'success'}`}>
                      {hql.hql_type === 'create' ? '📊' : '🔗'}
                      {hql.hql_type?.toUpperCase()}
                    </span>
                  </td>
                  <td>
                    <div className="event-name">{hql.event_name}</div>
                    <div className="event-name-cn">{hql.event_name_cn}</div>
                  </td>
                  <td>
                    <span className="text-muted">🎮</span>
                    {hql.game_name}
                  </td>
                  <td>
                    <span className="badge badge-secondary">v{hql.hql_version}</span>
                  </td>
                  <td>
                    {hql.is_active ? (
                      <span className="badge badge-success">
                        ✅ 激活
                      </span>
                    ) : (
                      <span className="badge badge-secondary">
                        ⏸️ 停用
                      </span>
                    )}
                  </td>
                  <td>
                    {hql.is_user_edited && (
                      <span className="badge badge-info">
                        ✏️ 已编辑
                      </span>
                    )}
                  </td>
                  <td>{new Date(hql.updated_at).toLocaleString('zh-CN')}</td>
                  <td>
                    <div className="action-buttons">
                      <Link to={`/hql/\${hql.id}/edit`}>
                        <Button variant="outline-primary" size="sm">
                          编辑
                        </Button>
                      </Link>
                      <Button
                        variant="outline-secondary"
                        size="sm"
                        onClick={() => handleToggleActive(hql.id)}
                      >
                        切换
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDelete(hql.id)}
                      >
                        删除
                      </Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

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

export default HqlManage;
