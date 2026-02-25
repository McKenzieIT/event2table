/**
 * AddEventModalGraphQL - 添加事件模态框（GraphQL版本）
 *
 * 使用GraphQL Mutation替代REST API
 */

import React, { useState } from 'react';
import { BaseModal, Button, Input, Select, useToast } from '@shared/ui';
import { useCreateEvent } from '../../graphql/hooks';
import './AddEventModal.css';

const AddEventModalGraphQL = ({ isOpen, onClose, gameGid }) => {
  const { success, error: showError } = useToast();

  // Form state
  const [formData, setFormData] = useState({
    eventName: '',
    eventNameCn: '',
    categoryId: '',
    includeInCommonParams: false
  });
  const [errors, setErrors] = useState({});

  // GraphQL Mutation
  const [createEvent, { loading: isSubmitting }] = useCreateEvent();

  // Handle input change
  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    // Clear error when user types
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};

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

  // Handle submit
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const { data } = await createEvent({
        variables: {
          gameGid: parseInt(gameGid),
          eventName: formData.eventName,
          eventNameCn: formData.eventNameCn,
          categoryId: parseInt(formData.categoryId),
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
    } catch (err) {
      showError(`创建失败: ${err.message}`);
    }
  };

  // Handle close
  const handleClose = () => {
    setFormData({
      eventName: '',
      eventNameCn: '',
      categoryId: '',
      includeInCommonParams: false
    });
    setErrors({});
    onClose();
  };

  return (
    <BaseModal isOpen={isOpen} onClose={handleClose} title="添加事件" size="md">
      <form onSubmit={handleSubmit} className="add-event-form">
        <Input
          id="eventName"
          label="事件名称（英文）"
          required
          type="text"
          value={formData.eventName}
          onChange={(e) => handleChange('eventName', e.target.value)}
          placeholder="例如: user_login"
          error={errors.eventName}
        />
        {errors.eventName && <span className="error-message">{errors.eventName}</span>}
        <span className="hint">只能包含小写字母和下划线</span>

        <Input
          id="eventNameCn"
          label="事件名称（中文）"
          required
          type="text"
          value={formData.eventNameCn}
          onChange={(e) => handleChange('eventNameCn', e.target.value)}
          placeholder="例如: 用户登录"
          error={errors.eventNameCn}
        />
        {errors.eventNameCn && <span className="error-message">{errors.eventNameCn}</span>}

        <div className="form-group">
          <Select
            id="categoryId"
            label="事件分类"
            required
            value={formData.categoryId}
            onChange={(e) => handleChange('categoryId', e.target.value)}
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
              onChange={(e) => handleChange('includeInCommonParams', e.target.checked)}
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

export default AddEventModalGraphQL;
