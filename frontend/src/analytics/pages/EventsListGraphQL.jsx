/**
 * EventsListGraphQL - 事件列表页面(GraphQL版本)
 *
 * 完整迁移自EventsList.jsx,保留所有功能:
 * - 分页
 * - 搜索
 * - 分类过滤
 * - 批量选择和删除
 * - 单个事件查看/编辑/删除
 *
 * 使用GraphQL API替代REST API
 */

import { useState, useMemo, useCallback } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';
import React from 'react';
import {
  Button,
  SearchInput,
  Checkbox,
  Badge,
  Spinner,
  useToast,
  SelectGamePrompt,
  Pagination
} from '@shared/ui';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import { useEvents, useSearchEvents, useDeleteEvent } from '@/graphql/hooks';
import './EventsList.css';

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

  // Game context check
  const hasGameContext = !!currentGame;

  // GraphQL queries
  const { data: eventsData, loading: eventsLoading, error: fetchError, refetch } = useEvents(
    currentGame?.gid,
    pageSize,
    (currentPage - 1) * pageSize
  );

  const { data: searchData, loading: searchLoading } = useSearchEvents(
    searchTerm,
    currentGame?.gid
  );

  // GraphQL mutations
  const [deleteEvent] = useDeleteEvent();

  // Get events list
  const events = useMemo(() => {
    if (searchTerm && searchData?.searchEvents) {
      return searchData.searchEvents;
    }
    return eventsData?.events || [];
  }, [eventsData, searchData, searchTerm]);

  // Filter by category (client-side)
  const filteredEvents = useMemo(() => {
    if (!Array.isArray(events)) {
      return [];
    }

    const filtered = events.filter(event => {
      const matchesCategory = selectedCategory === 'all' ||
        event.categoryName?.toLowerCase() === selectedCategory.toLowerCase();
      return matchesCategory;
    });

    console.log('[EventsListGraphQL] Filtered events count:', filtered.length, 'Total events:', events.length);
    return filtered;
  }, [events, selectedCategory]);

  // Get unique categories
  const categories = useMemo(() => {
    if (!Array.isArray(events)) {
      return ['all'];
    }
    return ['all', ...new Set(events.map(e => e.categoryName).filter(Boolean))];
  }, [events]);

  const pageSizeOptions = useMemo(() => [
    { value: '10', label: '10' },
    { value: '20', label: '20' },
    { value: '50', label: '50' },
    { value: '100', label: '100' }
  ], []);

  // Handlers
  const handleViewEvent = useCallback((eventId) => {
    navigate(`/events/${eventId}?game_gid=${currentGame?.gid}`);
  }, [navigate, currentGame?.gid]);

  const handleEditEvent = useCallback((eventId) => {
    navigate(`/events/${eventId}/edit?game_gid=${currentGame?.gid}`);
  }, [navigate, currentGame?.gid]);

  const handleSearchChange = useCallback((value) => {
    console.log('[EventsListGraphQL] Search term changed:', value);
    setSearchTerm(value);
    setCurrentPage(1);
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

  const handleDeleteEvent = useCallback(async (eventId, eventName) => {
    setConfirmState({
      open: true,
      title: '确认删除',
      message: `确定要删除事件「${eventName}」吗？\n\n警告：此操作将同时删除所有关联的参数，且不可恢复！`,
      onConfirm: async () => {
        setConfirmState(s => ({ ...s, open: false }));
        try {
          const result = await deleteEvent({
            variables: { id: eventId }
          });

          if (result.data?.deleteEvent?.ok) {
            success('删除成功');
            refetch();
          } else {
            showError(result.data?.deleteEvent?.errors?.[0] || '删除失败');
          }
        } catch (err) {
          showError(`删除失败: ${err.message}`);
        }
      }
    });
  }, [deleteEvent, success, showError, refetch]);

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
        try {
          // Delete events one by one (GraphQL doesn't have batch delete yet)
          let successCount = 0;
          for (const eventId of selectedEvents) {
            const result = await deleteEvent({
              variables: { id: eventId }
            });
            if (result.data?.deleteEvent?.ok) {
              successCount++;
            }
          }
          success(`成功删除 ${successCount} 个事件`);
          setSelectedEvents([]);
          refetch();
        } catch (err) {
          showError(`删除失败: ${err.message}`);
        }
      }
    });
  }, [selectedEvents, deleteEvent, success, showError, refetch]);

  // Show game selection prompt if no game selected
  if (!hasGameContext) {
    return <SelectGamePrompt message="查看事件列表需要先选择游戏" />;
  }

  // Loading state
  const isLoading = eventsLoading || searchLoading;
  if (isLoading) {
    return (
      <div className="loading-container">
        <Spinner size="lg" label="加载中..." />
      </div>
    );
  }

  // Error state
  if (fetchError) {
    return (
      <div className="error-container">
        <p>加载失败: {fetchError.message}</p>
        <Button variant="primary" onClick={() => refetch()}>重试</Button>
      </div>
    );
  }

  return (
    <div className="events-list-container" data-testid="events-list">
      {/* Header */}
      <div className="page-header">
        <h1>事件列表</h1>
        <p className="text-secondary">游戏: {currentGame?.name} (GraphQL)</p>
      </div>

      {/* Toolbar */}
      <div className="toolbar glass-card">
        <div className="toolbar-left">
          <SearchInput
            placeholder="搜索事件..."
            value={searchTerm}
            onChange={handleSearchChange}
          />
          <select
            className="category-filter"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>
                {cat === 'all' ? '全部分类' : cat}
              </option>
            ))}
          </select>
        </div>
        <div className="toolbar-right">
          {selectedEvents.length > 0 && (
            <Button
              variant="danger"
              onClick={handleBatchDelete}
            >
              删除选中 ({selectedEvents.length})
            </Button>
          )}
        </div>
      </div>

      {/* Events Table */}
      <div className="events-table glass-card">
        <table>
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
            {filteredEvents.length === 0 ? (
              <tr>
                <td colSpan="6" className="empty-state">
                  {searchTerm ? '没有找到匹配的事件' : '暂无事件数据'}
                </td>
              </tr>
            ) : (
              filteredEvents.map(event => (
                <tr key={event.id}>
                  <td>
                    <Checkbox
                      checked={selectedEvents.includes(event.id)}
                      onChange={() => handleToggleSelect(event.id)}
                    />
                  </td>
                  <td>
                    <code>{event.eventName}</code>
                  </td>
                  <td>{event.eventNameCn}</td>
                  <td>
                    {event.categoryName && (
                      <Badge variant="info">{event.categoryName}</Badge>
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
                        onClick={() => handleDeleteEvent(event.id, event.eventNameCn)}
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

      {/* Pagination */}
      {!searchTerm && (
        <div className="pagination-container">
          <Pagination
            currentPage={currentPage}
            totalPages={Math.ceil((eventsData?.totalCount || 0) / pageSize)}
            onPageChange={setCurrentPage}
          />
          <select
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setCurrentPage(1);
            }}
            className="page-size-select"
          >
            {pageSizeOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
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
}

export default EventsListGraphQL;
