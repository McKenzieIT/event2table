/* eslint-disable react-hooks/rules-of-hooks */
import { useState, useMemo, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useOutletContext } from 'react-router-dom';
import React from 'react';
import {
  Button,
  Input,
  SearchInput,
  Checkbox,
  Select,
  Badge,
  Spinner,
  useToast,
  SelectGamePrompt,
  Pagination
} from '@shared/ui';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import './EventsList.css';

function EventsList() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { currentGame } = useOutletContext();
  const { success, error: showError } = useToast();

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedEvents, setSelectedEvents] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [confirmState, setConfirmState] = useState({ open: false, onConfirm: () => {}, title: '', message: '' });
  const [pageSize, setPageSize] = useState(10);

  // Game context check - render prompt if no game selected
  // This must be AFTER all useState calls to maintain hooks order
  const hasGameContext = !!currentGame;

  // Use placeholder data when no game is selected - this keeps hooks consistent
  const placeholderData = { events: [], pagination: { total: 0, total_pages: 1 } };
  
  // Fetch events list - always call this hook for consistent hooks order
  const { data, isLoading, error: fetchError } = useQuery({
    queryKey: ['events', currentPage, pageSize, selectedCategory, currentGame?.gid, searchTerm],
    queryFn: async () => {
      // Guard: don't fetch if no game context
      if (!currentGame?.gid) {
        return placeholderData;
      }
      
      const params = new URLSearchParams({
        page: currentPage.toString(),
        per_page: pageSize.toString(),
        game_gid: currentGame.gid.toString()
      });

      if (searchTerm) {
        params.append('search', searchTerm);
      }

      console.log('[EventsList] Fetching events with params:', params.toString());
      const response = await fetch(`/api/events?${params.toString()}`);
      if (!response.ok) throw new Error('Failed to fetch events');
      const result = await response.json();

      if (!result?.success) {
        throw new Error(result?.message || 'Failed to fetch events');
      }

      return result.data || {};
    },
    // Only enable when we have a valid game context
    enabled: hasGameContext
  });

  // Use placeholder data when no game is selected
  const effectiveData = hasGameContext ? data : placeholderData;

  // Batch delete mutation - must be BEFORE any conditional returns
  const deleteMutation = useMutation({
    mutationFn: async (eventIds) => {
      const response = await fetch('/api/events/batch', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: eventIds })
      });
      if (!response.ok) throw new Error('Failed to delete events');
      return response.json();
    },
    onSuccess: (data) => {
      // ✅ Fix: Use complete cache key with game_gid for precise invalidation
      queryClient.invalidateQueries({
        queryKey: ['events', currentGame?.gid]
      });
      setSelectedEvents([]);
      const deletedCount = data?.data?.deleted_count ?? data?.deleted_count ?? 0;
      success(`成功删除 ${deletedCount} 个事件`);
    },
    onError: (err) => {
      showError(`删除失败: ${err.message}`);
    }
  });

  // All useMemo calls - MUST be before ANY conditional returns
  const filteredEvents = useMemo(() => {
    const events = effectiveData?.events;
    if (!Array.isArray(events)) {
      return [];
    }

    // Backend already handles search filtering via API parameter
    // Only need to filter by category on the client side
    const filtered = events.filter(event => {
      const matchesCategory = selectedCategory === 'all' ||
        event.category_name?.toLowerCase() === selectedCategory.toLowerCase();
      return matchesCategory;
    });

    console.log('[EventsList] Filtered events count:', filtered.length, 'Total events:', events.length);
    return filtered;
  }, [effectiveData, selectedCategory]);

  const categories = useMemo(() => {
    const events = effectiveData?.events;
    if (!Array.isArray(events)) {
      return ['all'];
    }

    return ['all', ...new Set(events.map(e => e.category_name).filter(Boolean))];
  }, [effectiveData]);

  const pageSizeOptions = useMemo(() => [
    { value: '10', label: '10' },
    { value: '20', label: '20' },
    { value: '50', label: '50' },
    { value: '100', label: '100' }
  ], []);

  // Callbacks that depend on currentGame - use optional chaining for safety
  const handleViewEvent = useCallback((eventId) => {
    navigate(`/events/${eventId}?game_gid=${currentGame?.gid}`);
  }, [navigate, currentGame?.gid]);

  const handleEditEvent = useCallback((eventId) => {
    navigate(`/events/${eventId}/edit?game_gid=${currentGame?.gid}`);
  }, [navigate, currentGame?.gid]);

  // Handle search with debounce - using useCallback
  const handleSearchChange = useCallback((value) => {
    console.log('[EventsList] Search term changed:', value);
    setSearchTerm(value);
    setCurrentPage(1); // Reset to first page on search
  }, []);

  // Handle toggle select - using useCallback
  const handleToggleSelect = useCallback((eventId) => {
    setSelectedEvents(prev => {
      if (prev.includes(eventId)) {
        return prev.filter(id => id !== eventId);
      } else {
        return [...prev, eventId];
      }
    });
  }, []);

  // Handle select all - using useCallback
  const handleSelectAll = useCallback(() => {
    setSelectedEvents(prev => {
      if (prev.length === filteredEvents.length) {
        return [];
      } else {
        return filteredEvents.map(e => e.id);
      }
    });
  }, [filteredEvents]);

  // Handle batch delete - using useCallback
  const handleBatchDelete = useCallback(() => {
    if (selectedEvents.length === 0) {
      showError('请先选择要删除的事件');
      return;
    }
    setConfirmState({
      open: true,
      title: '确认批量删除',
      message: `确定要删除选中的 ${selectedEvents.length} 个事件吗？\n\n警告：此操作将同时删除所有关联的参数，且不可恢复！`,
      onConfirm: () => {
        setConfirmState(s => ({ ...s, open: false }));
        deleteMutation.mutate(selectedEvents);
      }
    });
  }, [selectedEvents.length, deleteMutation, showError]);

  // Handle delete event - using useCallback
  const handleDeleteEvent = useCallback((eventId, eventName) => {
    setConfirmState({
      open: true,
      title: '确认删除',
      message: `确定要删除事件「${eventName}」吗？\n\n警告：此操作将同时删除所有关联的参数，且不可恢复！`,
      onConfirm: () => {
        setConfirmState(s => ({ ...s, open: false }));
        deleteMutation.mutate([eventId]);
      }
    });
  }, [deleteMutation]);

  // Handle clear selection - using useCallback
  const handleClearSelection = useCallback(() => {
    setSelectedEvents([]);
  }, []);

  // Get pagination info with optional chaining
  const pagination = effectiveData?.pagination || {};
  const totalPages = pagination.total_pages || 1;
  const total = pagination.total || 0;

  // Always render content - handle error state and no game context inline
  // This ensures consistent Hooks order across all render paths
  const renderContent = () => {
    // Show game selection prompt if no game context
    if (!hasGameContext) {
      return <SelectGamePrompt message="查看事件列表需要先选择游戏" />;
    }

    if (fetchError) {
      return (
        <div className="events-list-page">
          <div className="error-message">
            <p>加载事件列表失败: {fetchError.message}</p>
            <Button variant="primary" onClick={() => {
              // ✅ Fix: Use complete cache key with game_gid for precise invalidation
              queryClient.invalidateQueries({
                queryKey: ['events', currentGame?.gid]
              });
            }}>
              重新加载
            </Button>
          </div>
        </div>
      );
    }

    return (
    <div className="events-list-page">
      {/* Page Header */}
      <div className="page-header">
        <div className="header-title">
          <div className="hero-icon-box blue">
            <span>事件</span>
          </div>
          <div>
            <h1>日志事件管理</h1>
            <p>管理和配置所有日志事件</p>
          </div>
        </div>
        <div className="header-actions">
          {selectedEvents.length > 0 && (
            <Button
              variant="danger"
              onClick={handleBatchDelete}
            >
              删除选中 ({selectedEvents.length})
            </Button>
          )}
          <Button
            variant="outline-success"
            onClick={() => navigate('/import-events')}
          >
            导入Excel
          </Button>
          <Button
            variant="primary"
            onClick={() => navigate('/events/create')}
            data-testid="add-event-button"
          >
            新增事件
          </Button>
        </div>
      </div>

      {/* Statistics Cards - Always show */}
      <div className="stats-container">
        <div className="stat-card">
          <div className="stat-value">{total}</div>
          <div className="stat-label">
            <span>总事件数</span>
          </div>
        </div>
        <div className="stat-card purple">
          <div className="stat-value">
            {data?.events ? data.events.filter(e => e.category_name).length : 0}
          </div>
          <div className="stat-label">
            <span>已分类</span>
          </div>
        </div>
        <div className="stat-card orange">
          <div className="stat-value">
            {data?.events ? data.events.filter(e => !e.category_name).length : 0}
          </div>
          <div className="stat-label">
            <span>未分类</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="filters-bar">
        <SearchInput
          placeholder="搜索事件名、中文名或分类..."
          value={searchTerm}
          onChange={(value) => handleSearchChange(value)}
        />

        <div className="filter-actions">
          <label className="select-all-label">
            <Checkbox
              checked={selectedEvents.length === filteredEvents.length && filteredEvents.length > 0}
              onChange={handleSelectAll}
            />
            <Badge variant="primary">全选</Badge>
          </label>

          {selectedEvents.length > 0 && (
            <>
              <div className="divider"></div>
              <span className="selected-count">
                已选择 <strong>{selectedEvents.length}</strong> 个事件
              </span>
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={handleClearSelection}
              >
                取消选择
              </Button>
            </>
          )}
        </div>
      </div>

      {/* Events Table */}
      {isLoading ? (
        <div className="loading-state">
          <Spinner size="lg" label="正在加载事件列表..." />
        </div>
      ) : filteredEvents.length === 0 ? (
        <div className="empty-state">
          <h3>暂无日志事件</h3>
          <p>暂无事件，请先创建事件。</p>
          <div className="empty-actions">
            <Button
              variant="success"
              onClick={() => navigate('/import-events')}
            >
              导入Excel
            </Button>
            <Button
              variant="outline-primary"
              onClick={() => navigate('/events/create')}
            >
              创建事件
            </Button>
          </div>
        </div>
      ) : (
        <div className="events-table-container">
          <table className="oled-table">
            <thead>
              <tr>
                <th style={{ width: '50px', textAlign: 'center' }}>
                  <Checkbox
                    checked={selectedEvents.length === filteredEvents.length && filteredEvents.length > 0}
                    onChange={handleSelectAll}
                  />
                </th>
                <th style={{ width: '70px' }}>ID</th>
                <th style={{ width: '25%' }}>事件名称</th>
                <th style={{ width: '20%' }}>游戏</th>
                <th style={{ width: '120px' }}>分类</th>
                <th style={{ width: '80px', textAlign: 'center' }}>参数</th>
                <th style={{ width: '220px' }}>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map(event => (
                <tr
                  key={event.id}
                  className={`event-row ${selectedEvents.includes(event.id) ? 'selected' : ''}`}
                >
                  <td style={{ textAlign: 'center' }}>
                    <Checkbox
                      checked={selectedEvents.includes(event.id)}
                      onChange={() => handleToggleSelect(event.id)}
                    />
                  </td>
                  <td className="text-muted">#{event.id}</td>
                  <td>
                    <div>
                      <div className="event-name">{event.event_name}</div>
                      <div className="event-name-cn">{event.event_name_cn}</div>
                    </div>
                  </td>
                  <td>
                    <div className="game-info">
                      <span>{event.game_name} ({event.gid})</span>
                    </div>
                  </td>
                  <td>
                    {event.category_name ? (
                      <Badge variant="info">
                        {event.category_name}
                      </Badge>
                    ) : (
                      <Badge variant="secondary">
                        未分类
                      </Badge>
                    )}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    <Badge variant="primary">
                      {event.param_count !== undefined ? event.param_count : '-'}
                    </Badge>
                  </td>
                  <td>
                    <div className="action-buttons">
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={() => handleViewEvent(event.id)}
                        title="查看事件详情"
                      >
                        查看
                      </Button>
                      <Button
                        variant="outline-info"
                        size="sm"
                        onClick={() => handleEditEvent(event.id)}
                        title="编辑事件"
                      >
                        编辑
                      </Button>
                      <Button
                        variant="outline-danger"
                        size="sm"
                        onClick={() => handleDeleteEvent(event.id, event.event_name_cn || event.event_name)}
                        title="删除事件"
                      >
                        删除
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {total > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          pageSize={pageSize}
          totalItems={total}
          onPageChange={(page) => {
            setCurrentPage(page);
            navigate(`?page=${page}&per_page=${pageSize}`);
          }}
          onPageSizeChange={(size) => {
            setPageSize(size);
            setCurrentPage(1);
            navigate(`?page=1&per_page=${size}`);
          }}
          pageSizeOptions={[10, 20, 50, 100]}
        />
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
  };

  // Render the component
  return renderContent();
}

// Memoize the component to prevent unnecessary re-renders
const MemoizedEventsList = React.memo(EventsList);

MemoizedEventsList.displayName = 'EventsList';

export default MemoizedEventsList;
