/**
 * ParameterTypeEditor - Modal for Editing Parameter Type
 *
 * Allows users to change parameter type with validation.
 * Uses CHANGE_PARAMETER_TYPE mutation.
 *
 * @example
 * <ParameterTypeEditor
 *   isOpen={true}
 *   parameter={{
 *     id: 1,
 *     paramName: 'accountId',
 *     type: 'base',
 *     gameGid: 10000147
 *   }}
 *   onClose={() => setIsOpen(false)}
 *   onSuccess={() => {
 *     setIsOpen(false);
 *     refetch();
 *   }}
 * />
 *
 * Props:
 * @param {boolean} isOpen - Whether the modal is open
 * @param {Object} parameter - Parameter object to edit
 * @param {Function} onClose - Close handler
 * @param {Function} onSuccess - Success callback after type change
 */

import React, { useState } from 'react';
import { useMutation } from '@apollo/client/react';
import { BaseModal, Button, Select, Spinner, useToast } from '@shared/ui';
import { CHANGE_PARAMETER_TYPE } from '@/graphql/mutations';

const ParameterTypeEditor = ({ isOpen, onClose, parameter, onSuccess }) => {
  const { success, error: showError } = useToast();
  const [newType, setNewType] = useState(parameter?.type || 'base');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Mutation for changing parameter type
  const [changeType, { loading: mutationLoading }] = useMutation(CHANGE_PARAMETER_TYPE, {
    onCompleted: (data) => {
      if (data.changeParameterType.ok) {
        success('参数类型更新成功');
        onSuccess?.();
      } else {
        showError(data.changeParameterType.errors?.join(', ') || '更新失败');
      }
      setIsSubmitting(false);
    },
    onError: (err) => {
      console.error('Failed to change parameter type:', err);
      showError('更新失败: ' + err.message);
      setIsSubmitting(false);
    },
  });

  // Type options
  const typeOptions = [
    { value: 'base', label: '基础字段 (base)' },
    { value: 'param', label: '事件参数 (param)' },
    { value: 'custom', label: '自定义 (custom)' },
  ];

  const handleSubmit = async () => {
    if (!parameter) return;

    // Validate
    if (newType === parameter.type) {
      showError('参数类型未变化');
      return;
    }

    setIsSubmitting(true);

    try {
      await changeType({
        variables: {
          paramId: parameter.id,
          newType,
        },
      });
    } catch (err) {
      setIsSubmitting(false);
    }
  };

  const handleCancel = () => {
    setNewType(parameter?.type || 'base');
    onClose();
  };

  // Reset form when parameter changes
  React.useEffect(() => {
    if (parameter) {
      setNewType(parameter.type);
    }
  }, [parameter]);

  if (!isOpen || !parameter) return null;

  const getTypeDescription = (type) => {
    const descriptions = {
      base: '基础字段是事件表中的标准字段，如 ds、role_id、account_id 等。',
      param: '事件参数是存储在 params 字段中的 JSON 参数，需要使用 get_json_object 提取。',
      custom: '自定义字段是用户定义的特殊字段类型。',
    };
    return descriptions[type] || '';
  };

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={handleCancel}
      title="编辑参数类型"
      size="md"
      glassmorphism
    >
      <div className="space-y-6">
        {/* Current Parameter Info */}
        <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
          <div className="text-sm text-slate-400 mb-1">当前参数</div>
          <div className="flex items-center gap-2">
            <code className="text-cyan-400 font-semibold text-lg">{parameter.paramName}</code>
            {parameter.paramNameCn && (
              <span className="text-slate-300">({parameter.paramNameCn})</span>
            )}
          </div>
        </div>

        {/* Type Selection */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            新的参数类型
          </label>
          <Select
            options={typeOptions}
            value={newType}
            onChange={setNewType}
            placeholder="选择参数类型"
          />
        </div>

        {/* Type Description */}
        {newType && (
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="text-sm text-blue-300">{getTypeDescription(newType)}</div>
            </div>
          </div>
        )}

        {/* Warning Message */}
        <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-yellow-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <div className="text-sm text-yellow-300">
              修改参数类型可能会影响HQL生成。请确保您了解此变更的影响。
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
          <Button
            variant="secondary"
            onClick={handleCancel}
            disabled={isSubmitting || mutationLoading}
          >
            取消
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={isSubmitting || mutationLoading || newType === parameter.type}
            loading={isSubmitting || mutationLoading}
          >
            确认修改
          </Button>
        </div>
      </div>
    </BaseModal>
  );
};

export default ParameterTypeEditor;
