// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * NodeConfigForm Component
 * 节点配置表单组件
 */
import { Input } from '@shared/ui';
import React from 'react';

/**
 * 节点配置接口
 */
export interface NodeConfig {
  nameEn: string;
  nameCn: string;
  description?: string;
}

/**
 * 组件Props接口
 */
export interface NodeConfigFormProps {
  config: NodeConfig;
  onChange: (config: NodeConfig) => void;
  disabled?: boolean;
}

/**
 * NodeConfigForm Component
 */
export default function NodeConfigForm({ config, onChange, disabled = false }: NodeConfigFormProps) {
  const handleChange = (field: keyof NodeConfig, value: string) => {
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
            value={config.description || ''}
            onChange={(e) => handleChange('description', e.target.value)}
            disabled={disabled}
            rows={3}
          />
        </div>
      </div>
    </div>
  );
}
