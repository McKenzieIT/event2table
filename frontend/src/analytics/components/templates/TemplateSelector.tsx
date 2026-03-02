// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * Template Selector Component
 * Selects and manages templates
 *
 * @version 1.0.0
 * @date 2026-01-29
 */

import React, { useState, useEffect, useCallback } from 'react';
import { fetchTemplates } from '@shared/api/templateApi';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import { Input, EmptyState } from '@shared/ui';

import './TemplateSelector.css';

/**
 * Template interface
 */
interface Template {
  id: string | number;
  name: string;
  type?: string;
  tags?: string[];
  description?: string;
  created_at: string;
}

/**
 * Confirm State interface
 */
interface ConfirmState {
  open: boolean;
  template: Template | null;
  title: string;
  message: string;
}

/**
 * Template Selector Props interface
 */
interface TemplateSelectorProps {
  gameGid: number | string;
  onTemplateSelect?: (template: Template) => void;
  currentTemplateId?: string | number;
  onEditTemplate?: (template: Template) => void;
  onDeleteTemplate?: (template: Template) => void;
  onCloneTemplate?: (template: Template) => void;
  onCreateTemplate?: (template: Partial<Template>) => void;
  onApplyTemplate?: (template: Template) => Promise<{ success: boolean }>;
}

export default function TemplateSelector({
  gameGid,
  onTemplateSelect,
  onEditTemplate,
  onDeleteTemplate,
  onCloneTemplate,
  onCreateTemplate,
  onApplyTemplate,
}: TemplateSelectorProps): React.JSX.Element {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedTag, setSelectedTag] = useState<string>('all');
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [confirmState, setConfirmState] = useState<ConfirmState>({
    open: false,
    template: null,
    title: '删除模板',
    message: ''
  });

  // Load templates
  const loadTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchTemplates(Number(gameGid), {
        search: searchQuery,
        type: selectedTag
      });

      if (result.success && result.data) {
        setTemplates(result.data);
      } else {
        console.error('[TemplateSelector] Failed to load templates:', result.message);
      }
    } catch (error) {
      console.error('[TemplateSelector] Error loading templates:', error);
    } finally {
      setLoading(false);
    }
  }, [gameGid, searchQuery, selectedTag]);

  // Load templates on mount
  useEffect(() => {
    loadTemplates();
  }, [loadTemplates]);

  // Search templates
  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  // Filter tags
  const handleTagSelect = useCallback((tag: string) => {
    setSelectedTag(tag);
  }, []);

  // Apply template
  const handleApplyClick = useCallback(async (template: Template) => {
    if (!onApplyTemplate) return;

    if (onTemplateSelect) {
      onTemplateSelect(template);
    }

    try {
      const result = await onApplyTemplate(template);
      if (result.success) {
        console.log('[TemplateSelector] Template applied successfully');
      }
    } catch (error) {
      console.error('[TemplateSelector] Error applying template:', error);
    }
  }, [onApplyTemplate, onTemplateSelect]);

  // Edit template
  const handleEditTemplate = useCallback((template: Template) => {
    if (onEditTemplate) {
      onEditTemplate(template);
    }
  }, [onEditTemplate]);

  // Clone template
  const handleCloneTemplate = useCallback((template: Template) => {
    if (onCloneTemplate) {
      onCloneTemplate(template);
    }
  }, [onCloneTemplate]);

  // Delete template
  const handleDeleteTemplate = useCallback(async (template: Template) => {
    if (!onDeleteTemplate) return;

    setConfirmState({
      open: true,
      template,
      title: '删除模板',
      message: `确定要删除模板 "${template.name}" 吗？此操作不可撤销！`
    });
  }, [onDeleteTemplate]);

  const handleConfirmDelete = useCallback(() => {
    if (confirmState.template && onDeleteTemplate) {
      onDeleteTemplate(confirmState.template);
      setTemplates(prev => prev.filter(t => t.id !== confirmState.template!.id));
    }
    setConfirmState(prev => ({ ...prev, open: false }));
  }, [confirmState.template, onDeleteTemplate]);

  const handleCancelDelete = useCallback(() => {
    setConfirmState(prev => ({ ...prev, open: false }));
  }, []);

  // Create new template
  const handleCreateTemplate = useCallback(() => {
    setShowCreateModal(true);
  }, []);

  const handleCloseCreateModal = useCallback(() => {
    setShowCreateModal(false);
  }, []);

  return (
    <>
      <div className="template-selector">
        {/* Header */}
        <div className="template-selector-header">
          <h3 className="title">📋 模板系统</h3>
          <p className="subtitle">快速创建和复用查询模板</p>
        </div>

        {/* Tags Filter */}
        <div className="tags-filter">
          <div className="filter-container">
            <button
              className={`tag-btn ${selectedTag === 'all' ? 'active' : ''}`}
              onClick={() => handleTagSelect('all')}
            >
              全部模板
            </button>
            {['event', 'join', 'union_all', 'output'].map(tag => (
              <button
                key={tag}
                className={`tag-btn ${selectedTag === tag ? 'active' : ''}`}
                onClick={() => handleTagSelect(tag)}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* Search Bar */}
        <div className="search-bar">
          <i className="bi bi-search"></i>
          <Input
            type="text"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            placeholder="搜索模板..."
            className="search-input"
          />
          <button
            className="search-btn"
            onClick={() => loadTemplates()}
            disabled={loading}
          >
            <i className="bi-search"></i>
            搜索
          </button>
        </div>

        {/* Templates List */}
        {loading ? (
          <div className="templates-container loading">
            <div className="spinner"></div>
            <p>加载模板...</p>
          </div>
        ) : (
          <>
            {/* Empty State */}
            {templates.length === 0 && searchQuery === '' && (
              <EmptyState
                icon={<i className="bi bi-inbox" style={{ fontSize: '48px' }} />}
                title="没有找到模板"
              />
            )}

            {/* Filtered by tag */}
            {templates.length === 0 && searchQuery !== '' && (
              <EmptyState
                icon={<i className="bi bi-inbox" style={{ fontSize: '48px' }} />}
                title={`找不到"${searchQuery}"的模板`}
              />
            )}

            {/* No Templates */}
            {templates.length > 0 && (
              <div className="templates-list">
                {templates.map(template => (
                  <div key={template.id} className="template-card">
                    {/* Template Card */}
                    <div className="template-header">
                      <div className="template-name">{template.name}</div>
                      <div className="template-meta">
                        <span className="template-type">{template.type || 'event'}</span>
                        <span className="template-tags">
                          {template.tags && template.tags.map(tag => (
                            <span key={tag} className="tag-label">{tag}</span>
                          ))}
                        </span>
                      </div>
                      <div className="template-date">
                        {new Date(template.created_at).toLocaleDateString()}
                      </div>
                      <div className="template-actions">
                        {/* Edit */}
                        <button
                          onClick={() => handleEditTemplate(template)}
                          className="btn btn-sm btn-outline-primary"
                          title="编辑模板"
                        >
                          <i className="bi bi-pencil"></i>
                        </button>
                        {/* Clone */}
                        <button
                          onClick={() => handleCloneTemplate(template)}
                          className="btn btn-sm btn-outline-secondary"
                          title="复制模板"
                        >
                          <i className="bi-files"></i>
                        </button>
                        {/* Delete */}
                        <button
                          onClick={() => handleDeleteTemplate(template)}
                          className="btn btn-sm btn-outline-danger"
                          title="删除模板"
                        >
                          <i className="bi-trash"></i>
                        </button>
                      </div>
                    </div>

                    {/* Description */}
                    <div className="template-description">
                      {template.description}
                    </div>

                    {/* Apply Template */}
                    <button
                      onClick={() => handleApplyClick(template)}
                      className="btn btn-primary w-100"
                    >
                      <i className="bi-play-fill"></i>
                      应用模板
                    </button>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* Create Modal - Simplified for now */}
        {showCreateModal && (
          <div className="modal-overlay">
            <div className="modal-content">
              <div className="modal-header">
                <h3 className="modal-title">
                  创建新模板
                </h3>
                <button
                  onClick={handleCloseCreateModal}
                  className="close-button"
                  aria-label="关闭"
                >
                  <i className="bi-x"></i>
                </button>
              </div>

              {/* Placeholder for template creation form */}
              <div className="modal-body">
                <p>模板创建功能待实现</p>
              </div>

              {/* Close Button */}
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={handleCloseCreateModal}
                >
                  关闭
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <ConfirmDialog
        open={confirmState.open}
        title={confirmState.title}
        message={confirmState.message}
        confirmText="删除"
        cancelText="取消"
        variant="danger"
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
      />
    </>
  );
}
