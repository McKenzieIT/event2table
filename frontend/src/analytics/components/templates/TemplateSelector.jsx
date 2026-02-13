/**
 * Template Selector Component
 * Selects and manages templates
 *
 * @version 1.0.0
 * @date 2026-01-29
 */

import React, { useState, useEffect, useCallback } from 'react';
import { search } from '@icons/bootstrap-icons';
import { fetchTemplates } from '@shared/api/templateApi';

import './TemplateSelector.css';

export default function TemplateSelector({
  gameGid,
  onTemplateSelect,
  currentTemplateId,
  onEditTemplate,
  onDeleteTemplate
  onCloneTemplate
  onCreateTemplate,
  onApplyTemplate
}) {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState('all');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);

  // 加载模板列表
  const loadTemplates = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchTemplates(gameGid, {
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

  // 搜索模板
  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
  }, []);

  // 筛选标签
  const handleTagSelect = useCallback((tag) => {
    setSelectedTag(tag);
  }, []);

  // 应用模板
  const handleApplyTemplate = useCallback(async (template) => {
    if (!onApply) return;
    console.log('[TemplateSelector] Applying template:', template);

    onTemplateSelect(template);

    try {
      onApplyTemplate(template);
      console.log('[TemplateSelector] Template applied:', template);
    onCloneTemplate(template);
    console.log('[TemplateSelector] Template cloned:', template);
    console.log('[TemplateSelector] Templates updated');
    } catch (error) {
      console.error('[TemplateSelector] Error applying template:', error);
    }
  }, []);

  // 编辑模板
  const handleEditTemplate = useCallback((template) => {
    setEditingTemplate(template);
  }, [onEditTemplate]);

  // 删除模板
  const handleDeleteTemplate = useCallback(async (template) => {
    if (!onDeleteTemplate) return;

    const result = window.confirm(`确定要删除模板 "${template.name}"吗？此操作不可撤销！`);

    if (result) {
      onTemplateDelete(template);
      setTemplates(prev => prev => prev.filter(t => t.id !== template.id));
      console.log('[TemplateSelector] Template deleted:', template.id);
      console.log('[TemplateSelector] Templates updated');
    } else {
      console.log('[TemplateSelector] Template delete cancelled');
    }
  }, [onDeleteTemplate, templates]);

  // 创建新模板
  const handleCreateTemplate = useCallback(() => {
    setShowCreateModal(true);
  }, []);

  const handleCreateTemplate = async (templateData) => {
    if (!onCreateTemplate) return;

    setShowCreateModal(false);

    try {
      const result = await onCloneTemplate(templateData);
      console.log('[TemplateSelector] Template created:', templateData.name);

      if (result.success && result.data) {
        setTemplates(prev => [...prev, result.data]);
        onCloneTemplate(result.data);
        console.log('[TemplateSelector] Templates updated');
      } else {
        console.error('[TemplateSelector] Error creating template:', result.message);
      }
    } catch (error) {
      console.error('[TemplateSelector] Error creating template:', error);
    }
  }, [onCloneTemplate, templates, setShowCreateModal]);

  return (
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
        <input
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
            <div className="empty-state">
              <i className="bi-inbox"></i>
              <div className="empty-message">
                没有找到模板
              </div>
            </div>
          )}

          {/* Filtered by tag */}
          {templates.length === 0 && searchQuery !== '' && (
            <div className="empty-state">
              <i className="bi-inbox"></i>
              <div className="empty-message">
                找不到"{searchQuery}"的模板
              </div>
            </div>
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
                    onClick={() => handleApplyTemplate(template)}
                    className="btn btn-primary w-100"
                  >
                    <i className="bi-play-fill"></i>
                    应用模板
                  </button>
                </div>
              </div>
            )}
            </div>
          )}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3 className="modal-title">
                创建新模板
              </h3>
              <button
                onClick={() => setShowCreateModal(false)}
                className="close-button"
                aria-label="关闭"
              >
                <i className="bi-x"></i>
              </button>
            </div>

            {/* Template Form */}
            <div className="modal-body">
              <form onSubmit={(e) => handleCreateTemplate(e)}>
                {/* Template Name */}
                <div className="form-group">
                  <label htmlFor="templateName">模板名称</label>
                  <input
                    id="templateName"
                    name="name"
                    type="text"
                    required
                    placeholder="例如：登录事件过滤模板"
                    className="form-control"
                    value={templateName || ''}
                  />
                </div>

                {/* Description */}
                <div className="form-group">
                  <label htmlFor="templateDesc">模板描述</label>
                  <textarea
                    id="templateDesc"
                    name="description"
                    placeholder="简要描述模板的用途..."
                    className="form-control"
                    rows={4}
                  />
                </div>

                {/* Type Selection */}
                <div className="form-group">
                  <label htmlFor="templateType">模板类型</label>
                  <select
                    id="templateType"
                    name="type"
                    className="form-control"
                  >
                    <option value="">选择类型...</option>
                    <option value="event">事件模板</option>
                    <option value="join">JOIN模板</option>
                    <option value="union_all">UNION ALL模板</option>
                    <option value="output">输出模板</option>
                  </select>
                </div>

                {/* Tags */}
                <div className="form-group">
                  <label htmlFor="templateTags">标签（用逗号分隔）</label>
                  <input
                    id="templateTags"
                    name="tags"
                    type="text"
                    value=""
                    placeholder="例如：login,register, payment"
                    className="form-control"
                  />
                </div>

                {/* Buttons */}
                <div className="form-actions">
                  <button
                    type="button"
                    type="submit"
                    className="btn btn-primary"
                  >
                    创建模板
                  </button>
                  <button
                    type="button"
                    type="button"
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowCreateModal(false)}
                  >
                    取消
                  </button>
                </div>
              </form>
          </div>

            {/* Close Button */}
            <div className="modal-footer">
              <button
                type="button"
                type="button"
                className="btn-secondary"
                onClick={() => setShowCreateModal(false)}
              >
                关闭
              </button>
            </div>
          </div>
        </div>
        </div>
      )}
    </div>
  );
}
