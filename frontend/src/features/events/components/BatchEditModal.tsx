/**
 * BatchEditModal Component
 *
 * 批量编辑事件模态框
 * 支持批量修改事件的名称、分类、描述等属性
 */

import type { Event } from '@shared/types/event-types';
import { Modal, Button, Input, Select, Checkbox, Badge, useToast } from '@shared/ui';
import React, { useState, useMemo, useCallback } from 'react';

/**
 * 批量编辑表单数据
 */
export interface BatchEditFormData {
  eventName?: string;
  eventNameCn?: string;
  categoryId?: number | null;
  description?: string;
  includeInCommonParams?: boolean;
}

/**
 * 批量编辑模态框属性
 */
export interface BatchEditModalProps {
  /** 是否打开模态框 */
  isOpen: boolean;
  /** 关闭回调 */
  onClose: () => void;
  /** 选中的事件列表 */
  selectedEvents: Event[];
  /** 可用的分类选项 */
  categoryOptions: Array<{ value: number; label: string }>;
  /** 提交成功回调 */
  onSuccess?: () => void;
}

/**
 * 批量编辑模态框组件
 */
export const BatchEditModal = React.memo(function BatchEditModal({
  isOpen,
  onClose,
  selectedEvents,
  categoryOptions,
  onSuccess,
}: BatchEditModalProps) {
  const { success, error } = useToast();

  // 表单状态
  const [formData, setFormData] = useState<BatchEditFormData>({
    eventName: '',
    eventNameCn: '',
    categoryId: null,
    description: '',
    includeInCommonParams: undefined,
  });

  // 提交状态
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 预览状态
  const [showPreview, setShowPreview] = useState(false);

  // 重置表单
  const resetForm = useCallback(() => {
    setFormData({
      eventName: '',
      eventNameCn: '',
      categoryId: null,
      description: '',
      includeInCommonParams: undefined,
    });
    setShowPreview(false);
  }, []);

  // 当模态框打开时重置表单
  React.useEffect(() => {
    if (isOpen) {
      resetForm();
    }
  }, [isOpen, resetForm]);

  // 处理表单字段变更
  const handleFieldChange = useCallback((field: keyof BatchEditFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
  }, []);

  // 检查是否有字段被修改
  const hasChanges = useMemo(() => {
    return Object.keys(formData).some(key => {
      const value = formData[key as keyof BatchEditFormData];
      return value !== '' && value !== null && value !== undefined;
    });
  }, [formData]);

  // 预览变更
  const handlePreview = useCallback(() => {
    if (!hasChanges) {
      error('请至少选择一个字段进行修改');
      return;
    }
    setShowPreview(true);
  }, [hasChanges, error]);

  // 提交批量编辑
  const handleSubmit = useCallback(async () => {
    if (!hasChanges) {
      error('请至少选择一个字段进行修改');
      return;
    }

    setIsSubmitting(true);

    try {
      const updates = selectedEvents.map(event => {
        const update: any = { id: event.id };
        
        if (formData.eventName) update.event_name = formData.eventName;
        if (formData.eventNameCn) update.event_name_cn = formData.eventNameCn;
        if (formData.categoryId !== null && formData.categoryId !== undefined) {
          update.category_id = formData.categoryId;
        }
        if (formData.description) update.description = formData.description;
        if (formData.includeInCommonParams !== undefined) {
          update.include_in_common_params = formData.includeInCommonParams;
        }
        
        return update;
      });

      const response = await fetch('/api/events/batch', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ updates }),
      });

      if (!response.ok) {
        throw new Error('批量编辑失败');
      }

      const result = await response.json();
      
      if (result.success) {
        success(`成功更新 ${result.data?.updated_count || selectedEvents.length} 个事件`);
        onSuccess?.();
        onClose();
      } else {
        throw new Error(result.message || '批量编辑失败');
      }
    } catch (err) {
      error(err instanceof Error ? err.message : '批量编辑失败');
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, selectedEvents, hasChanges, success, error, onSuccess, onClose]);

  // 渲染预览内容
  const renderPreview = useCallback(() => {
    if (!showPreview) return null;

    const changes = Object.entries(formData)
      .filter(([_, value]) => value !== '' && value !== null && value !== undefined)
      .map(([key, value]) => {
        let label = '';
        switch (key) {
          case 'eventName':
            label = '事件英文名';
            break;
          case 'eventNameCn':
            label = '事件中文名';
            break;
          case 'categoryId':
            const category = categoryOptions.find(c => c.value === value);
            label = `分类: ${category?.label || value}`;
            break;
          case 'description':
            label = '描述';
            break;
          case 'includeInCommonParams':
            label = `包含在公共参数: ${value ? '是' : '否'}`;
            break;
        }
        return { label, value };
      });

    return (
      <div className="batch-edit-preview">
        <h4>预览变更</h4>
        <div className="preview-changes">
          {changes.map((change, index) => (
            <div key={index} className="preview-change-item">
              <Badge variant="info">{change.label}</Badge>
              <span>{String(change.value)}</span>
            </div>
          ))}
        </div>
        <div className="preview-summary">
          <p>将影响 <strong>{selectedEvents.length}</strong> 个事件</p>
        </div>
      </div>
    );
  }, [showPreview, formData, categoryOptions, selectedEvents.length]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`批量编辑 (${selectedEvents.length} 个事件)`}
      size="lg"
      onBeforeClose={() => {
        if (hasChanges) {
          return confirm('有未保存的修改，确定要关闭吗？');
        }
        return true;
      }}
    >
      <div className="batch-edit-modal">
        {/* 事件列表摘要 */}
        <div className="batch-edit-summary">
          <h4>选中的事件</h4>
          <div className="event-list-summary">
            {selectedEvents.slice(0, 5).map(event => (
              <Badge key={event.id} variant="secondary">
                {event.eventNameCn || event.eventName || `#${event.id}`}
              </Badge>
            ))}
            {selectedEvents.length > 5 && (
              <Badge variant="secondary">
                +{selectedEvents.length - 5} 个更多
              </Badge>
            )}
          </div>
        </div>

        {/* 编辑表单 */}
        <div className="batch-edit-form">
          <Input
            type="text"
            label="事件英文名（可选，留空表示不修改）"
            placeholder="输入新的事件英文名..."
            value={formData.eventName || ''}
            onChange={(e) => handleFieldChange('eventName', e.target.value)}
          />

          <Input
            type="text"
            label="事件中文名（可选，留空表示不修改）"
            placeholder="输入新的事件中文名..."
            value={formData.eventNameCn || ''}
            onChange={(e) => handleFieldChange('eventNameCn', e.target.value)}
          />

          <Select
            label="分类（可选，留空表示不修改）"
            placeholder="选择分类..."
            options={[
              { value: '', label: '不修改' },
              ...categoryOptions,
            ]}
            value={formData.categoryId ?? ''}
            onChange={(value) => handleFieldChange('categoryId', value ? Number(value) : null)}
          />

          <Input
            type="text"
            label="描述（可选，留空表示不修改）"
            placeholder="输入新的描述..."
            value={formData.description || ''}
            onChange={(e) => handleFieldChange('description', e.target.value)}
          />

          <div className="checkbox-field">
            <Checkbox
              checked={formData.includeInCommonParams === true}
              onChange={(checked) => handleFieldChange('includeInCommonParams', checked)}
              label="包含在公共参数中"
              helperText="留空表示不修改当前设置"
            />
          </div>
        </div>

        {/* 预览区域 */}
        {renderPreview()}

        {/* 操作按钮 */}
        <div className="batch-edit-actions">
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={isSubmitting}
          >
            取消
          </Button>
          {!showPreview ? (
            <Button
              variant="primary"
              onClick={handlePreview}
              disabled={!hasChanges}
            >
              预览变更
            </Button>
          ) : (
            <>
              <Button
                variant="secondary"
                onClick={() => setShowPreview(false)}
                disabled={isSubmitting}
              >
                返回编辑
              </Button>
              <Button
                variant="primary"
                onClick={handleSubmit}
                loading={isSubmitting}
                disabled={isSubmitting}
              >
                确认提交
              </Button>
            </>
          )}
        </div>
      </div>
    </Modal>
  );
});

export default BatchEditModal;
