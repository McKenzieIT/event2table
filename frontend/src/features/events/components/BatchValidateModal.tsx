/**
 * BatchValidateModal Component
 *
 * 批量验证事件模态框
 * 验证事件配置的完整性，展示验证结果和修复建议
 */

import type { Event } from '@shared/types/event-types';
import { Modal, Button, Badge, Spinner, useToast } from '@shared/ui';
import React, { useState, useMemo, useCallback } from 'react';

/**
 * 验证问题类型
 */
export enum ValidationIssueType {
  MISSING_NAME = 'MISSING_NAME',
  MISSING_CATEGORY = 'MISSING_CATEGORY',
  MISSING_SOURCE_TABLE = 'MISSING_SOURCE_TABLE',
  MISSING_TARGET_TABLE = 'MISSING_TARGET_TABLE',
  NO_PARAMETERS = 'NO_PARAMETERS',
  INVALID_NAME_FORMAT = 'INVALID_NAME_FORMAT',
}

/**
 * 验证问题
 */
export interface ValidationIssue {
  type: ValidationIssueType;
  eventId: number;
  eventName: string;
  message: string;
  severity: 'error' | 'warning';
  suggestion?: string;
}

/**
 * 验证结果
 */
export interface ValidationResult {
  totalEvents: number;
  validEvents: number;
  invalidEvents: number;
  issues: ValidationIssue[];
}

/**
 * 批量验证模态框属性
 */
export interface BatchValidateModalProps {
  /** 是否打开模态框 */
  isOpen: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 选中的事件列表 */
  selectedEvents: Event[];
}

/**
 * 批量验证模态框组件
 */
