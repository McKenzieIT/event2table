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
 *
 * @component FieldEventSelector
 */

import React, { useState, useMemo, useRef } from 'react';
import { useDraggable } from '@dnd-kit/core';
import './FieldEventSelector.css';

/**
 * Draggable event item component
 */
function DraggableEventItem({ event, isSelected, onSelect }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    isDragging
  } = useDraggable({
    id: `event-${event.id}`,
    data: {
      type: 'event',
      event: event
    }
  });

  const style = transform ? {
    transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`,
    opacity: isDragging ? 0.5 : 1,
    cursor: 'grab'
  } : undefined;

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
}) {
  return (
    <div className="category-section">
      <div
        className="category-header"
        onClick={onToggle}
        tabIndex={0}
        role="button"
        aria-label={`切换${category || '未分类'}分类`}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            onToggle();
          }
        }}
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
 *
 * @param {Object} props - Component props
 * @param {Array} props.events - Array of events to display
 * @param {number|null} props.selectedEventId - Currently selected event ID
 * @param {Function} props.onEventSelect - Callback when an event is selected
 */
export default function FieldEventSelector({
  events,
  selectedEventId,
  onEventSelect
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCategories, setExpandedCategories] = useState(new Set());
  const searchDebounceRef = useRef(null);

  // Group events by category
  const eventsByCategory = useMemo(() => {
    const grouped = {};

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
    const filtered = {};

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
  const toggleCategory = (category) => {
    setExpandedCategories(prev => {
      const newSet = new Set(prev);
      if (newSet.has(category)) {
        newSet.delete(category);
      } else {
        newSet.add(category);
      }
      return newSet;
    });
  };

  // Expand/collapse all categories
  const expandAll = () => {
    setExpandedCategories(new Set(Object.keys(filteredCategories)));
  };

  const collapseAll = () => {
    setExpandedCategories(new Set());
  };

  // Clear search
  const clearSearch = () => {
    setSearchQuery('');
  };

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
          <input
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
          >
            <i className="bi bi-chevron-down"></i>
            展开
          </button>
          <button
            className="btn-link btn-sm"
            onClick={collapseAll}
          >
            <i className="bi bi-chevron-right"></i>
            收起
          </button>
        </div>
      )}

      {/* Event List */}
      <div className="event-selector-content">
        {totalEventCount === 0 ? (
          <div className="empty-state">
            <i className="bi bi-inbox"></i>
            <p>暂无事件</p>
          </div>
        ) : categoryCount === 0 ? (
          <div className="empty-state">
            <i className="bi bi-search"></i>
            <p>未找到匹配的事件</p>
          </div>
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
