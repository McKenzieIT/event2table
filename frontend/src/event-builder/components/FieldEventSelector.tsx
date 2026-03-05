// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * FieldEventSelector Component
 *
 * Displays a list of events with drag-and-drop support for the Field Builder.
 * Events can be dragged to the field canvas for parameter extraction.
 *
 * Features:
 * - Search/filter events by name or category
 * - Group events by category
 * - Collapsible category sections
 * - Draggable event items with visual feedback
 * - Selected state highlighting
 */

import React, { useState, useMemo, useRef, useCallback } from 'react';
import { useDraggable, UseDraggableArguments } from '@dnd-kit/core';
import { Input, EmptyState } from '@shared/ui';
import './FieldEventSelector.css';

/**
 * 事件接口
 */
export interface FieldEvent {
  id: number;
  name: string;
  description: string;
  category?: string;
}

/**
 * 组件Props接口
 */
export interface FieldEventSelectorProps {
  events: FieldEvent[];
  selectedEventId: number | null;
  onEventSelect: (eventId: number) => void;
}

/**
 * Draggable event item props
 */
interface DraggableEventItemProps {
  event: FieldEvent;
  isSelected: boolean;
  onSelect: (eventId: number) => void;
}

/**
 * Category section props
 */
interface CategorySectionProps {
  category: string;
  events: FieldEvent[];
  selectedEventId: number | null;
  onEventSelect: (eventId: number) => void;
  isExpanded: boolean;
  onToggle: () => void;
}

/**
 * Draggable event item component
 */
function DraggableEventItem({ event, isSelected, onSelect }: DraggableEventItemProps) {
  const draggableArgs: UseDraggableArguments = {
    id: `event-${event.id}`,
    data: {
      type: 'event',
      event: event
    }
  };

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging
  } = useDraggable(draggableArgs);

  const style: React.CSSProperties = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    opacity: isDragging ? 0.5 : 1,
    cursor: 'grab'
  } : {};

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={`event-item ${isSelected ? 'selected' : ''} ${isDragging ? 'dragging' : ''}`}
      onClick={() => onSelect(event.id)}
    >
      <div className="event-info">
        <strong>{event.name}</strong>
        <span className="event-description">{event.description}</span>
      </div>
      {isSelected && (
        <i className="bi bi-check-circle text-success"></i>
      )}
    </div>
  );
}

/**
 * Collapsible category section component
 */
