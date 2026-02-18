/**
 * BaseFieldsList Component
 * 基础字段列表组件
 */
import { useState } from 'react';

const BASE_FIELDS = [
  { fieldName: 'ds', displayName: '分区' },
  { fieldName: 'role_id', displayName: '角色ID' },
  { fieldName: 'account_id', displayName: '账号ID' },
  { fieldName: 'utdid', displayName: '设备ID' },
  { fieldName: 'tm', displayName: '上报时间' },
  { fieldName: 'ts', displayName: '上报时间戳' },
  { fieldName: 'envinfo', displayName: '环境信息' },
];

export default function BaseFieldsList({ onAddField }) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const handleDoubleClick = (field) => {
    onAddField('base', field.fieldName, field.displayName);

    // Add success animation
    const element = document.querySelector(`[data-field="${field.fieldName}"]`);
    if (element) {
      element.classList.add('double-click-success');
      setTimeout(() => {
        element.classList.remove('double-click-success');
      }, 600);
    }
  };

  const handleDragStart = (e, field) => {
    e.dataTransfer.effectAllowed = 'copy';
    // 设置多种格式以确保兼容性
    const dragData = {
      type: 'base',
      fieldType: 'base',
      fieldName: field.fieldName,
      displayName: field.displayName,
    };

    // 使用多种格式设置数据
    e.dataTransfer.setData('application/json', JSON.stringify(dragData));
    e.dataTransfer.setData('text/plain', JSON.stringify(dragData));
  };

  return (
    <div className="sidebar-section glass-card-dark">
      <div
        className={`section-header ${isCollapsed ? 'collapsed' : ''}`}
        onClick={() => setIsCollapsed(!isCollapsed)}
        style={{ cursor: 'pointer' }}
      >
        <h3>
          <i className="bi bi-list-task"></i>
                   基础字段
        </h3>
        <i className={`bi ${isCollapsed ? 'chevron-right' : 'chevron-down'} toggle-icon`}></i>
      </div>
      <div className={`section-content ${isCollapsed ? 'collapsed' : ''}`}>
        <div className="base-fields-list">
          {BASE_FIELDS.map(field => (
            <div
              key={field.fieldName}
              data-testid={`param-${field.fieldName}`}
              data-field={field.fieldName}
              className="base-field-item"
              draggable
              onDragStart={(e) => handleDragStart(e, field)}
              onDoubleClick={() => handleDoubleClick(field)}
              title="双击或拖拽添加到画布"
            >
              <span className="field-name">{field.displayName}</span>
              <small className="field-en">{field.fieldName}</small>
            </div>
          ))}
        </div>
        <p className="help-text">双击或拖拽添加字段</p>
      </div>
    </div>
  );
}
