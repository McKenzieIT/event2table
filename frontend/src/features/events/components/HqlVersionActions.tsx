/**
 * HqlVersionActions Component
 *
 * Action buttons for HQL version management (save, rollback, compare)
 *
 * @example
 * ```tsx
 * <HqlVersionActions
 *   eventId={123}
 *   currentHql="SELECT * FROM table"
 *   onSaveSuccess={() => {}}
 *   onRollbackSuccess={() => {}}
 *   onCompare={(v1, v2) => {}}
 * />
 * ```
 */

import { Button, useToast } from '@shared/ui';
import React, { useState, useCallback } from 'react';

import type { HqlVersion } from '../api/hqlVersionApi';
import { useSaveHqlVersion, useRollbackHqlVersion } from '../hooks';
import './HqlVersionActions.css';

interface HqlVersionActionsProps {
  eventId: number;
  currentHql: string;
  selectedVersion?: HqlVersion | null;
  compareVersion?: HqlVersion | null;
  onSaveSuccess?: (version: HqlVersion) => void;
  onRollbackSuccess?: (version: HqlVersion) => void;
  onCompare?: (version1: HqlVersion, version2: HqlVersion) => void;
}

const HqlVersionActions: React.FC<HqlVersionActionsProps> = ({
  eventId,
  currentHql,
  selectedVersion,
  compareVersion,
  onSaveSuccess,
  onRollbackSuccess,
  onCompare
}) => {
  const { success, error: showError } = useToast();
  const [showDescriptionInput, setShowDescriptionInput] = useState(false);
  const [description, setDescription] = useState('');

  const saveMutation = useSaveHqlVersion({
    onSuccess: (data) => {
      success('版本保存成功');
      setDescription('');
      setShowDescriptionInput(false);
      onSaveSuccess?.(data.version);
    },
    onError: (err) => {
      showError(`保存失败: ${err.message}`);
    }
  });

  const rollbackMutation = useRollbackHqlVersion({
    onSuccess: (data) => {
      success('回滚成功');
      onRollbackSuccess?.(data.version);
    },
    onError: (err) => {
      showError(`回滚失败: ${err.message}`);
    }
  });

  const handleSave = useCallback(() => {
    if (!currentHql.trim()) {
      showError('HQL内容不能为空');
      return;
    }

    saveMutation.mutate({
      event_id: eventId,
      hql_content: currentHql,
      change_description: description || undefined
    });
  }, [eventId, currentHql, description, saveMutation, showError]);

  const handleRollback = useCallback(() => {
    if (!selectedVersion) {
      showError('请先选择要回滚的版本');
      return;
    }

    rollbackMutation.mutate({
      version_id: selectedVersion.id
    });
  }, [selectedVersion, rollbackMutation, showError]);

  const handleCompare = useCallback(() => {
    if (!selectedVersion || !compareVersion) {
      showError('请先选择两个版本进行对比');
      return;
    }

    onCompare?.(selectedVersion, compareVersion);
  }, [selectedVersion, compareVersion, onCompare, showError]);

  const isSaving = saveMutation.isPending;
  const isRollingBack = rollbackMutation.isPending;
  const canRollback = selectedVersion && !selectedVersion.is_current;
  const canCompare = selectedVersion && compareVersion && selectedVersion.id !== compareVersion.id;

  return (
    <div className="hql-version-actions">
      <div className="actions-header">
        <h6>版本操作</h6>
      </div>
      <div className="actions-buttons">
        {/* Save Version */}
        <div className="action-group">
          {!showDescriptionInput ? (
            <Button
              variant="outline-primary"
              onClick={() => setShowDescriptionInput(true)}
              disabled={isSaving || !currentHql.trim()}
            >
              <i className="bi bi-save"></i>
              {' '}保存版本
            </Button>
          ) : (
            <div className="save-version-input">
              <input
                type="text"
                className="form-control form-control-sm"
                placeholder="输入版本描述（可选）"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSave();
                  } else if (e.key === 'Escape') {
                    setShowDescriptionInput(false);
                    setDescription('');
                  }
                }}
                autoFocus
              />
              <div className="save-actions">
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleSave}
                  disabled={isSaving}
                >
                  <i className={`bi ${isSaving ? 'bi-hourglass-split' : 'bi-check-lg'}`}></i>
                  {' '}{isSaving ? '保存中...' : '保存'}
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => {
                    setShowDescriptionInput(false);
                    setDescription('');
                  }}
                  disabled={isSaving}
                >
                  取消
                </Button>
              </div>
            </div>
          )}
        </div>

        {/* Rollback Version */}
        <div className="action-group">
          <Button
            variant="warning"
            onClick={handleRollback}
            disabled={!canRollback || isRollingBack}
          >
            <i className={`bi ${isRollingBack ? 'bi-hourglass-split' : 'bi-arrow-counterclockwise'}`}></i>
            {' '}{isRollingBack ? '回滚中...' : '回滚到此版本'}
          </Button>
        </div>

        {/* Compare Versions */}
        <div className="action-group">
          <Button
            variant="info"
            onClick={handleCompare}
            disabled={!canCompare}
          >
            <i className="bi bi-code-diff"></i>
            {' '}对比版本
          </Button>
        </div>
      </div>

      {/* Selected Version Info */}
      {selectedVersion && (
        <div className="selected-version-info">
          <div className="info-label">已选择版本:</div>
          <div className="info-content">
            <span className="version-number">v{selectedVersion.version_number}</span>
            {selectedVersion.is_current && (
              <span className="badge badge-success ms-2">当前</span>
            )}
            <span className="version-date text-muted ms-2">
              {new Date(selectedVersion.created_at).toLocaleString('zh-CN')}
            </span>
          </div>
          {selectedVersion.change_description && (
            <div className="version-description">
              {selectedVersion.change_description}
            </div>
          )}
        </div>
      )}

      {/* Compare Version Info */}
      {compareVersion && compareVersion.id !== selectedVersion?.id && (
        <div className="compare-version-info">
          <div className="info-label">对比版本:</div>
          <div className="info-content">
            <span className="version-number">v{compareVersion.version_number}</span>
            <span className="version-date text-muted ms-2">
              {new Date(compareVersion.created_at).toLocaleString('zh-CN')}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default React.memo(HqlVersionActions);