export const BatchValidateModal = React.memo(function BatchValidateModal({
  isOpen,
  onClose,
  selectedEvents,
}: BatchValidateModalProps) {
  const { success, error, warning } = useToast();

  // 验证状态
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);

  // 重置验证结果
  const resetValidation = useCallback(() => {
    setValidationResult(null);
  }, []);

  // 当模态框打开时重置验证结果
  React.useEffect(() => {
    if (isOpen) {
      resetValidation();
    }
  }, [isOpen, resetValidation]);

  // 验证单个事件
  const validateEvent = useCallback((event: Event): ValidationIssue[] => {
    const issues: ValidationIssue[] = [];

    // 检查事件名称
    if (!event.eventName || event.eventName.trim() === '') {
      issues.push({
        type: ValidationIssueType.MISSING_NAME,
        eventId: event.id,
        eventName: event.eventNameCn || event.eventName || `#${event.id}`,
        message: '缺少事件英文名称',
        severity: 'error',
        suggestion: '请为事件添加英文名称',
      });
    } else if (!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(event.eventName)) {
      issues.push({
        type: ValidationIssueType.INVALID_NAME_FORMAT,
        eventId: event.id,
        eventName: event.eventNameCn || event.eventName || `#${event.id}`,
        message: '事件名称格式不正确',
        severity: 'warning',
        suggestion: '事件名称应以字母开头，只能包含字母、数字和下划线',
      });
    }

    // 检查中文名称
    if (!event.eventNameCn || event.eventNameCn.trim() === '') {
      issues.push({
        type: ValidationIssueType.MISSING_NAME,
        eventId: event.id,
        eventName: event.eventName || `#${event.id}`,
        message: '缺少事件中文名称',
        severity: 'warning',
        suggestion: '建议为事件添加中文名称',
      });
    }

    // 检查分类
    if (!event.categoryId && !event.categoryName) {
      issues.push({
        type: ValidationIssueType.MISSING_CATEGORY,
        eventId: event.id,
        eventName: event.eventNameCn || event.eventName || `#${event.id}`,
        message: '未设置事件分类',
        severity: 'warning',
        suggestion: '建议为事件设置分类以便于管理',
      });
    }

    // 检查源表
    if (!event.sourceTable || event.sourceTable.trim() === '') {
      issues.push({
        type: ValidationIssueType.MISSING_SOURCE_TABLE,
        eventId: event.id,
        eventName: event.eventNameCn || event.eventName || `#${event.id}`,
        message: '未设置源表',
        severity: 'error',
        suggestion: '请为事件设置源表',
      });
    }

    // 检查目标表
    if (!event.targetTable || event.targetTable.trim() === '') {
      issues.push({
        type: ValidationIssueType.MISSING_TARGET_TABLE,
        eventId: event.id,
        eventName: event.eventNameCn || event.eventName || `#${event.id}`,
        message: '未设置目标表',
        severity: 'error',
        suggestion: '请为事件设置目标表',
      });
    }

    // 检查参数
    if (!event.fields || event.fields.length === 0) {
      issues.push({
        type: ValidationIssueType.NO_PARAMETERS,
        eventId: event.id,
        eventName: event.eventNameCn || event.eventName || `#${event.id}`,
        message: '事件没有配置参数',
        severity: 'warning',
        suggestion: '建议为事件添加必要的参数',
      });
    }

    return issues;
  }, []);

  // 执行批量验证
  const handleValidate = useCallback(() => {
    setIsValidating(true);

    // 模拟异步验证（实际可以调用后端API）
    setTimeout(() => {
      const allIssues: ValidationIssue[] = [];
      const validEventIds = new Set<number>();

      selectedEvents.forEach(event => {
        const issues = validateEvent(event);
        if (issues.length === 0) {
          validEventIds.add(event.id);
        } else {
          allIssues.push(...issues);
        }
      });

      const result: ValidationResult = {
        totalEvents: selectedEvents.length,
        validEvents: validEventIds.size,
        invalidEvents: selectedEvents.length - validEventIds.size,
        issues: allIssues,
      };

      setValidationResult(result);
      setIsValidating(false);

      // 显示验证结果通知
      if (result.invalidEvents === 0) {
        success(`所有 ${result.totalEvents} 个事件验证通过！`);
      } else {
        warning(`验证完成：${result.validEvents} 个通过，${result.invalidEvents} 个存在问题`);
      }
    }, 500);
  }, [selectedEvents, validateEvent, success, warning]);

  // 统计问题类型
  const issueStats = useMemo(() => {
    if (!validationResult) return null;

    const stats = {
      error: 0,
      warning: 0,
    };

    validationResult.issues.forEach(issue => {
      if (issue.severity === 'error') {
        stats.error++;
      } else {
        stats.warning++;
      }
    });

    return stats;
  }, [validationResult]);

  // 按严重程度分组问题
  const groupedIssues = useMemo(() => {
    if (!validationResult) return { errors: [], warnings: [] };

    return {
      errors: validationResult.issues.filter(issue => issue.severity === 'error'),
      warnings: validationResult.issues.filter(issue => issue.severity === 'warning'),
    };
  }, [validationResult]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`批量验证 (${selectedEvents.length} 个事件)`}
      size="lg"
    >
      <div className="batch-validate-modal">
        {/* 验证结果摘要 */}
        {validationResult && (
          <div className="validation-summary">
            <div className="summary-stats">
              <div className="stat-item">
                <Badge variant="success">通过: {validationResult.validEvents}</Badge>
              </div>
              <div className="stat-item">
                <Badge variant="danger">错误: {issueStats?.error || 0}</Badge>
              </div>
              <div className="stat-item">
                <Badge variant="warning">警告: {issueStats?.warning || 0}</Badge>
              </div>
            </div>
          </div>
        )}

        {/* 验证按钮 */}
        {!validationResult && (
          <div className="validate-actions">
            <Button
              variant="primary"
              onClick={handleValidate}
              loading={isValidating}
              disabled={isValidating}
            >
              开始验证
            </Button>
          </div>
        )}

        {/* 验证进度 */}
        {isValidating && (
          <div className="validation-progress">
            <Spinner size="md" label="正在验证事件配置..." />
          </div>
        )}

        {/* 验证结果详情 */}
        {validationResult && !isValidating && (
          <div className="validation-results">
            {/* 错误列表 */}
            {groupedIssues.errors.length > 0 && (
              <div className="issue-section error-section">
                <h4>
                  <Badge variant="danger">错误 ({groupedIssues.errors.length})</Badge>
                </h4>
                <div className="issue-list">
                  {groupedIssues.errors.map((issue, index) => (
                    <div key={index} className="issue-item error-item">
                      <div className="issue-header">
                        <Badge variant="secondary">#{issue.eventId}</Badge>
                        <span className="issue-event-name">{issue.eventName}</span>
                      </div>
                      <div className="issue-message">{issue.message}</div>
                      {issue.suggestion && (
                        <div className="issue-suggestion">
                          <strong>建议：</strong> {issue.suggestion}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 警告列表 */}
            {groupedIssues.warnings.length > 0 && (
              <div className="issue-section warning-section">
                <h4>
                  <Badge variant="warning">警告 ({groupedIssues.warnings.length})</Badge>
                </h4>
                <div className="issue-list">
                  {groupedIssues.warnings.map((issue, index) => (
                    <div key={index} className="issue-item warning-item">
                      <div className="issue-header">
                        <Badge variant="secondary">#{issue.eventId}</Badge>
                        <span className="issue-event-name">{issue.eventName}</span>
                      </div>
                      <div className="issue-message">{issue.message}</div>
                      {issue.suggestion && (
                        <div className="issue-suggestion">
                          <strong>建议：</strong> {issue.suggestion}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 无问题 */}
            {validationResult.issues.length === 0 && (
              <div className="no-issues">
                <div className="no-issues-icon">✓</div>
                <p>所有事件配置完整，没有发现问题！</p>
              </div>
            )}
          </div>
        )}

        {/* 操作按钮 */}
        <div className="batch-validate-actions">
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={isValidating}
          >
            关闭
          </Button>
          {validationResult && !isValidating && (
            <Button
              variant="primary"
              onClick={() => {
                resetValidation();
                handleValidate();
              }}
            >
              重新验证
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
});

export default BatchValidateModal;
