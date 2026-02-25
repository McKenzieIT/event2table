/**
 * NodeConfigForm Component
 * 节点配置表单组件
 */
import React from 'react';
import { Input } from '@shared/ui';

export default function NodeConfigForm({ config, onChange, disabled }) {
  const handleChange = (field, value) => {
    onChange({ ...config, [field]: value });
  };

  return (
    <div className="sidebar-section glass-card-dark node-config-section">
      <div className="section-header">
        <h3>
          <i className="bi bi-gear"></i>
                   节点配置
        </h3>
      </div>
      <div className="section-content">
        <Input
          id="configNameEn"
          label="英文名称 *"
          type="text"
          placeholder="例如: login_event_node"
          value={config.nameEn}
          onChange={(e) => handleChange('nameEn', e.target.value)}
          disabled={disabled}
        />

        <Input
          id="configNameCn"
          label="中文名称 *"
          type="text"
          placeholder="例如: 登录事件节点"
          value={config.nameCn}
          onChange={(e) => handleChange('nameCn', e.target.value)}
          disabled={disabled}
        />

        <div className="form-group">
          <label htmlFor="configDescription">描述</label>
          <textarea
            id="configDescription"
            className="glass-input"
            placeholder="节点配置说明（可选）"
            value={config.description}
            onChange={(e) => handleChange('description', e.target.value)}
            disabled={disabled}
            rows="3"
          />
        </div>
      </div>
    </div>
  );
}
