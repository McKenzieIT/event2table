/**
 * JoinConfigModal Component
 * JOIN节点配置模态框
 *
 * 功能：
 * - 支持 INNER/LEFT/RIGHT/FULL OUTER JOIN
 * - 多条件配置 (AND连接)
 * - 字段选择器
 * - 操作符选择 (=, >, <, >=, <=, <>)
 * - SQL实时预览
 *
 * @version 1.0.0
 * @date 2026-01-29
 */

import { Modal , Button, useToast, EmptyState } from '@shared/ui';
import React, { useState, useMemo, useCallback, memo } from 'react';

import './JoinConfigModal.css';
import type { JoinConfigModalProps, JoinConfig, JoinCondition, AvailableFields } from './types';

function JoinConfigModal({
  isOpen,
  onClose,
  node,
  availableFields,
  onApply
}: JoinConfigModalProps): React.JSX.Element | null {
  const { warning: toastWarning } = useToast();

  // JOIN类型状态
  const [joinType, setJoinType] = useState<JoinConfig['joinType']>('INNER');

  // 连接条件状态
  const [conditions, setConditions] = useState<JoinCondition[]>([
    { leftField: '', rightField: '', operator: '=' }
  ]);

  // ⚡ PERF: 使用 useCallback 稳定处理函数
  const addCondition = useCallback((): void => {
    setConditions([...conditions, {
      leftField: '',
      rightField: '',
      operator: '='
    }]);
  }, [conditions]);

  const removeCondition = useCallback((index: number): void => {
    setConditions(conditions.filter((_, i) => i !== index));
  }, [conditions]);

  const updateCondition = useCallback((index: number, field: keyof JoinCondition, value: string): void => {
    const newConditions = [...conditions];
    newConditions[index] = { ...newConditions[index], [field]: value };
    setConditions(newConditions);
  }, [conditions]);

  // ⚡ PERF: SQL预览使用useMemo缓存计算结果
  const sqlPreview = useMemo(() => {
    const validConditions = conditions.filter(
      c => c.leftField && c.rightField
    );

    if (validConditions.length === 0) {
      return '-- 请添加连接条件';
    }

    const conditionStr = validConditions
      .map(c => `${c.leftField} ${c.operator} ${c.rightField}`)
      .join('\n    AND ');

    return `SELECT *\nFROM table1\n${joinType} JOIN table2\nON ${conditionStr};`;
  }, [joinType, conditions]);

  const handleApply = useCallback((): void => {
    const validConditions = conditions.filter(
      c => c.leftField && c.rightField
    );

    if (validConditions.length === 0) {
      toastWarning('请至少添加一个有效的连接条件');
      return;
    }

    const config: JoinConfig = {
      joinType,
      conditions: validConditions
    };

    onApply(config);
    onClose();
  }, [conditions, joinType, onApply, onClose, toastWarning]);

  if (!isOpen) return null;

  // 检查可用字段
  const hasFields = (availableFields as AvailableFields)?.left?.length > 0 &&
                   (availableFields as AvailableFields)?.right?.length > 0;

  if (!hasFields) {
    return (
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title="JOIN节点配置"
        size="lg"
      >
        <div className="join-config-modal">
          <EmptyState
            icon={<i className="bi bi-exclamation-triangle" style={{ fontSize: '48px' }} />}
            title="无法配置JOIN节点"
            description="JOIN节点需要连接两个事件节点才能配置。请先连接事件节点，然后双击JOIN节点进行配置"
          />
          <div className="modal-footer">
            <Button variant="secondary" onClick={onClose}>
              关闭
            </Button>
          </div>
        </div>
      </Modal>
    );
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="JOIN节点配置"
      size="lg"
    >
      <div className="join-config-modal">
        {/* JOIN类型选择 */}
        <div className="join-type-section">
          <label className="form-label">JOIN类型:</label>
          <div className="join-type-selector">
            {(['INNER', 'LEFT', 'RIGHT', 'FULL OUTER'] as const).map(type => (
              <label key={type} className={`join-type-option ${joinType === type ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="joinType"
                  value={type}
                  checked={joinType === type}
                  onChange={(e) => setJoinType(e.target.value as JoinConfig['joinType'])}
                />
                <span>{type} JOIN</span>
              </label>
            ))}
          </div>
        </div>

        {/* 连接条件 */}
        <div className="conditions-section">
          <div className="section-header">
            <label className="form-label">连接条件:</label>
            <Button
              variant="outline-primary"
              size="sm"
              onClick={addCondition}
              type="button"
            >
              <i className="bi bi-plus"></i> 添加条件
            </Button>
          </div>

          <div className="conditions-list">
            {conditions.map((condition, index) => (
              <div key={index} className="condition-row">
                {/* 左表字段 */}
                <select
                  className="form-select"
                  value={condition.leftField}
                  onChange={(e) => updateCondition(index, 'leftField', e.target.value)}
                >
                  <option value="">选择左表字段</option>
                  {(availableFields as AvailableFields).left.map(field => (
                    <option key={field.name} value={field.name}>
                      {field.displayName || field.name}
                    </option>
                  ))}
                </select>

                {/* 操作符 */}
                <select
                  className="form-select operator-select"
                  value={condition.operator}
                  onChange={(e) => updateCondition(index, 'operator', e.target.value)}
                >
                  <option value="=">=</option>
                  <option value=">">&gt;</option>
                  <option value="<">&lt;</option>
                  <option value=">=">&gt;=</option>
                  <option value="<=">&lt;=</option>
                  <option value="<>">&lt;&gt;</option>
                </select>

                {/* 右表字段 */}
                <select
                  className="form-select"
                  value={condition.rightField}
                  onChange={(e) => updateCondition(index, 'rightField', e.target.value)}
                >
                  <option value="">选择右表字段</option>
                  {(availableFields as AvailableFields).right.map(field => (
                    <option key={field.name} value={field.name}>
                      {field.displayName || field.name}
                    </option>
                  ))}
                </select>

                {/* 删除按钮 */}
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => removeCondition(index)}
                  type="button"
                  title="删除条件"
                >
                  <i className="bi bi-trash"></i>
                </Button>
              </div>
            ))}

            {conditions.length === 0 && (
              <div className="empty-conditions">
                <p className="text-muted">暂无连接条件</p>
              </div>
            )}
          </div>
        </div>

        {/* SQL预览 */}
        <div className="preview-section">
          <label className="form-label">SQL预览:</label>
          <pre className="sql-preview">
            <code>{sqlPreview}</code>
          </pre>
        </div>

        {/* 底部按钮 */}
        <div className="modal-footer">
          <Button variant="secondary" onClick={onClose}>
            取消
          </Button>
          <Button
            variant="primary"
            onClick={handleApply}
            disabled={conditions.filter(c => c.leftField && c.rightField).length === 0}
          >
            <i className="bi bi-check"></i> 应用配置
          </Button>
        </div>
      </div>
    </Modal>
  );
}

// ⚡ PERF: 使用 React.memo 优化渲染性能
const JoinConfigModalMemo = memo(JoinConfigModal);
export default JoinConfigModalMemo;
