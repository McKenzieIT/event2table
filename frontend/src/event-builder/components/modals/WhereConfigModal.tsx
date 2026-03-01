/**
 * WhereConfigModal Component
 * WHERE条件配置模态框组件
 */
import { useState } from 'react';
import { Input } from '@shared/ui';
import type { WhereCondition } from '@shared/types/whereBuilder';

/**
 * WHERE条件项接口（简化版，用于模态框内部）
 */
interface LocalWhereCondition {
  id: number;
  field: string;
  operator: string;
  value: string;
  logicalOperator: 'AND' | 'OR' | '';
}

/**
 * 组件Props接口
 */
interface WhereConfigModalProps {
  conditions: WhereCondition[];
  onChange: (conditions: WhereCondition[]) => void;
  onClose: () => void;
}

/**
 * 组件类型定义
 */
type WhereConfigModalComponent = React.FC<WhereConfigModalProps>;

/**
 * WhereConfigModal: WHERE条件配置模态框组件
 *
 * 功能：
 * - 添加、编辑、删除WHERE条件
 * - 支持逻辑操作符（AND/OR）
 * - 支持多种比较操作符（>=, <=, =, !=, LIKE, IN等）
 */
const WhereConfigModal: WhereConfigModalComponent = ({ conditions, onChange, onClose }) => {
  const [localConditions, setLocalConditions] = useState<LocalWhereCondition[]>(
    conditions.map((cond) => ({
      id: parseInt(cond.id) || Date.now() + Math.random(),
      field: cond.field,
      operator: cond.operator,
      value: cond.value?.toString() || '',
      logicalOperator: (cond.logicalOp as 'AND' | 'OR' | '') || '',
    }))
  );

  /**
   * 添加新条件
   */
  const handleAddCondition = (): void => {
    const newCondition: LocalWhereCondition = {
      id: Date.now(),
      field: '',
      operator: '=',
      value: '',
      logicalOperator: localConditions.length > 0 ? 'AND' : '',
    };
    setLocalConditions([...localConditions, newCondition]);
  };

  /**
   * 更新条件
   */
  const handleUpdateCondition = (index: number, field: keyof LocalWhereCondition, value: string): void => {
    const updated = [...localConditions];
    updated[index] = { ...updated[index], [field]: value };
    setLocalConditions(updated);
  };

  /**
   * 删除条件
   */
  const handleDeleteCondition = (index: number): void => {
    const updated = localConditions.filter((_, i) => i !== index);
    // 重新设置 logicalOperator
    updated.forEach((cond, i) => {
      if (i === 0) {
        cond.logicalOperator = '';
      } else {
        cond.logicalOperator = 'AND';
      }
    });
    setLocalConditions(updated);
  };

  /**
   * 保存并关闭
   */
  const handleSave = (): void => {
    // 移除空条件
    const validConditions = localConditions
      .filter((c) => c.field && c.operator && c.value)
      .map((c) => ({
        id: c.id.toString(),
        type: 'condition' as const,
        field: c.field,
        operator: c.operator as any,
        value: c.value,
        logicalOp: c.logicalOperator as 'AND' | 'OR' | undefined,
      }));
    onChange(validConditions);
    onClose();
  };

  /**
   * 处理键盘事件
   */
  const handleKeyDown = (e: React.KeyboardEvent): void => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClose();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      onClose();
    }
  };

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      tabIndex={0}
      role="button"
      aria-label="关闭"
      onKeyDown={handleKeyDown}
    >
      <div
        className="modal-content glass-card where-config-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal-header">
          <h3>配置WHERE条件</h3>
          <button className="modal-close" onClick={onClose} aria-label="关闭对话框" type="button">
            ✕
          </button>
        </div>

        <div className="modal-body">
          {localConditions.length === 0 ? (
            <div className="modal-empty">
              <p>暂无WHERE条件</p>
              <button className="btn btn-primary" onClick={handleAddCondition} type="button">
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
                      <option value=">=">≥</option>
                      <option value="<=">≤</option>
                      <option value=">">&gt;</option>
                      <option value="<">&lt;</option>
                      <option value="=">=</option>
                      <option value="<=">≤</option>
                      <option value="≈">≈</option>
                      <option value="!=">≠</option>
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
                      type="button"
                    >
                      删除
                    </button>
                  </div>
                </div>
              ))}

              <button className="btn btn-outline-primary btn-sm" onClick={handleAddCondition} type="button">
                添加条件
              </button>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose} type="button">
            取消
          </button>
          <button className="btn btn-primary" onClick={handleSave} type="button">
            保存
          </button>
        </div>
      </div>
    </div>
  );
};

export default WhereConfigModal;