function CategorySection({
  category,
  events,
  selectedEventId,
  onEventSelect,
  isExpanded,
  onToggle
}: CategorySectionProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onToggle();
    }
  };

  return (
    <div className="category-section">
      <div
        className="category-header"
        onClick={onToggle}
        tabIndex={0}
        role="button"
        aria-label={`切换${category || '未分类'}分类`}
        onKeyDown={handleKeyDown}
      >
        <div className="category-info">
          <i className={`bi bi-chevron-${isExpanded ? 'down' : 'right'}`}></i>
          <span className="category-name">{category || '未分类'}</span>
        </div>
        <span className="badge badge-secondary">{events.length}</span>
      </div>
      {isExpanded && (
        <div className="category-events">
          {events.map(event => (
            <DraggableEventItem
              key={event.id}
              event={event}
              isSelected={selectedEventId === event.id}
              onSelect={onEventSelect}
            />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Main FieldEventSelector component
 */
export default function FieldEventSelector({
  events,
  selectedEventId,
  onEventSelect
}: FieldEventSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const searchDebounceRef = useRef<NodeJS.Timeout | null>(null);

  // Group events by category
  const eventsByCategory = useMemo(() => {
    const grouped: Record<string, FieldEvent[]> = {};

    events.forEach(event => {
      const category = event.category || '未分类';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(event);
    });

    // Sort events within each category by name
    Object.keys(grouped).forEach(category => {
      grouped[category].sort((a, b) => a.name.localeCompare(b.name));
    });

    return grouped;
  }, [events]);

  // Filter events based on search query
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) {
      return eventsByCategory;
    }

    const query = searchQuery.toLowerCase();
    const filtered: Record<string, FieldEvent[]> = {};

    Object.entries(eventsByCategory).forEach(([category, categoryEvents]) => {
      const matchingEvents = categoryEvents.filter(event =>
        event.name.toLowerCase().includes(query) ||
        event.description.toLowerCase().includes(query) ||
        category.toLowerCase().includes(query)
      );

      if (matchingEvents.length > 0) {
        filtered[category] = matchingEvents;
      }
    });

    return filtered;
  }, [eventsByCategory, searchQuery]);

  // Toggle category expansion
  const toggleCategory = useCallback((category: string) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(category)) {
        newSet.delete(category);
      } else {
        newSet.add(category);
      }
      return newSet;
    });
  }, []);

  // Expand/collapse all categories
  const expandAll = useCallback(() => {
    setExpandedCategories(new Set(Object.keys(filteredCategories)));
  }, [filteredCategories]);

  const collapseAll = useCallback(() => {
    setExpandedCategories(new Set());
  }, []);

  // Clear search
  const clearSearch = useCallback(() => {
    setSearchQuery('');
  }, []);

  const categoryCount = Object.keys(filteredCategories).length;
  const totalEventCount = events.length;

  return (
    <div className="field-event-selector">
      {/* Header */}
      <div className="event-selector-header">
        <h3>
          <i className="bi bi-diagram-3"></i>
          事件列表
        </h3>
        {totalEventCount > 0 && (
          <span className="badge badge-secondary">{totalEventCount}</span>
        )}
      </div>

      {/* Search */}
      <div className="event-selector-search">
        <div className="search-input-wrapper">
          <i className="bi bi-search search-icon"></i>
          <Input
            type="text"
            className="search-input"
            placeholder="搜索事件名称或分类..."
            value={searchQuery}
            onChange={(e) => {
              const value = e.target.value;
              if (searchDebounceRef.current) {
                clearTimeout(searchDebounceRef.current);
              }
              searchDebounceRef.current = setTimeout(() => {
                setSearchQuery(value);
              }, 300);
            }}
          />
          {searchQuery && (
            <button
              className="search-clear"
              onClick={clearSearch}
              aria-label="清除搜索"
              type="button"
            >
              <i className="bi bi-x"></i>
            </button>
          )}
        </div>
      </div>

      {/* Category Actions */}
      {categoryCount > 1 && (
        <div className="category-actions">
          <button
            className="btn-link btn-sm"
            onClick={expandAll}
            type="button"
          >
            <i className="bi bi-chevron-down"></i>
            展开
          </button>
          <button
            className="btn-link btn-sm"
            onClick={collapseAll}
            type="button"
          >
            <i className="bi bi-chevron-right"></i>
            收起
          </button>
        </div>
      )}

      {/* Event List */}
      <div className="event-selector-content">
        {totalEventCount === 0 ? (
          <EmptyState
            icon={<i className="bi bi-inbox" style={{ fontSize: '48px' }} />}
            title="暂无事件"
          />
        ) : categoryCount === 0 ? (
          <EmptyState
            icon={<i className="bi bi-search" style={{ fontSize: '48px' }} />}
            title="未找到匹配的事件"
          />
        ) : (
          <div className="event-list">
            {Object.entries(filteredCategories)
              .sort(([a], [b]) => a.localeCompare(b))
              .map(([category, categoryEvents]) => (
                <CategorySection
                  key={category}
                  category={category}
                  events={categoryEvents}
                  selectedEventId={selectedEventId}
                  onEventSelect={onEventSelect}
                  isExpanded={expandedCategories.has(category)}
                  onToggle={() => toggleCategory(category)}
                />
              ))}
          </div>
        )}
      </div>
    </div>
  );
}
