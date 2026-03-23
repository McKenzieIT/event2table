// ⚡️ REACT PERF - Features: Optimized with React.memo, useCallback
// ✅ Performance optimization: Prevent unnecessary re-renders in add event form
// See: docs/reports/2026-03-06/FEATURES-OPTIMIZATION-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * AddEventModalGraphQL - 添加事件模态框（GraphQL版本）
 *
 * 使用GraphQL Mutation替代REST API
 */

import { Modal, Button, Input, Select, useToast } from '@shared/ui';
import React, { useState, useRef, useEffect, ChangeEvent, FormEvent, useCallback, memo } from 'react';

import { useCreateEvent } from '../../shared/graphql/hooks';

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
  }, [formData]);

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="添加事件" size="md">
      <form onSubmit={handleSubmit} className="add-event-form">
        <div className="form-group">
          <label htmlFor="eventName">事件名称（英文）</label>
          <Input
            id="eventName"
            ref={eventNameRef}
            type="text"
            value={formData.eventName}
            onChange={(e) => handleChange('eventName', e.target.value)}
            placeholder="例如: player_login"
            error={errors.eventName}
          />
        </div>

        <div className="form-group">
          <label htmlFor="eventNameCn">事件名称（中文）</label>
          <Input
            id="eventNameCn"
            ref={eventNameCnRef}
            type="text"
            value={formData.eventNameCn}
            onChange={(e) => handleChange('eventNameCn', e.target.value)}
            placeholder="例如: 玩家登录"
            error={errors.eventNameCn}
          />
        </div>

        <div className="form-group">
          <label htmlFor="categoryId">事件分类</label>
          <Select
            id="categoryId"
            value={formData.categoryId}
            onChange={(e) => handleChange('categoryId', e.target.value)}
            error={errors.categoryId}
          >
            <option value="">请选择分类</option>
            <option value="1">登录事件</option>
            <option value="2">游戏事件</option>
            <option value="3">支付事件</option>
          </Select>
        </div>

        <div className="form-group">
          <label>
            <input
              type="checkbox"
              checked={formData.includeInCommonParams}
              onChange={(e) => handleChange('includeInCommonParams', e.target.checked)}
            />
            包含通用参数
          </label>
        </div>

        <div className="form-actions">
          <Button variant="outline-secondary" onClick={handleClose}>
            取消
          </Button>
          <Button variant="primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? '提交中...' : '提交'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

// ✅ 添加 React.memo 优化渲染性能
const AddEventModalGraphQLMemo = memo(AddEventModalGraphQL);

export default AddEventModalGraphQLMemo;
