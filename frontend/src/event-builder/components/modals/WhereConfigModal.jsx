/**
 * WhereConfigModal Component
 * WHERE条件配置模态框组件
 */
import { useState } from 'react';
import { Input } from '@shared/ui';

export default function WhereConfigModal({ conditions, onChange, onClose }) {
  const [localConditions, setLocalConditions] = useState([...conditions]);

  // 添加新条件
  const handleAddCondition = () => {
    const newCondition = {
      id: Date.now(),
      field: '',
      operator: '=',
      value: '',
      logicalOperator: localConditions.length > 0 ? 'AND' : ''
    };
    setLocalConditions([...localConditions, newCondition]);
  };

  // 更新条件
  const handleUpdateCondition = (index, field, value) => {
    const updated = [...localConditions];
    updated[index][field] = value;
    setLocalConditions(updated);
  };

  // 删除条件
  const handleDeleteCondition = (index) => {
    const updated = localConditions.filter((_, i) => i !== index);
    // 重新设置 logicalOperator
    updated.forEach((cond, i) => {
      if (i === 0) cond.logicalOperator = '';
      else cond.logicalOperator = 'AND';
    });
    setLocalConditions(updated);
  };

  // 保存并关闭
  const handleSave = () => {
    // 移除空条件
    const validConditions = localConditions.filter(c => c.field && c.operator && c.value);
    onChange(validConditions);
    onClose();
  };

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      tabIndex={0}
      role="button"
      aria-label="关闭"
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClose();
        } else if (e.key === 'Escape') {
          e.preventDefault();
          onClose();
        }
      }}
    >
      <div
        className="modal-content glass-card where-config-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>配置WHERE条件</h3>
          <button className="modal-close" onClick={onClose} aria-label="关闭对话框">
            ✕
          </button>
        </div>

        <div className="modal-body">
          {localConditions.length === 0 ? (
            <div className="modal-empty">
              <p>暂无WHERE条件</p>
              <button className="btn btn-primary" onClick={handleAddCondition}>
                添加条件
              </button>
            </div>
          ) : (
            <div className="where-conditions-list">
              {localConditions.map((condition, index) => (
                <div key={condition.id} className="where-condition-item">
                  {index > 0 && (
                    <div className="logical-operator">
                      <select
                        value={condition.logicalOperator}
                        onChange={(e) => handleUpdateCondition(index, 'logicalOperator', e.target.value)}
                      >
                        <option value="AND">AND</option>
                        <option value="OR">OR</option>
                      </select>
                    </div>
                  )}

                  <div className="condition-fields">
                    <Input
                      type="text"
                      placeholder="字段名"
                      value={condition.field}
                      onChange={(e) => handleUpdateCondition(index, 'field', e.target.value)}
                    />
                    <select
                      value={condition.operator}
                      onChange={(e) => handleUpdateCondition(index, 'operator', e.target.value)}
                    >
                      <option value=">=">&ge;</option>
                      <option value="<=">&le;</option>
                      <option value=">">&gt;</option>
                      <option value="<">&lt;</option>
                      <option value="=">=</option>
                      <option value="<=">&le;</option>
                      <option value="≈">≈</option>
                      <option value="!=">&ne;</option>
                      <option value="LIKE">LIKE</option>
                      <option value="NOT LIKE">NOT LIKE</option>
                      <option value="IN">IN</option>
                      <option value="NOT IN">NOT IN</option>
                      <option value="IS NULL">IS NULL</option>
                      <option value="IS NOT NULL">IS NOT NULL</option>
                    </select>
                    <Input
                      type="text"
                      placeholder="值"
                      value={condition.value}
                      onChange={(e) => handleUpdateCondition(index, 'value', e.target.value)}
                    />
                    <button
                      className="btn btn-sm btn-outline-danger"
                      onClick={() => handleDeleteCondition(index)}
                      title="删除"
                    >
                      删除
                    </button>
                  </div>
                </div>
              ))}

              <button className="btn btn-outline-primary btn-sm" onClick={handleAddCondition}>
                添加条件
              </button>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            取消
          </button>
          <button className="btn btn-primary" onClick={handleSave}>
            保存
          </button>
        </div>
      </div>
    </div>
  );
}
