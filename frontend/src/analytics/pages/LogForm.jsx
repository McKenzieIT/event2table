import React, { useState, useCallback, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { Button, Input } from '@shared/ui';
import { Spinner } from '@shared/ui';
import { useFormValidation } from '../../shared/hooks/useFormValidation';
import './LogForm.css';

/**
 * 日志表单组件
 * 创建/编辑日志配置
 * 最佳实践: useCallback + 提前返回 + useMemo
 */
function LogForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const isEdit = !!id;

  const [formData, setFormData] = useState({
    log_type: '',
    source_table: '',
    target_table: '',
    params_fields: [],
    can_join_with: []
  });

  const validationRules = {
    log_type: { required: true, message: '日志类型不能为空' },
    source_table: { required: true, message: '源表不能为空' },
    target_table: { required: true, message: '目标表不能为空' }
  };

  const { errors, touched, handleBlur, validateAll } = useFormValidation(formData, validationRules);

  // 并行加载数据（编辑模式）
  const { data: initialData, isLoading } = useQuery({
    queryKey: ['log', id],
    queryFn: async () => {
      if (!isEdit) return null;
      const response = await fetch(`/api/logs/${id}`);
      if (!response.ok) throw new Error('加载日志配置失败');
      return response.json();
    },
    enabled: isEdit,
    onSuccess: (data) => {
      // data 是 queryFn 的返回值，即 { success: true, data: {...} }
      if (data?.success && data?.data) {
        setFormData({
          log_type: data.data.log_type || '',
          source_table: data.data.source_table || '',
          target_table: data.data.target_table || '',
          params_fields: data.data.params_fields || [],
          can_join_with: data.data.can_join_with || []
        });
      }
    }
  });

  // 提交mutation
  const mutation = useMutation({
    mutationFn: async (data) => {
      const url = isEdit ? `/api/logs/${id}` : '/api/logs';
      const method = isEdit ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.message || '操作失败');
      }

      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['logs']);
      navigate('/events');
    },
    onError: (error) => {
      // Use setErrors from hook to show submit errors
    }
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateAll()) return;
    if (mutation.isLoading) return;

    try {
      await mutation.mutateAsync(formData);
    } catch (error) {
      // Error handled in mutation onError
    }
  };

  // 添加字段
  const addField = useCallback(() => {
    setFormData(prev => ({
      ...prev,
      params_fields: [...prev.params_fields, { name: '', type: 'string', comment: '' }]
    }));
  }, []);

  // 删除字段
  const removeField = useCallback((index) => {
    setFormData(prev => ({
      ...prev,
      params_fields: prev.params_fields.filter((_, i) => i !== index)
    }));
  }, []);

  // 更新字段
  const updateField = useCallback((index, field, value) => {
    setFormData(prev => ({
      ...prev,
      params_fields: prev.params_fields.map((f, i) =>
        i === index ? { ...f, [field]: value } : f
      )
    }));
  }, []);

  // 添加关联日志
  const addJoinableLog = useCallback(() => {
    setFormData(prev => ({
      ...prev,
      can_join_with: [...prev.can_join_with, '']
    }));
  }, []);

  // 更新关联日志
  const updateJoinableLog = useCallback((index, value) => {
    setFormData(prev => ({
      ...prev,
      can_join_with: prev.can_join_with.map((log, i) =>
        i === index ? value : log
      )
    }));
  }, []);

  // 自动填充表名
  useEffect(() => {
    if (formData.log_type && !isEdit) {
      const logType = formData.log_type.replace(/\./g, '_');
      if (!formData.source_table) {
        setFormData(prev => ({ ...prev, source_table: `ods_${logType}` }));
      }
      if (!formData.target_table) {
        setFormData(prev => ({ ...prev, target_table: `dwd_${logType}` }));
      }
    }
  }, [formData.log_type, isEdit]);

  if (isLoading) {
    return (
      <div className="loading-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spinner size="lg" label="加载中..." />
      </div>
    );
  }

  return (
    <div className="log-form-container">
      <div className="page-header">
        <h1>{isEdit ? '编辑日志' : '新增日志'}</h1>
        <Link to="/events" className="btn btn-outline-secondary">
          <i className="bi bi-arrow-left"></i>
          返回
        </Link>
      </div>

      <form onSubmit={handleSubmit} className="form-card glass-card">

        <div className="form-row">
          <Input
            id="log_type"
            name="log_type"
            label="日志类型 *"
            type="text"
            value={formData.log_type}
            onChange={(e) => setFormData({ ...formData, log_type: e.target.value })}
            onBlur={handleBlur ? () => handleBlur('log_type') : undefined}
            placeholder="例如: card.gacha"
            readOnly={isEdit}
            error={touched.log_type && errors.log_type ? errors.log_type : undefined}
            helperText="使用点号分隔的格式，如: card.gacha, user.login"
            icon="bi-tag"
          />

          <Input
            id="source_table"
            name="source_table"
            label="源表 (ODS) *"
            type="text"
            value={formData.source_table}
            onChange={(e) => setFormData({ ...formData, source_table: e.target.value })}
            onBlur={handleBlur ? () => handleBlur('source_table') : undefined}
            placeholder="例如: ods_card_gacha"
            error={touched.source_table && errors.source_table ? errors.source_table : undefined}
            icon="bi-database"
          />
        </div>

        <Input
          id="target_table"
          name="target_table"
          label="目标表 (DWD) *"
          type="text"
          value={formData.target_table}
          onChange={(e) => setFormData({ ...formData, target_table: e.target.value })}
          onBlur={handleBlur ? () => handleBlur('target_table') : undefined}
          placeholder="例如: dwd_card_gacha"
          error={touched.target_table && errors.target_table ? errors.target_table : undefined}
          icon="bi-table"
        />

        <div className="form-divider"></div>

        <h5 className="section-title">参数字段 (params_fields)</h5>
        <p className="section-description">定义需要从JSON params字段中解析的字段</p>

        <div className="fields-container">
          {formData.params_fields.map((field, index) => (
            <div key={index} className="field-row glass-card">
              <div className="field-grid">
                <div className="field-item">
                  <Input
                    label="字段名"
                    type="text"
                    value={field.name}
                    onChange={(e) => updateField(index, 'name', e.target.value)}
                    required
                  />
                </div>
                <div className="field-item">
                  <label>类型</label>
                  <select
                    className="form-control"
                    value={field.type}
                    onChange={(e) => updateField(index, 'type', e.target.value)}
                  >
                    <option value="string">string</option>
                    <option value="int">int</option>
                    <option value="bigint">bigint</option>
                    <option value="decimal(10,2)">decimal(10,2)</option>
                  </select>
                </div>
                <div className="field-item comment">
                  <Input
                    label="说明"
                    type="text"
                    value={field.comment}
                    onChange={(e) => updateField(index, 'comment', e.target.value)}
                  />
                </div>
                <div className="field-item action">
                  <label>&nbsp;</label>
                  <button
                    type="button"
                    className="btn btn-sm btn-outline-danger"
                    onClick={() => removeField(index)}
                  >
                    <i className="bi bi-trash"></i>
                    <span>删除</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <button
          type="button"
          className="btn btn-outline-primary"
          onClick={addField}
        >
          <i className="bi bi-plus-circle"></i>
          <span>添加字段</span>
        </button>

        <div className="form-divider"></div>

        <h5 className="section-title">可关联日志</h5>
        <p className="section-description">选择可以与此日志关联的其他日志类型</p>

        <div className="form-group">
          <div className="joinable-logs-container">
            {formData.can_join_with.map((log, index) => (
              <Input
                key={index}
                type="text"
                className="joinable-log"
                value={log}
                onChange={(e) => updateJoinableLog(index, e.target.value)}
                placeholder="输入日志类型，例如: item.change"
              />
            ))}
          </div>
          <button
            type="button"
            className="btn btn-outline-primary"
            onClick={addJoinableLog}
          >
            <i className="bi bi-plus-circle"></i>
            <span>添加关联日志</span>
          </button>
        </div>

        <div className="form-actions">
          <Button
            variant="primary"
            type="submit"
            loading={mutation.isLoading}
          >
            <i className="bi bi-check-circle" aria-hidden="true"></i>
            {mutation.isLoading ? '提交中...' : (isEdit ? '保存修改' : '创建日志')}
          </Button>
          <Button variant="secondary" onClick={() => navigate('/events')}>
            <i className="bi bi-x-circle" aria-hidden="true"></i>
            取消
          </Button>
        </div>
      </form>
    </div>
  );
}

export default LogForm;
