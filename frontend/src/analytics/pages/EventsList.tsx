// ⚡️ REACT PERF: Refactored component architecture + performanceMonitor
// ✅ Performance: Modular components with React.memo optimization
// - Extracted sub-components for better maintainability
// - Preserved all React.memo, useCallback, useMemo optimizations
// - Each component file < 500 lines

import React, { useState, useCallback } from 'react';
import { useNavigate, useOutletContext } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { useToast } from '@shared/ui';
import { usePerformanceMonitor } from '@/shared/utils/performanceMonitor';
import { SelectGamePrompt, Pagination, ConfirmDialog } from '@shared/ui';
import { BatchEditModal } from '@features/events/components/BatchEditModal';
import { BatchValidateModal } from '@features/events/components/BatchValidateModal';
import './EventsList.css';
import './VirtualTable.css';

// 导入类型和子组件
import { LayoutContext, ConfirmState } from './components/EventsList/types';
import { useEventsList } from './components/EventsList/hooks';
import EventsListHeader from './components/EventsList/EventsListHeader';
import EventsStats from './components/EventsList/EventsStats';
import EventsFilters from './components/EventsList/EventsFilters';
import EventsVirtualTable from './components/EventsList/EventsVirtualTable';

/**
 * EventsList 主组件
 * 重构后的模块化组件，职责清晰，易于维护
 */
function EventsList() {
  // ⚡️ Performance monitoring
  usePerformanceMonitor('EventsList', 16.67); // 60fps threshold

  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { currentGame } = useOutletContext<LayoutContext>();
  const { success, error: showError } = useToast();

  // ========== 状态管理 ==========

  const [confirmState, setConfirmState] = useState<ConfirmState>({
    open: false,
    onConfirm: () => {},
    title: '',
    message: ''
  });
  
  const [showBatchEditModal, setShowBatchEditModal] = useState<boolean>(false);
  const [showBatchValidateModal, setShowBatchValidateModal] = useState<boolean>(false);

  // ========== 使用自定义 Hook ==========

  const {
    searchTerm,
    selectedCategory,
    selectedEvents,
    currentPage,
    pageSize,
    hasGameContext,
    isLoading,
    fetchError,
    filteredEvents,
    categories,
    pagination,
    totalPages,
    total,
    effectiveData,
    handleViewEvent,
    handleEditEvent,
    handleSearchChange,
    handleToggleSelect,
    handleSelectAll,
    handleBatchDelete,
    handleDeleteEvent,
    handleClearSelection,
    handlePageChange,
    handlePageSizeChange,
    setSelectedCategory,
    deleteMutation
  } = useEventsList(currentGame);

  // ========== 批量操作处理器 ==========

  const handleBatchEdit = useCallback(() => {
    setShowBatchEditModal(true);
  }, []);

  const handleBatchValidate = useCallback(() => {
    setShowBatchValidateModal(true);
  }, []);

  const handleConfirmBatchDelete = useCallback(() => {
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

  const handleConfirmDeleteEvent = useCallback((eventId: number, eventName: string) => {
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

  // ========== 导航处理器 ==========

  const handleCreateEvent = useCallback(() => {
    navigate(`/events/create?game_gid=${currentGame?.gid}`);
  }, [navigate, currentGame?.gid]);

  const handleImportEvents = useCallback(() => {
    navigate('/import-events');
  }, [navigate]);

  const handleRetryLoad = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: ['events', currentGame?.gid]
    });
  }, [queryClient, currentGame?.gid]);

  // ========== 统计数据 ==========

  const categorizedCount = React.useMemo(() => {
    return effectiveData?.events ? effectiveData.events.filter(e => e.category_name).length : 0;
  }, [effectiveData]);

  const uncategorizedCount = React.useMemo(() => {
    return effectiveData?.events ? effectiveData.events.filter(e => !e.category_name).length : 0;
  }, [effectiveData]);

  // ========== 渲染逻辑 ==========

  // 如果没有游戏上下文，显示游戏选择提示
  if (!hasGameContext) {
    return <SelectGamePrompt message="查看事件列表需要先选择游戏" />;
  }

  // 如果有错误，显示错误状态
  if (fetchError) {
    return (
      <div className="events-list-page">
        <div className="error-message">
          <p>加载事件列表失败: {fetchError.message}</p>
          <ConfirmDialog
            open={true}
            title="加载失败"
            message={`无法加载事件列表：${fetchError.message}`}
            confirmText="重新加载"
            cancelText="取消"
            variant="danger"
            onConfirm={handleRetryLoad}
            onCancel={() => {}}
          />
        </div>
      </div>
    );
  }

  // 正常渲染主内容
  return (
    <div className="events-list-page">
      {/* 页面头部 */}
      <EventsListHeader
        selectedCount={selectedEvents.length}
        onBatchEdit={handleBatchEdit}
        onBatchValidate={handleBatchValidate}
        onBatchDelete={handleConfirmBatchDelete}
        onCreateEvent={handleCreateEvent}
        onImportEvents={handleImportEvents}
      />

      {/* 统计卡片 */}
      <EventsStats
        total={total}
        categorizedCount={categorizedCount}
        uncategorizedCount={uncategorizedCount}
      />

      {/* 筛选栏 */}
      <EventsFilters
        searchTerm={searchTerm}
        onSearchChange={handleSearchChange}
        selectedCount={selectedEvents.length}
        totalCount={filteredEvents.length}
        onSelectAll={handleSelectAll}
        onClearSelection={handleClearSelection}
      />

      {/* 事件表格 */}
      <EventsVirtualTable
        events={filteredEvents}
        selectedEvents={selectedEvents}
        onToggleSelect={handleToggleSelect}
        onViewEvent={handleViewEvent}
        onEditEvent={handleEditEvent}
        onDeleteEvent={handleConfirmDeleteEvent}
        isLoading={isLoading}
      />

      {/* 分页 */}
      {total > 0 && (
        <Pagination
          currentPage={currentPage}
          totalPages={totalPages}
          pageSize={pageSize}
          totalItems={total}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          pageSizeOptions={[10, 20, 50, 100]}
        />
      )}

      {/* 确认对话框 */}
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

      {/* 批量编辑模态框 */}
      <BatchEditModal
        isOpen={showBatchEditModal}
        onClose={() => setShowBatchEditModal(false)}
        selectedEvents={filteredEvents.filter(e => selectedEvents.includes(e.id)).map(e => ({
          id: e.id,
          event_name: e.event_name,
          event_name_cn: e.event_name_cn,
          gameGid: e.gid,
          category_id: e.category_id,
          category_name: e.category_name
        }))}
        categoryOptions={categories
          .filter(c => c !== 'all')
          .map(c => ({ value: parseInt(c), label: c }))}
        onSuccess={() => {
          queryClient.invalidateQueries({ queryKey: ['events', currentGame?.gid] });
          handleClearSelection();
        }}
      />

      {/* 批量验证模态框 */}
      <BatchValidateModal
        isOpen={showBatchValidateModal}
        onClose={() => setShowBatchValidateModal(false)}
        selectedEvents={filteredEvents.filter(e => selectedEvents.includes(e.id)).map(e => ({
          id: e.id,
          event_name: e.event_name,
          event_name_cn: e.event_name_cn,
          gameGid: e.gid,
          category_id: e.category_id,
          category_name: e.category_name
        }))}
      />
    </div>
  );
}

// 使用React.memo防止不必要的重新渲染
const MemoizedEventsList = React.memo(EventsList);

MemoizedEventsList.displayName = 'EventsList';

export default MemoizedEventsList;
