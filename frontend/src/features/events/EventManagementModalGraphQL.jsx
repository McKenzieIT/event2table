/**
 * EventManagementModalGraphQL - 事件管理模态框（GraphQL版本）
 *
 * 使用GraphQL API替代REST API
 * 利用GraphQL的灵活性优化数据获取
 */

import React, { useState, useMemo, useCallback } from 'react';
import { BaseModal, Button, Input, Select, useToast, SearchInput, Skeleton } from '@shared/ui';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import {
  useEvents,
  useSearchEvents,
  useUpdateEvent,
  useDeleteEvent,
} from '../../graphql/hooks';
import './EventManagementModal.css';

const EventManagementModalGraphQL = ({ isOpen, onClose, gameGid }) => {
  const { success, error: showError } = useToast();

  // Local state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEventId, setSelectedEventId] = useState(null);
  const [editingEvent, setEditingEvent] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [confirmState, setConfirmState] = useState({
    open: false,
    type: null,
    data: null,
    title: '',
    message: ''
  });

  // GraphQL Hooks
  const { data: eventsData, loading: isLoading, error } = useEvents(gameGid, 100, 0);
  const { data: searchData, loading: isSearching } = useSearchEvents(searchTerm, gameGid);

  // Mutations
  const [updateEvent] = useUpdateEvent();
  const [deleteEvent] = useDeleteEvent();

  // Get events list
  const events = useMemo(() => {
    if (searchTerm && searchData?.searchEvents) {
      return searchData.searchEvents;
    }
    return eventsData?.events || [];
  }, [eventsData, searchData, searchTerm]);

  // Filter events based on search term (client-side fallback)
  const filteredEvents = useMemo(() => {
    if (!events.length) return [];
    if (searchTerm && searchData?.searchEvents) {
      return events; // Already filtered by GraphQL
    }
    return events.filter(event =>
      event.eventName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.eventNameCn?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [events, searchTerm, searchData]);

  // Handle event selection
  const handleSelectEvent = useCallback((event) => {
    setSelectedEventId(event.id);
    setEditingEvent({ ...event });
    setHasChanges(false);
  }, []);

  // Handle event edit
  const handleEditEvent = useCallback((field, value) => {
    setEditingEvent(prev => ({
      ...prev,
      [field]: value
    }));
    setHasChanges(true);
  }, []);

  // Handle save event
  const handleSaveEvent = useCallback(async () => {
    if (!editingEvent || !hasChanges) return;

    try {
      const { data } = await updateEvent({
        variables: {
          id: editingEvent.id,
          eventNameCn: editingEvent.eventNameCn,
          categoryId: editingEvent.categoryId,
          includeInCommonParams: editingEvent.includeInCommonParams
        }
      });

      if (data?.updateEvent?.ok) {
        success('事件更新成功');
        setHasChanges(false);
      } else {
        showError(data?.updateEvent?.errors?.[0] || '更新失败');
      }
    } catch (err) {
      showError(`更新失败: ${err.message}`);
    }
  }, [editingEvent, hasChanges, updateEvent, success, showError]);

  // Handle delete event
  const handleDeleteEvent = useCallback(async (id) => {
    try {
      const { data } = await deleteEvent({
        variables: { id }
      });

      if (data?.deleteEvent?.ok) {
        success('事件删除成功');
        setSelectedEventId(null);
        setEditingEvent(null);
      } else {
        showError(data?.deleteEvent?.errors?.[0] || '删除失败');
      }
    } catch (err) {
      showError(`删除失败: ${err.message}`);
    }
  }, [deleteEvent, success, showError]);

  // Render loading state
  if (isLoading) {
    return (
      <BaseModal isOpen={isOpen} onClose={onClose} title="事件管理" size="lg">
        <div className="event-management-loading">
          <Skeleton height={40} count={5} />
        </div>
      </BaseModal>
    );
  }

  // Render error state
  if (error) {
    return (
      <BaseModal isOpen={isOpen} onClose={onClose} title="事件管理" size="lg">
        <div className="event-management-error">
          <p>加载失败: {error.message}</p>
          <Button onClick={() => window.location.reload()}>重试</Button>
        </div>
      </BaseModal>
    );
  }

  return (
    <>
      <BaseModal isOpen={isOpen} onClose={onClose} title="事件管理" size="lg">
        <div className="event-management-container">
          {/* Header */}
          <div className="event-management-header">
            <div className="header-left">
              <SearchInput
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="搜索事件名称..."
                loading={isSearching}
              />
            </div>
            <div className="header-right">
              <Button variant="primary">
                + 添加事件
              </Button>
            </div>
          </div>

          {/* Main content */}
          <div className="event-management-content">
            {/* Left: Events list */}
            <div className="events-list">
              <div className="events-list-header">
                <span>事件列表 ({filteredEvents.length})</span>
              </div>
              <div className="events-list-body">
                {filteredEvents.map(event => (
                  <div
                    key={event.id}
                    className={`event-item ${selectedEventId === event.id ? 'selected' : ''}`}
                    onClick={() => handleSelectEvent(event)}
                  >
                    <div className="event-info">
                      <div className="event-name">{event.eventName}</div>
                      <div className="event-name-cn">{event.eventNameCn}</div>
                      <div className="event-meta">
                        分类: {event.categoryName} | 参数: {event.paramCount || 0}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: Event details */}
            <div className="event-details">
              {selectedEventId && editingEvent ? (
                <>
                  <div className="details-header">
                    <h3>事件详情</h3>
                    <div className="details-actions">
                      {hasChanges && (
                        <Button onClick={handleSaveEvent} variant="primary" size="sm">
                          保存
                        </Button>
                      )}
                      <Button
                        onClick={() => handleDeleteEvent(editingEvent.id)}
                        variant="danger"
                        size="sm"
                      >
                        删除
                      </Button>
                    </div>
                  </div>
                  <div className="details-body">
                    <Input
                      label="ID"
                      value={editingEvent.id}
                      disabled
                    />
                    <Input
                      label="事件名称（英文）"
                      value={editingEvent.eventName}
                      disabled
                    />
                    <Input
                      label="事件名称（中文）"
                      value={editingEvent.eventNameCn}
                      onChange={(e) => handleEditEvent('eventNameCn', e.target.value)}
                    />
                    <Input
                      label="分类"
                      value={editingEvent.categoryName}
                      disabled
                    />
                    <Input
                      label="参数数量"
                      value={editingEvent.paramCount || 0}
                      disabled
                    />
                    <Input
                      label="源表"
                      value={editingEvent.sourceTable || '-'}
                      disabled
                    />
                    <Input
                      label="目标表"
                      value={editingEvent.targetTable || '-'}
                      disabled
                    />
                  </div>
                </>
              ) : (
                <div className="no-selection">
                  <p>请从左侧列表选择一个事件</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </BaseModal>

      {/* Confirm Dialog */}
      <ConfirmDialog
        isOpen={confirmState.open}
        onClose={() => setConfirmState({ open: false, type: null, data: null, title: '', message: '' })}
        onConfirm={() => {}}
        title={confirmState.title}
        message={confirmState.message}
        confirmText="确认"
        cancelText="取消"
      />
    </>
  );
};

export default EventManagementModalGraphQL;
