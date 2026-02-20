/**
 * MultiEventConfigV2 - 多事件配置UI组件
 *
 * 功能：
 * - 选择多个事件
 * - 配置JOIN条件
 * - 配置UNION字段映射
 * - 支持拖拽排序
 */

import React, { useState } from 'react';
import toast from 'react-hot-toast';
import './MultiEventConfigV2.css';

export default function MultiEventConfigV2({
  availableEvents = [],
  selectedEvents = [],
  joinConditions = [],
  onEventsChange,
  onJoinConditionsChange
}) {
  const [mode, setMode] = useState('join'); // 'join' | 'union'
  const [showEventSelector, setShowEventSelector] = useState(false);
  const [newJoinCondition, setNewJoinCondition] = useState({
    leftEvent: '',
    leftField: '',
    rightEvent: '',
    rightField: '',
    operator: '='
  });

  // 添加事件到选择列表
  const handleAddEvent = (event) => {
    if (!selectedEvents.find(e => e.id === event.id)) {
      onEventsChange([...selectedEvents, event]);
    }
    setShowEventSelector(false);
  };

  // 移除事件
  const handleRemoveEvent = (eventId) => {
    onEventsChange(selectedEvents.filter(e => e.id !== eventId));
  };

  // 添加JOIN条件
  const handleAddJoinCondition = () => {
    if (!newJoinCondition.leftEvent || !newJoinCondition.rightEvent) {
      toast.error('请选择左右两侧事件');
      return;
    }

    onJoinConditionsChange([...joinConditions, { ...newJoinCondition }]);
    setNewJoinCondition({
      leftEvent: '',
      leftField: '',
      rightEvent: '',
      rightField: '',
      operator: '='
    });
  };

  // 移除JOIN条件
  const handleRemoveJoinCondition = (index) => {
    onJoinConditionsChange(joinConditions.filter((_, i) => i !== index));
  };

  // 获取可用字段
  const getAvailableFields = (eventName) => {
    const event = availableEvents.find(e => e.event_name === eventName);
    return event?.fields || [];
  };

  return (
    <div className="multi-event-config-v2">
      <div className="config-header">
        <h3>🔗 多事件配置</h3>

        {/* 模式切换 */}
        <div className="mode-switcher">
          <button
            className={`mode-btn ${mode === 'join' ? 'active' : ''}`}
            onClick={() => setMode('join')}
          >
            JOIN 模式
          </button>
          <button
            className={`mode-btn ${mode === 'union' ? 'active' : ''}`}
            onClick={() => setMode('union')}
          >
            UNION 模式
          </button>
        </div>
      </div>

      {/* 已选择事件列表 */}
      <div className="selected-events-section">
        <div className="section-header">
          <h4>已选择事件 ({selectedEvents.length})</h4>
          <button
            className="btn btn-sm btn-primary"
            onClick={() => setShowEventSelector(true)}
          >
            <i className="bi bi-plus"></i> 添加事件
          </button>
        </div>

        <div className="events-list">
          {selectedEvents.length === 0 ? (
            <div className="empty-state">
              <p>尚未选择事件</p>
              <p className="text-muted">请点击上方按钮添加事件</p>
            </div>
          ) : (
            selectedEvents.map((event, index) => (
              <div key={event.id} className="event-item">
                <span className="event-index">{index + 1}</span>
                <span className="event-name">{event.event_name}</span>
                <button
                  className="btn btn-sm btn-outline-danger remove-btn"
                  onClick={() => handleRemoveEvent(event.id)}
                >
                  <i className="bi bi-trash"></i>
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* JOIN模式配置 */}
      {mode === 'join' && selectedEvents.length >= 2 && (
        <div className="join-config-section">
          <div className="section-header">
            <h4>JOIN 条件配置</h4>
          </div>

          {/* 已有JOIN条件 */}
          {joinConditions.length > 0 && (
            <div className="existing-conditions">
              <h5>已配置条件</h5>
              {joinConditions.map((condition, index) => (
                <div key={index} className="condition-item">
                  <code>
                    {condition.leftEvent}.{condition.leftField}{' '}
                    {condition.operator}{' '}
                    {condition.rightEvent}.{condition.rightField}
                  </code>
                  <button
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => handleRemoveJoinCondition(index)}
                  >
                    <i className="bi bi-x"></i>
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* 添加新条件 */}
          <div className="new-condition-form">
            <h5>添加JOIN条件</h5>

            <div className="form-row">
              <div className="form-group">
                <label>左事件</label>
                <select
                  value={newJoinCondition.leftEvent}
                  onChange={(e) => setNewJoinCondition({
                    ...newJoinCondition,
                    leftEvent: e.target.value
                  })}
                >
                  <option value="">选择事件</option>
                  {selectedEvents.map(event => (
                    <option key={event.id} value={event.event_name}>
                      {event.event_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>左字段</label>
                <select
                  value={newJoinCondition.leftField}
                  onChange={(e) => setNewJoinCondition({
                    ...newJoinCondition,
                    leftField: e.target.value
                  })}
                  disabled={!newJoinCondition.leftEvent}
                >
                  <option value="">选择字段</option>
                  {getAvailableFields(newJoinCondition.leftEvent).map(field => (
                    <option key={field.field_name} value={field.field_name}>
                      {field.field_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group operator-select">
                <label>操作符</label>
                <select
                  value={newJoinCondition.operator}
                  onChange={(e) => setNewJoinCondition({
                    ...newJoinCondition,
                    operator: e.target.value
                  })}
                >
                  <option value="=">=</option>
                  <option value=">">{'>'}</option>
                  <option value="<">{'<'}</option>
                  <option value=">=">≥</option>
                  <option value="<=">≤</option>
                  <option value="!=">≠</option>
                </select>
              </div>

              <div className="form-group">
                <label>右事件</label>
                <select
                  value={newJoinCondition.rightEvent}
                  onChange={(e) => setNewJoinCondition({
                    ...newJoinCondition,
                    rightEvent: e.target.value
                  })}
                >
                  <option value="">选择事件</option>
                  {selectedEvents.map(event => (
                    <option key={event.id} value={event.event_name}>
                      {event.event_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>右字段</label>
                <select
                  value={newJoinCondition.rightField}
                  onChange={(e) => setNewJoinCondition({
                    ...newJoinCondition,
                    rightField: e.target.value
                  })}
                  disabled={!newJoinCondition.rightEvent}
                >
                  <option value="">选择字段</option>
                  {getAvailableFields(newJoinCondition.rightEvent).map(field => (
                    <option key={field.field_name} value={field.field_name}>
                      {field.field_name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-actions">
                <button
                  className="btn btn-primary"
                  onClick={handleAddJoinCondition}
                >
                  <i className="bi bi-plus"></i> 添加条件
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* UNION模式配置 */}
      {mode === 'union' && selectedEvents.length >= 2 && (
        <div className="union-config-section">
          <div className="section-header">
            <h4>UNION 字段映射配置</h4>
            <p className="text-muted">
              确保所有事件的字段顺序和类型一致
            </p>
          </div>

          <div className="union-mapping-info">
            <div className="info-item">
              <i className="bi bi-info-circle"></i>
              <span>UNION ALL 将合并所有事件的指定字段</span>
            </div>
            <div className="info-item">
              <i className="bi bi-exclamation-triangle"></i>
              <span>请确保字段数量和类型匹配</span>
            </div>
          </div>
        </div>
      )}

      {/* 事件选择器弹窗 */}
      {showEventSelector && (
        <div className="event-selector-modal">
          <div className="modal-backdrop" onClick={() => setShowEventSelector(false)} />
          <div className="modal-content glass-card">
            <div className="modal-header">
              <h4>选择事件</h4>
              <button className="btn btn-sm btn-outline-secondary" onClick={() => setShowEventSelector(false)}>
                <i className="bi bi-x"></i>
              </button>
            </div>

            <div className="event-list">
              {availableEvents
                .filter(event => !selectedEvents.find(e => e.id === event.id))
                .map(event => (
                  <div
                    key={event.id}
                    className="selectable-event"
                    onClick={() => handleAddEvent(event)}
                  >
                    <div className="event-info">
                      <strong>{event.event_name}</strong>
                      <span className="event-id">ID: {event.id}</span>
                    </div>
                    <i className="bi bi-plus-circle"></i>
                  </div>
                ))
              }
            </div>
          </div>
        </div>
      )}

      {/* 预览生成的HQL类型 */}
      {selectedEvents.length >= 2 && (
        <div className="hql-preview-info">
          <h5>生成的HQL类型</h5>
          <div className="preview-badge">
            {mode === 'join' ? (
              <span className="badge badge-primary">
                <i className="bi bi-diagram-3"></i> 多事件 JOIN
              </span>
            ) : (
              <span className="badge badge-success">
                <i className="bi bi-layers"></i> 多事件 UNION ALL
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
