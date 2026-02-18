/**
 * WhereBuilderCanvas Component
 * WHERE条件构建器画布（支持拖拽、性能优化）
 */
import React, { useState, useMemo, useCallback } from 'react';
import { DndContext, closestCenter } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { arrayMove } from '@dnd-kit/sortable';
import WhereConditionItem from './WhereConditionItem';
import './WhereBuilderCanvas.css';

// 虚拟渲染阈值（使用CSS优化而非react-window）
const LARGE_LIST_THRESHOLD = 50;

export default function WhereBuilderCanvas({
  conditions,
  canvasFields,
  selectedEvent,
  onUpdate
}) {
  const [activeId, setActiveId] = useState(null);

  // 处理拖拽结束
  const handleDragEnd = useCallback((event) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = conditions.findIndex(c => c.id === active.id);
      const newIndex = conditions.findIndex(c => c.id === over.id);
      const reordered = arrayMove(conditions, oldIndex, newIndex);
      onUpdate(reordered);
    }
    setActiveId(null);
  }, [conditions, onUpdate]);

  // 添加条件
  const handleAddCondition = useCallback(() => {
    onUpdate([
      ...conditions,
      {
        id: `where-${Date.now()}`,
        type: 'condition',
        field: '',
        operator: '=',
        value: '',
        logicalOp: conditions.length > 0 ? 'AND' : undefined
      }
    ]);
  }, [conditions, onUpdate]);

  // 添加分组
  const handleAddGroup = useCallback(() => {
    const newGroup = {
      id: `group-${Date.now()}`,
      type: 'group',
      logicalOp: 'AND',
      children: [],
      isCollapsed: false
    };

    onUpdate([
      ...conditions,
      {
        ...newGroup,
        logicalOp: conditions.length > 0 ? 'AND' : undefined
      }
    ]);
  }, [conditions, onUpdate]);

  // 判断是否使用性能模式
  const isLargeList = conditions.length > LARGE_LIST_THRESHOLD;

  // 使用useMemo缓存条件列表渲染，避免不必要的重渲染
  const conditionsList = useMemo(() => {
    return conditions.map((condition, index) => (
      <WhereConditionItem
        key={condition.id}
        condition={condition}
        index={index}
        isFirst={index === 0}
        canvasFields={canvasFields}
        selectedEvent={selectedEvent}
        onUpdate={(id, updates) => {
          const updated = conditions.map(c =>
            c.id === id ? { ...c, ...updates } : c
          );
          onUpdate(updated);
        }}
        onDelete={(id) => {
          const filtered = conditions.filter(c => c.id !== id);
          onUpdate(filtered);
        }}
      />
    ));
  }, [conditions, onUpdate, canvasFields, selectedEvent]);

  return (
    <div className="where-builder-canvas">
      {/* 工具栏 */}
      <div className="where-toolbar">
        <button className="btn btn-sm btn-primary" onClick={handleAddCondition}>
          <i className="bi bi-plus-circle"></i> 添加条件
        </button>
        <button className="btn btn-sm btn-secondary" onClick={handleAddGroup}>
          <i className="bi bi-layer-group"></i> 添加分组
        </button>
        <button className="btn btn-sm btn-outline-danger" onClick={() => onUpdate([])}>
          <i className="bi bi-trash"></i> 清空
        </button>
        {isLargeList && (
          <span className="badge badge-info ml-2">
            性能优化: {conditions.length} 个条件
          </span>
        )}
      </div>

      {/* 条件列表 */}
      {conditions.length === 0 ? (
        <div className="where-empty-state">
          <i className="bi bi-inbox"></i>
          <p>暂无WHERE条件</p>
          <button className="btn btn-primary" onClick={handleAddCondition}>
            添加第一个条件
          </button>
        </div>
      ) : (
        <DndContext
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={conditions.map(c => c.id)}
            strategy={verticalListSortingStrategy}
          >
            <div className={isLargeList ? 'where-conditions-list large-list' : 'where-conditions-list'}>
              {conditionsList}
            </div>
          </SortableContext>
        </DndContext>
      )}
    </div>
  );
}
