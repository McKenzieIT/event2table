/**
 * BindToLibraryModal 组件 - 绑定到参数库弹窗
 *
 * 显示匹配的库参数，允许用户选择并绑定
 *
 * @example
 * <BindToLibraryModal
 *   paramId={123}
 *   paramName="accountId"
 *   templateId={1}
 *   onClose={() => setShowModal(false)}
 * />
 *
 * Props:
 * @param {number} paramId - 参数ID
 * @param {string} paramName - 参数名
 * @param {number} templateId - 类型ID
 * @param {Function} onClose - 关闭回调
 */

import React, { useEffect, useState } from 'react';
import { Button } from '../ui/Button';
import toast from 'react-hot-toast';

export function BindToLibraryModal({ paramId, paramName, templateId, onClose, onSuccess }) {
  const [matchedParams, setMatchedParams] = useState([]);
  const [selectedLibraryId, setSelectedLibraryId] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 调用 API 检查匹配的库参数
    fetch(`/api/param-library/check?param_name=${paramName}&template_id=${templateId}`)
      .then(res => res.json())
      .then(data => {
        if (data.success && data.data.exists) {
          setMatchedParams([data.data.library_param]);
          setSelectedLibraryId(data.data.library_param.id);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to check library:', err);
        toast.error('检查参数库失败');
        setLoading(false);
      });
  }, [paramName, templateId]);

  const handleConfirm = async () => {
    if (!selectedLibraryId) {
      toast.error('请选择要绑定的库参数');
      return;
    }

    try {
      const res = await fetch(`/api/event-params/${paramId}/link-library`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ library_id: selectedLibraryId })
      });

      const data = await res.json();

      if (data.success) {
        toast.success('参数已绑定到库');
        onClose();
        if (onSuccess) {
          onSuccess();
        } else {
          window.location.reload();
        }
      } else {
        toast.error('绑定失败：' + (data.error || '未知错误'));
      }
    } catch (err) {
      console.error('Failed to link to library:', err);
      toast.error('绑定失败');
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass-card" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h4>绑定到参数库</h4>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <div className="mb-3">
            <div><strong>参数名:</strong> {paramName}</div>
            <div><strong>类型:</strong> {templateId}</div>
          </div>

          {loading ? (
            <div>加载中...</div>
          ) : matchedParams.length > 0 ? (
            <div>
              <h5>匹配的库参数:</h5>
              {matchedParams.map(param => (
                <label key={param.id} className="d-block mb-2">
                  <input
                    type="radio"
                    name="library_param"
                    checked={selectedLibraryId === param.id}
                    onChange={() => setSelectedLibraryId(param.id)}
                  />
                  <span className="ms-2">
                    {param.param_name} ({param.param_name_cn})
                    <small className="text-muted"> - 使用次数: {param.usage_count}</small>
                  </span>
                </label>
              ))}
            </div>
          ) : (
            <div className="text-muted">
              未找到匹配的库参数
            </div>
          )}
        </div>
        <div className="modal-footer">
          <Button variant="secondary" onClick={onClose}>
            取消
          </Button>
          <Button variant="primary" onClick={handleConfirm} disabled={!selectedLibraryId}>
            确认绑定
          </Button>
        </div>
      </div>
    </div>
  );
}
