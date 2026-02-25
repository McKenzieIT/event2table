/**
 * BaseFieldsQuickToolbar Component
 * 基础字段快速添加工具栏（紧凑型）
 */
import React, { useState, useCallback, useMemo } from 'react';
import PropTypes from 'prop-types';

export default function BaseFieldsQuickToolbar({ canvasFields = [], onAddField }) {
  const [showToolbar, setShowToolbar] = useState(false);

  // Common fields (高频使用)
  const commonFields = useMemo(() => ['ds', 'role_id', 'account_id', 'tm'], []);

  // All available base fields
  const allFields = useMemo(
    () => ['ds', 'role_id', 'account_id', 'tm', 'utdid', 'ts', 'envinfo'],
    []
  );

  // Field metadata (displayName and dataType)
  const fieldMetadata = useMemo(
    () => ({
      ds: { displayName: '分区', dataType: 'STRING' },
      role_id: { displayName: '角色ID', dataType: 'BIGINT' },
      account_id: { displayName: '账号ID', dataType: 'BIGINT' },
      utdid: { displayName: '设备ID', dataType: 'STRING' },
      tm: { displayName: '上报时间', dataType: 'STRING' },
      ts: { displayName: '上报时间戳', dataType: 'BIGINT' },
      envinfo: { displayName: '环境信息', dataType: 'STRING' },
    }),
    []
  );

  // Check if field is already added
  const isAdded = useCallback(
    (fieldName) => canvasFields.some((f) => f.fieldType === 'base' && f.fieldName === fieldName),
    [canvasFields]
  );

  // Add single field
  const handleAddField = useCallback(
    (fieldName) => {
      if (!isAdded(fieldName)) {
        const meta = fieldMetadata[fieldName];
        // 传递对象格式以匹配EventNodeBuilder的onAddField处理函数
        onAddField({
          fieldType: 'base',
          fieldName,
          displayName: meta.displayName,
          dataType: meta.dataType
        });
      }
    },
    [isAdded, fieldMetadata, onAddField]
  );

  // Add all fields
  const handleAddAll = useCallback(() => {
    allFields.forEach(handleAddField);
  }, [allFields, handleAddField]);

  // Add common fields
  const handleAddCommon = useCallback(() => {
    commonFields.forEach(handleAddField);
  }, [commonFields, handleAddField]);

  // Toggle toolbar visibility
  const toggleToolbar = useCallback(() => {
    setShowToolbar(prev => !prev);
  }, []);

  // Calculate stats
  const stats = useMemo(() => {
    const added = allFields.filter(isAdded).length;
    return { total: allFields.length, added };
  }, [allFields, isAdded]);

  return (
    <div className="base-fields-compact">
      <button
        className="btn-quick-add"
        onClick={toggleToolbar}
        aria-expanded={showToolbar}
        aria-haspopup="true"
        type="button"
      >
        <span className="icon">⚡</span>
        <span>基础字段</span>
        <span className="badge" style={{ marginLeft: '4px', fontSize: '10px', opacity: 0.7 }}>
          {stats.added}/{stats.total}
        </span>
      </button>

      {showToolbar && (
        <div className="quick-add-panel">
          {/* Batch Actions */}
          <div className="batch-actions">
            <button
              className="btn-add-all"
              onClick={handleAddAll}
              disabled={stats.added === stats.total}
              title="添加所有基础字段"
              type="button"
            >
              <span>+</span>
              <span>全部</span>
            </button>
            <button
              className="btn-add-common"
              onClick={handleAddCommon}
              disabled={commonFields.every(isAdded)}
              title="添加常用基础字段"
              type="button"
            >
              <span>⚡</span>
              <span>常用</span>
            </button>
          </div>

          {/* Field Buttons Grid */}
          <div className="field-buttons-grid">
            {allFields.map((fieldName) => {
              const added = isAdded(fieldName);
              const meta = fieldMetadata[fieldName];

              return (
                <button
                  key={fieldName}
                  className={`field-btn ${added ? 'added' : ''}`}
                  onClick={() => handleAddField(fieldName)}
                  disabled={added}
                  title={`${meta.displayName} (${meta.dataType})${added ? ' - 已添加' : ''}`}
                  type="button"
                  aria-label={`添加基础字段: ${meta.displayName} (${fieldName})`}
                >
                  {fieldName}
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

BaseFieldsQuickToolbar.propTypes = {
  canvasFields: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      fieldType: PropTypes.oneOf(['base', 'param', 'basic', 'custom', 'fixed']).isRequired,
      fieldName: PropTypes.string,
      name: PropTypes.string.isRequired,
      displayName: PropTypes.string,
      alias: PropTypes.string,
      dataType: PropTypes.string.isRequired,
    })
  ),
  onAddField: PropTypes.func.isRequired,
};
