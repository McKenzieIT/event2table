// ⚡️ REACT PERF - Features: Optimized with React.memo, useCallback
// ✅ Performance optimization: Prevent unnecessary re-renders in add event form
// See: docs/reports/2026-03-06/FEATURES-OPTIMIZATION-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * AddEventModalGraphQL - 添加事件模态框（GraphQL版本）
 *
 * 使用GraphQL Mutation替代REST API
 */

import React, { useState, useRef, useEffect, ChangeEvent, FormEvent, useCallback, memo } from 'react';
import { BaseModal, Button, Input, Select, useToast } from '@shared/ui';
import { useCreateEvent } from '../../graphql/hooks';
import './AddEventModal.css';

interface FormData {
  eventName: string;
  eventNameCn: string;
  categoryId: string;
  includeInCommonParams: boolean;
}

interface FormErrors {
  eventName?: string;
  eventNameCn?: string;
  categoryId?: string;
}

interface AddEventModalProps {
  isOpen: boolean;
  onClose: () => void;
  gameGid: string | number;
}

const AddEventModalGraphQL: React.FC<AddEventModalProps> = ({ isOpen, onClose, gameGid }) => {
  const { success, error: showError } = useToast();

  // Form state
  const [formData, setFormData] = useState<FormData>({
    eventName: '',
    eventNameCn: '',
    categoryId: '',
    includeInCommonParams: false
  });
  const [errors, setErrors] = useState<FormErrors>({});

  // Refs to input elements (for Chrome MCP compatibility)
  const eventNameRef = useRef<HTMLInputElement>(null);
  const eventNameCnRef = useRef<HTMLInputElement>(null);

  // GraphQL Mutation
  const [createEvent, { loading: isSubmitting }] = useCreateEvent();

  // ✅ 使用 useCallback 优化 - Handle input change
  const handleChange = useCallback((field: keyof FormData, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear error when user types
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }));
    }
  }, [errors]);

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.eventName) {
      newErrors.eventName = '事件名称（英文）不能为空';
    } else if (!/^[a-z_]+$/.test(formData.eventName)) {
      newErrors.eventName = '事件名称只能包含小写字母和下划线';
    }

    if (!formData.eventNameCn) {
      newErrors.eventNameCn = '事件名称（中文）不能为空';
    }

    if (!formData.categoryId) {
      newErrors.categoryId = '请选择事件分类';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // ✅ 使用 useCallback 优化 - Handle submit
  const handleSubmit = useCallback(async (e: FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const { data } = await createEvent({
        variables: {
          gameGid: parseInt(String(gameGid), 10),
          eventName: formData.eventName,
          eventNameCn: formData.eventNameCn,
          categoryId: parseInt(formData.categoryId, 10),
          includeInCommonParams: formData.includeInCommonParams
        }
      });

      if (data?.createEvent?.ok) {
        success('事件创建成功');
        // Reset form
        setFormData({
          eventName: '',
          eventNameCn: '',
          categoryId: '',
          includeInCommonParams: false
        });
        onClose();
      } else {
        showError(data?.createEvent?.errors?.[0] || '创建失败');
      }
    } catch (err: unknown) {
      const error = err as { message?: string };
      showError(`创建失败: ${error.message || 'Unknown error'}`);
    }
  }, [gameGid, formData, createEvent, success, showError, onClose]);

  // ✅ 使用 useCallback 优化 - Handle close
  const handleClose = useCallback(() => {
    setFormData({
      eventName: '',
      eventNameCn: '',
      categoryId: '',
      includeInCommonParams: false
    });
    setErrors({});
    onClose();
  }, [onClose]);

  // Chrome MCP兼容性: 监听DOM值变化并同步到state
  useEffect(() => {
    if (!eventNameRef.current || !eventNameCnRef.current) {
      return;
    }

    const eventNameDomValue = eventNameRef.current.value;
    const eventNameCnDomValue = eventNameCnRef.current.value;

    const updates: Partial<FormData> = {};

    if (eventNameDomValue !== formData.eventName) {
      updates.eventName = eventNameDomValue;
    }
    if (eventNameCnDomValue !== formData.eventNameCn) {
      updates.eventNameCn = eventNameCnDomValue;
    }

    if (Object.keys(updates).length > 0) {
      setFormData(prev => ({ ...prev, ...updates }));
    }
  }, [formData.eventName, formData.eventNameCn]);

  return (
    <BaseModal isOpen={isOpen} onClose={handleClose} title="添加事件" size="md">
      <form onSubmit={handleSubmit} className="add-event-form">
        <Input
          id="eventName"
          label="事件名称（英文）"
          required
          type="text"
          value={formData.eventName}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('eventName', e.target.value)}
          placeholder="例如: user_login"
          error={errors.eventName}
          ref={eventNameRef}
        />
        {errors.eventName && <span className="error-message">{errors.eventName}</span>}
        <span className="hint">只能包含小写字母和下划线</span>

        <Input
          id="eventNameCn"
          label="事件名称（中文）"
          required
          type="text"
          value={formData.eventNameCn}
          onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('eventNameCn', e.target.value)}
          placeholder="例如: 用户登录"
          error={errors.eventNameCn}
          ref={eventNameCnRef}
        />
        {errors.eventNameCn && <span className="error-message">{errors.eventNameCn}</span>}

        <div className="form-group">
          <Select
            id="categoryId"
            label="事件分类"
            required
            value={formData.categoryId}
            onChange={(e: ChangeEvent<HTMLSelectElement>) => handleChange('categoryId', e.target.value)}
            options={[
              { value: '', label: '请选择分类' },
              { value: '1', label: '用户行为' },
              { value: '2', label: '支付相关' },
              { value: '3', label: '游戏逻辑' },
              { value: '4', label: '系统事件' }
            ]}
          />
          {errors.categoryId && <span className="error-message">{errors.categoryId}</span>}
        </div>

        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={formData.includeInCommonParams}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('includeInCommonParams', e.target.checked)}
            />
            包含在通用参数中
          </label>
        </div>

        <div className="form-actions">
          <Button type="button" onClick={handleClose} variant="secondary">
            取消
          </Button>
          <Button type="submit" variant="primary" loading={isSubmitting}>
            {isSubmitting ? '创建中...' : '创建事件'}
          </Button>
        </div>
      </form>
    </BaseModal>
  );
};

// ✅ 添加 React.memo 优化渲染性能
const AddEventModalGraphQLMemo = memo(AddEventModalGraphQL);

export default AddEventModalGraphQLMemo;
