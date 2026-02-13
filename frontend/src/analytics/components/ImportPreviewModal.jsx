/**
 * ImportPreviewModal 组件 - 批量导入预览弹窗
 *
 * 显示批量导入时参数匹配结果，允许用户选择哪些参数关联到库
 *
 * @example
 * <ImportPreviewModal
 *   parameters={[
 *     { param_name: 'accountId', template_id: 1, libraryParam: {...} },
 *     { param_name: 'customField', template_id: 1, libraryParam: null }
 *   ]}
 *   onConfirm={(selected) => console.log('Importing', selected)}
 *   onCancel={() => setShowModal(false)}
 * />
 *
 * Props:
 * @param {Array} parameters - 参数列表（包含 libraryParam 字段表示是否匹配）
 * @param {Function} onConfirm - 确认导入回调
 * @param {Function} onCancel - 取消回调
 */

import React, { useState } from 'react';
import { Button } from '@shared/ui';

export function ImportPreviewModal({ parameters, onConfirm, onCancel }) {
  const [selectedMatches, setSelectedMatches] = useState(new Set());

  const matched = parameters.filter(p => p.libraryParam);
  const unmatched = parameters.filter(p => !p.libraryParam);

  const handleToggleMatch = (index) => {
    const newSelected = new Set(selectedMatches);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    setSelectedMatches(newSelected);
  };

  const handleLinkAll = () => {
    const newSelected = new Set(selectedMatches);
    matched.forEach((_, index) => newSelected.add(index));
    setSelectedMatches(newSelected);
  };

  const handleConfirm = () => {
    onConfirm(selectedMatches);
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-content glass-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h4>导入预览</h4>
          <button className="modal-close" onClick={onCancel}>✕</button>
        </div>
        <div className="modal-body">
          <div className="import-stats mb-3">
            <div>共 {parameters.length} 个参数</div>
            <div className="text-success">✓ 可关联到库: {matched.length} 个</div>
            <div className="text-warning">⚠ 未匹配: {unmatched.length} 个</div>
          </div>

          {matched.length > 0 && (
            <div className="matched-params mb-3">
              <h5>可关联的参数 ({matched.length})</h5>
              {matched.map((param, index) => (
                <div key={index} className="param-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={selectedMatches.has(index)}
                      onChange={() => handleToggleMatch(index)}
                    />
                    {param.param_name} → 库中存在 ({param.libraryParam?.template_name})
                  </label>
                </div>
              ))}
            </div>
          )}

          {unmatched.length > 0 && (
            <div className="unmatched-params">
              <h5>未匹配的参数 ({unmatched.length})</h5>
              {unmatched.map((param, index) => (
                <div key={index} className="param-item">
                  {param.param_name}
                </div>
              ))}
            </div>
          )}
        </div>
        <div className="modal-footer">
          <Button variant="secondary" onClick={onCancel}>
            取消
          </Button>
          <Button variant="primary" onClick={handleLinkAll}>
            全部关联
          </Button>
          <Button variant="primary" onClick={handleConfirm}>
            开始导入
          </Button>
        </div>
      </div>
    </div>
  );
}
