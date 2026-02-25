/**
 * AddGameModalGraphQL - 添加游戏模态框（GraphQL版本）
 *
 * 使用GraphQL Mutation替代REST API
 */

import React, { ChangeEvent, FormEvent } from 'react';
import { BaseModal, Button, Input, Select, useToast } from '@shared/ui';
import { useCreateGame } from '../../graphql/hooks';
import { useFormValidation } from '@shared/hooks/useFormValidation';
import { gameValidationRules } from '@shared/utils/validationUtils';
import './AddGameModal.css';

interface AddGameModalGraphQLProps {
  isOpen: boolean;
  onClose: () => void;
}

interface FormData {
  gid: string;
  name: string;
  odsDb: string;
}

const AddGameModalGraphQL: React.FC<AddGameModalGraphQLProps> = ({ isOpen, onClose }) => {
  const { success, error: showError } = useToast();

  const {
    formData,
    errors,
    touched,
    handleChange,
    handleBlur,
    validateForm,
    resetForm,
    setFormData,
  } = useFormValidation<FormData>(
    { gid: '', name: '', odsDb: 'ieu_ods' },
    gameValidationRules
  );

  // GraphQL Mutation
  const [createGame, { loading: isSubmitting }] = useCreateGame();

  // Handle submit
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      const { data } = await createGame({
        variables: {
          gid: parseInt(formData.gid),
          name: formData.name,
          odsDb: formData.odsDb
        }
      });

      if (data?.createGame?.ok) {
        success('游戏创建成功');
        // Reset form
        setFormData({
          gid: '',
          name: '',
          odsDb: 'ieu_ods'
        });
        onClose();
      } else {
        showError(data?.createGame?.errors?.[0] || '创建失败');
      }
    } catch (err: any) {
      showError(`创建失败: ${err.message}`);
    }
  };

  // Handle close
  const handleClose = () => {
    resetForm();
    onClose();
  };

  return (
    <BaseModal isOpen={isOpen} onClose={handleClose} title="添加游戏" size="md">
      <form onSubmit={handleSubmit} className="add-game-form">
        <Input
            id="gid"
            label="游戏GID"
            required
            type="text"
            value={formData.gid}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('gid', e.target.value)}
            placeholder="请输入游戏GID（数字）"
            error={touched.gid && errors.gid}
            onBlur={() => handleBlur('gid')}
          />
          {touched.gid && errors.gid && <span className="error-message">{errors.gid}</span>}

        <div className="form-group">
          <Input
            id="name"
            label="游戏名称"
            required
            type="text"
            value={formData.name}
            onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange('name', e.target.value)}
            onBlur={() => handleBlur('name')}
            placeholder="请输入游戏名称"
            error={touched.name && errors.name}
          />
          {touched.name && errors.name && <span className="error-message">{errors.name}</span>}
        </div>

        <div className="form-group">
          <Select
            id="odsDb"
            label="ODS数据库"
            required
            value={formData.odsDb}
            onChange={(e: ChangeEvent<HTMLSelectElement>) => handleChange('odsDb', e.target.value)}
            onBlur={() => handleBlur('odsDb')}
            options={[
              { value: 'ieu_ods', label: 'ieu_ods' },
              { value: 'overseas_ods', label: 'overseas_ods' }
            ]}
          />
          {touched.odsDb && errors.odsDb && <span className="error-message">{errors.odsDb}</span>}
        </div>

        <div className="form-actions">
          <Button type="button" onClick={handleClose} variant="secondary">
            取消
          </Button>
          <Button type="submit" variant="primary" loading={isSubmitting}>
            {isSubmitting ? '创建中...' : '创建游戏'}
          </Button>
        </div>
      </form>
    </BaseModal>
  );
};

export default AddGameModalGraphQL;