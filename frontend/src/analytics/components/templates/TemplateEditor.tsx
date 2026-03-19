/**
 * Template Editor Component
 * 模板编辑器组件
 *
 * @version 1.0.0
 * @date 2026-03-19
 */

import React, { useState, useEffect, useCallback } from 'react';
import type { Template } from '@shared/api/templateApi';
import { fetchTemplate, createTemplate, updateTemplate, deleteTemplate } from '@shared/api/templateApi';
import { Button, Input, TextArea, Modal, ConfirmDialog } from '@shared/ui';

import './TemplateEditor.css';

/**
 * Template Editor Props interface
 */
interface TemplateEditorProps {
  templateId?: number | null;
  gameGid?: number;
  isOpen: boolean;
  onClose: () => void;
  onSave?: (template: Template) => void;
  onDelete?: () => void;
}

export default function TemplateEditor({
  templateId,
  gameGid,
  isOpen,
  onClose,
  onSave,
  onDelete,
}: TemplateEditorProps): React.JSX.Element {
  const [template, setTemplate] = useState<Partial<Template>>({
    name: '',
    content: '',
    category: '',
    description: '',
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<boolean>(false);

  // Load template data when editing
  const loadTemplate = useCallback(async () => {
    if (!templateId) {
      setTemplate({
        name: '',
        content: '',
        category: '',
        description: '',
      });
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await fetchTemplate(templateId);
      if (data) {
        setTemplate(data);
      } else {
        setError('模板不存在');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载模板失败');
    } finally {
      setLoading(false);
    }
  }, [templateId]);

  // Load template when modal opens or templateId changes
  useEffect(() => {
    if (isOpen) {
      loadTemplate();
    }
  }, [isOpen, loadTemplate]);

  // Handle input changes
  const handleChange = useCallback((field: keyof Template, value: string) => {
    setTemplate(prev => ({ ...prev, [field]: value }));
    setError(null);
  }, []);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!template.name?.trim()) {
      setError('模板名称不能为空');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      let result;
      if (templateId) {
        result = await updateTemplate(templateId, template);
      } else {
        result = await createTemplate(template as Omit<Template, 'id' | 'createdAt' | 'updatedAt'>);
      }

      if (result.success && result.template) {
        if (onSave) {
          onSave(result.template);
        }
        onClose();
      } else {
        setError(result.error || '保存失败');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setSaving(false);
    }
  }, [template, templateId, onSave, onClose]);

  // Handle delete
  const handleDelete = useCallback(() => {
    setShowDeleteConfirm(true);
  }, []);

  // Confirm delete
  const handleConfirmDelete = useCallback(async () => {
    if (!templateId) return;

    try {
      const result = await deleteTemplate(templateId);
      if (result.success) {
        if (onDelete) {
          onDelete();
        }
        onClose();
      } else {
        setError(result.error || '删除失败');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败');
    } finally {
      setShowDeleteConfirm(false);
    }
  }, [templateId, onDelete, onClose]);

  // Cancel delete
  const handleCancelDelete = useCallback(() => {
    setShowDeleteConfirm(false);
  }, []);

  // Handle key press
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleSave();
    }
  }, [handleSave]);

  if (!isOpen) return <></>;

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} title={templateId ? '编辑模板' : '新建模板'}>
        <div className="template-editor">
          {loading ? (
            <div className="template-editor-loading">
              <div className="spinner"></div>
              <p>加载中...</p>
            </div>
          ) : (
            <>
              {/* Error message */}
              {error && (
                <div className="template-editor-error">
                  <i className="bi bi-exclamation-circle"></i>
                  {error}
                </div>
              )}

              {/* Template name */}
              <div className="form-group">
                <label htmlFor="template-name">
                  模板名称 <span className="required">*</span>
                </label>
                <Input
                  id="template-name"
                  type="text"
                  value={template.name || ''}
                  onChange={(e) => handleChange('name', e.target.value)}
                  placeholder="输入模板名称..."
                  onKeyDown={handleKeyPress}
                />
              </div>

              {/* Template category */}
              <div className="form-group">
                <label htmlFor="template-category">分类</label>
                <Input
                  id="template-category"
                  type="text"
                  value={template.category || ''}
                  onChange={(e) => handleChange('category', e.target.value)}
                  placeholder="输入分类（如：event, join, union_all）..."
                  onKeyDown={handleKeyPress}
                />
              </div>

              {/* Template description */}
              <div className="form-group">
                <label htmlFor="template-description">描述</label>
                <Input
                  id="template-description"
                  type="text"
                  value={template.description || ''}
                  onChange={(e) => handleChange('description', e.target.value)}
                  placeholder="输入模板描述..."
                  onKeyDown={handleKeyPress}
                />
              </div>

              {/* Template content */}
              <div className="form-group">
                <label htmlFor="template-content">
                  模板内容 <span className="required">*</span>
                </label>
                <TextArea
                  id="template-content"
                  value={template.content || ''}
                  onChange={(e) => handleChange('content', e.target.value)}
                  placeholder="输入模板内容..."
                  rows={15}
                  onKeyDown={handleKeyPress}
                />
                <div className="form-hint">
                  提示：按 Ctrl/Cmd + Enter 快速保存
                </div>
              </div>

              {/* Actions */}
              <div className="template-editor-actions">
                <div className="template-editor-actions-left">
                  {templateId && (
                    <Button
                      variant="danger"
                      onClick={handleDelete}
                      disabled={saving}
                    >
                      <i className="bi bi-trash"></i>
                      删除
                    </Button>
                  )}
                </div>
                <div className="template-editor-actions-right">
                  <Button
                    variant="secondary"
                    onClick={onClose}
                    disabled={saving}
                  >
                    取消
                  </Button>
                  <Button
                    variant="primary"
                    onClick={handleSave}
                    disabled={saving}
                  >
                    {saving ? (
                      <>
                        <div className="spinner-small"></div>
                        保存中...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-lg"></i>
                        {templateId ? '更新' : '创建'}
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </>
          )}
        </div>
      </Modal>

      {/* Delete confirmation dialog */}
      <ConfirmDialog
        open={showDeleteConfirm}
        title="删除模板"
        message={`确定要删除模板 "${template.name}" 吗？此操作不可撤销！`}
        confirmText="删除"
        cancelText="取消"
        variant="danger"
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
      />
    </>
  );
}
