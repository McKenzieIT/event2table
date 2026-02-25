/* eslint-disable react-hooks/rules-of-hooks */
import { useState, useMemo, useCallback } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';
import React from 'react';
import { useQuery, useMutation } from '@apollo/client';
import {
  Button,
  Input,
  SearchInput,
  Checkbox,
  Select,
  Badge,
  Spinner,
  useToast,
  SelectGamePrompt
} from '@shared/ui';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import { GET_EVENTS, GET_CATEGORIES } from '@/graphql/queries';
import { DELETE_EVENT } from '@/graphql/mutations';
import './EventsList.css';

/**
 * EventsList Page (GraphQL Version)
 *
 * 已迁移到GraphQL:
 * - 使用Apollo Client替代React Query + fetch
 * - 使用GraphQL查询GET_EVENTS
 * - 使用GraphQL变更DELETE_EVENT
 * - 自动类型检查（通过GraphQL Code Generator）
 */
function EventsListGraphQL() {
  const navigate = useNavigate();
  const { currentGame } = useOutletContext();
  const { success, error: showError } = useToast();

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedEvents, setSelectedEvents] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [confirmState, setConfirmState] = useState({ open: false, onConfirm: () => {}, title: '', message: '' });
  const [pageSize, setPageSize] = useState(10);

  // Game context check - render prompt if no game selected
  const hasGameContext = !!currentGame;

  // Fetch events list using GraphQL
  const { data, loading: isLoading, error: fetchError, refetch } = useQuery(GET_EVENTS, {
    variables: {
      gameGid: currentGame?.gid,
      category: selectedCategory === 'all' ? null : selectedCategory,
      limit: pageSize,
      offset: (currentPage - 1) * pageSize
    },
    skip: !hasGameContext,
    fetchPolicy: 'cache-and-network',
    pollInterval: 60000, // 每分钟轮询一次
  });

  // Fetch categories using GraphQL
  const { data: categoriesData } = useQuery(GET_CATEGORIES, {
    variables: { limit: 100, offset: 0 },
    fetchPolicy: 'cache-first',
  });

  // Delete event mutation
  const [deleteEvent] = useMutation(DELETE_EVENT, {
    onCompleted: (data) => {
      if (data.deleteEvent.ok) {
        success(`成功删除事件`);
        setSelectedEvents([]);
        // Refetch events after deletion
        refetch();
      } else {
        showError(`删除失败: ${data.deleteEvent.errors?.join(', ') || '未知错误'}`);
      }
    },
    onError: (err) => {
      showError(`删除失败: ${err.message}`);
    }
  });

  // Use placeholder data when no game is selected
  const events = hasGameContext ? (data?.events || []) : [];
  const categories = useMemo(() => {
    const cats = categoriesData?.categories || [];
    return ['all', ...cats.map(c => c.name).filter(Boolean)];
  }, [categoriesData]);

  // Filter events by search term (client-side filtering for search)
  const filteredEvents = useMemo(() => {
    if (!searchTerm) return events;

    return events.filter(event => {
      const matchesSearch = !searchTerm ||
        event.eventName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        event.eventNameCn?.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesSearch;
    });
  }, [events, searchTerm]);

  const pageSizeOptions = useMemo(() => [
    { value: '10', label: '10' },
    { value: '20', label: '20' },
    { value: '50', label: '50' },
    { value: '100', label: '100' }
  ], []);

  // Callbacks
  const handleViewEvent = useCallback((eventId) => {
    navigate(`/events/${eventId}?game_gid=${currentGame?.gid}`);
  }, [navigate, currentGame?.gid]);

  const handleEditEvent = useCallback((eventId) => {
    navigate(`/events/${eventId}/edit?game_gid=${currentGame?.gid}`);
  }, [navigate, currentGame?.gid]);

  const handleSearchChange = useCallback((value) => {
    setSearchTerm(value);
    setCurrentPage(1); // Reset to first page on search
  }, []);

  const handleToggleSelect = useCallback((eventId) => {
    setSelectedEvents(prev => {
      if (prev.includes(eventId)) {
        return prev.filter(id => id !== eventId);
      } else {
        return [...prev, eventId];
      }
    });
  }, []);

  const handleSelectAll = useCallback(() => {
    setSelectedEvents(prev => {
      if (prev.length === filteredEvents.length) {
        return [];
      } else {
        return filteredEvents.map(e => e.id);
      }
    });
  }, [filteredEvents]);

  const handleBatchDelete = useCallback(() => {
    if (selectedEvents.length === 0) {
      showError('请先选择要删除的事件');
      return;
    }
    setConfirmState({
      open: true,
      title: '确认批量删除',
      message: `确定要删除选中的 ${selectedEvents.length} 个事件吗？\n\n警告：此操作将同时删除所有关联的参数，且不可恢复！`,
      onConfirm: async () => {
        setConfirmState(s => ({ ...s, open: false }));
        // Delete events one by one (GraphQL doesn't have batch delete)
        for (const eventId of selectedEvents) {
          await deleteEvent({ variables: { id: eventId } });
        }
      }
    });
  }, [selectedEvents.length, deleteEvent, showError]);

  const handleDeleteEvent = useCallback((eventId, eventName) => {
    setConfirmState({
      open: true,
      title: '确认删除',
      message: `确定要删除事件「${eventName}」吗？\n\n警告：此操作将同时删除所有关联的参数，且不可恢复！`,
      onConfirm: () => {
        setConfirmState(s => ({ ...s, open: false }));
        deleteEvent({ variables: { id: eventId } });
      }
    });
  }, [deleteEvent]);

  const handleClearSelection = useCallback(() => {
    setSelectedEvents([]);
  }, []);

  // Pagination
  const total = filteredEvents.length;
  const totalPages = Math.ceil(total / pageSize);

  // Always render content
  const renderContent = () => {
    if (!hasGameContext) {
      return <SelectGamePrompt message="查看事件列表需要先选择游戏" />;
    }

    if (fetchError) {
      return (
        <div className="events-list-page">
          <div className="error-message">
            <p>加载事件列表失败: {fetchError.message}</p>
            <Button variant="primary" onClick={() => refetch()}>
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
              <h1>日志事件管理 (GraphQL版本)</h1>
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

        {/* Statistics Cards */}
        <div className="stats-container">
          <div className="stat-card">
            <div className="stat-value">{total}</div>
            <div className="stat-label">
              <span>总事件数</span>
            </div>
          </div>
          <div className="stat-card purple">
            <div className="stat-value">
              {events.filter(e => e.categoryName).length}
            </div>
            <div className="stat-label">
              <span>已分类</span>
            </div>
          </div>
          <div className="stat-card orange">
            <div className="stat-value">
              {events.filter(e => !e.categoryName).length}
            </div>
            <div className="stat-label">
              <span>未分类</span>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="filters-container">
          <div className="filters-left">
            <SearchInput
              placeholder="搜索事件名称..."
              value={searchTerm}
              onChange={handleSearchChange}
              className="search-input"
            />
            <Select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setCurrentPage(1);
              }}
              options={categories.map(cat => ({
                value: cat,
                label: cat === 'all' ? '全部分类' : cat
              }))}
              className="category-select"
            />
          </div>
          <div className="filters-right">
            <Select
              value={pageSize.toString()}
              onChange={(e) => {
                setPageSize(parseInt(e.target.value));
                setCurrentPage(1);
              }}
              options={pageSizeOptions}
              className="page-size-select"
            />
          </div>
        </div>

        {/* Events Table */}
        {isLoading ? (
          <div className="loading-container">
            <Spinner size="lg" label="加载中..." />
          </div>
        ) : (
          <>
            <div className="events-table-container">
              <table className="events-table">
                <thead>
                  <tr>
                    <th>
                      <Checkbox
                        checked={selectedEvents.length === filteredEvents.length && filteredEvents.length > 0}
                        onChange={handleSelectAll}
                      />
                    </th>
                    <th>事件名称</th>
                    <th>中文名称</th>
                    <th>分类</th>
                    <th>参数数量</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredEvents.map(event => (
                    <tr key={event.id}>
                      <td>
                        <Checkbox
                          checked={selectedEvents.includes(event.id)}
                          onChange={() => handleToggleSelect(event.id)}
                        />
                      </td>
                      <td>
                        <span
                          className="event-name-link"
                          onClick={() => handleViewEvent(event.id)}
                        >
                          {event.eventName}
                        </span>
                      </td>
                      <td>{event.eventNameCn || '-'}</td>
                      <td>
                        {event.categoryName ? (
                          <Badge variant="primary">{event.categoryName}</Badge>
                        ) : (
                          <Badge variant="secondary">未分类</Badge>
                        )}
                      </td>
                      <td>{event.paramCount || 0}</td>
                      <td>
                        <div className="action-buttons">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            onClick={() => handleViewEvent(event.id)}
                          >
                            查看
                          </Button>
                          <Button
                            variant="outline-secondary"
                            size="sm"
                            onClick={() => handleEditEvent(event.id)}
                          >
                            编辑
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleDeleteEvent(event.id, event.eventName)}
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

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="pagination-container">
                <Button
                  variant="outline-secondary"
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage(p => p - 1)}
                >
                  上一页
                </Button>
                <span className="page-info">
                  第 {currentPage} / {totalPages} 页
                </span>
                <Button
                  variant="outline-secondary"
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage(p => p + 1)}
                >
                  下一页
                </Button>
              </div>
            )}
          </>
        )}

        {/* Confirm Dialog */}
        <ConfirmDialog
          isOpen={confirmState.open}
          onClose={() => setConfirmState(s => ({ ...s, open: false }))}
          onConfirm={confirmState.onConfirm}
          title={confirmState.title}
          message={confirmState.message}
        />
      </div>
    );
  };

  return renderContent();
}

export default EventsListGraphQL;
