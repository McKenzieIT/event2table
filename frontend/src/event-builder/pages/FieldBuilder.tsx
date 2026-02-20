// @ts-nocheck - TypeScript检查暂禁用
import React, { useState, useCallback, useEffect, useMemo, useRef } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  fetchEvents,
  fetchEventParameters,
  saveFieldConfig,
  loadFieldConfig,
  previewHQL
} from '@shared/api/fieldBuilder';
import { Field, FieldType, DataType, FieldConfig, SQLMode } from '@shared/types/fieldBuilder';
import { generateId, validateField } from '@shared/utils/fieldBuilder';
import FieldEventSelector from '@event-builder/components/FieldEventSelector';
import FieldCanvas from '@event-builder/components/FieldCanvas';
import HQLPreview from '@event-builder/components/HQLPreview';
import { Button } from '@shared/ui/Button';
import { useToast } from '@shared/ui/Toast/Toast';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';
import './FieldBuilder.css';

/**
 * Field Builder Page - Container Component
 *
 * Main container for the Field Builder feature that allows users to:
 * - Select events from a game
 * - Build field configurations by dragging parameters
 * - Preview generated HQL in real-time
 * - Save and load field configurations
 *
 * URL Parameters:
 * - gameGid (required): Game GID
 * - eventId (optional): Pre-selected event ID
 * - configId (optional): Load saved configuration
 *
 * @component
 * @example
 * // Basic usage with game context
 * <FieldBuilder />
 *
 * // With pre-selected event
 * /field-builder?gameGid=10000147&eventId=123
 *
 * // With saved configuration
 * /field-builder?gameGid=10000147&configId=456
 */
function FieldBuilder() {
  // URL parameters
  const { gameGid } = useParams();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  // Parse URL parameters
  const urlGameGid = parseInt(searchParams.get('gameGid') || gameGid || '0');
  const urlEventId = searchParams.get('eventId') ? parseInt(searchParams.get('eventId')) : null;
  const urlConfigId = searchParams.get('configId') ? parseInt(searchParams.get('configId')) : null;

  // Local state
  const [selectedEventId, setSelectedEventId] = useState(urlEventId);
  const [fields, setFields] = useState([]);
  const [sqlMode, setSqlMode] = useState('view');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [configName, setConfigName] = useState('');
  const [customHQL, setCustomHQL] = useState('');
  const [hqlLoading, setHqlLoading] = useState(false);
  const [confirmState, setConfirmState] = useState({ open: false, onConfirm: () => {}, title: '', message: '' });

  // Toast
  const { warning, error } = useToast();

  // Refs
  const hqlPreviewRef = useRef(null);
  const handleSaveRef = useRef(null);
  const handleCloseRef = useRef(null);

  // React Query client
  const queryClient = useQueryClient();

  // Fetch events for the game
  const {
    data: events = [],
    isLoading: eventsLoading,
    error: eventsError
  } = useQuery({
    queryKey: ['events', urlGameGid],
    queryFn: () => fetchEvents(urlGameGid),
    enabled: !!urlGameGid,
    retry: 1
  });

  // Fetch event parameters when event is selected
  const {
    data: parameters = [],
    isLoading: parametersLoading,
    error: parametersError
  } = useQuery({
    queryKey: ['event-parameters', selectedEventId],
    queryFn: () => selectedEventId ? fetchEventParameters(selectedEventId) : [],
    enabled: !!selectedEventId,
    retry: 1
  });

  // Load saved configuration if configId is provided
  const {
    data: savedConfig,
    isLoading: configLoading,
    error: configError
  } = useQuery({
    queryKey: ['field-config', urlConfigId],
    queryFn: () => urlConfigId ? loadFieldConfig(urlConfigId) : null,
    enabled: !!urlConfigId,
    retry: 1,
    onSuccess: (config) => {
      if (config) {
        setSelectedEventId(config.eventId);
        setFields(config.fields);
        setSqlMode(config.mode);
        setConfigName(config.name);
        setHasUnsavedChanges(false);
      }
    }
  });

  // Save configuration mutation
  const saveMutation = useMutation({
    mutationFn: (config) => saveFieldConfig(config),
    onSuccess: (data) => {
      setHasUnsavedChanges(false);
      queryClient.invalidateQueries({ queryKey: ['field-config'] });
    },
    onError: (error) => {
      console.error('Failed to save configuration:', error);
      error('保存失败: ' + (error?.message || '请稍后重试'));
    }
  });

  // Generate HQL preview using useMemo for derived state
  const hqlPreview = useMemo(() => {
    if (fields.length === 0 || !selectedEventId) return '';
    try {
      return previewHQL(fields, selectedEventId, sqlMode);
    } catch (error) {
      console.error('[FieldBuilder] Failed to generate HQL:', error);
      error('HQL生成失败: ' + (error?.message || '未知错误'));
      return '';
    }
  }, [fields, selectedEventId, sqlMode]);

  // Update URL when selected event changes
  useEffect(() => {
    if (selectedEventId) {
      setSearchParams({ gameGid: urlGameGid.toString(), eventId: selectedEventId.toString() });
    } else {
      setSearchParams({ gameGid: urlGameGid.toString() });
    }
  }, [selectedEventId, urlGameGid, setSearchParams]);

  // Warn before navigation with unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (hasUnsavedChanges) {
        e.preventDefault();
        e.returnValue = '';
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [hasUnsavedChanges]);

  // Initialize fields from event parameters
  useEffect(() => {
    if (parameters.length > 0 && fields.length === 0 && !savedConfig) {
      // Create initial fields from parameters
      const initialFields = parameters.map((param, index) => ({
        id: generateId(),
        type: FieldType.PARAMETER,
        sourceId: param.id,
        name: param.name,
        alias: param.alias || param.name,
        dataType: param.dataType,
        isEditable: true
      }));
      setFields(initialFields);
    }
  }, [parameters, fields.length, savedConfig]);

  // Handle event selection
  const handleEventSelect = useCallback((eventId) => {
    if (hasUnsavedChanges) {
      setConfirmState({
        open: true,
        title: '确认切换事件',
        message: '有未保存的更改，确定要切换事件吗？',
        onConfirm: () => {
          setConfirmState(s => ({ ...s, open: false }));
          setSelectedEventId(eventId);
          setFields([]);
          setHasUnsavedChanges(false);
        }
      });
      return;
    }
    setSelectedEventId(eventId);
    setFields([]); // Clear fields for new event
    setHasUnsavedChanges(false);
  }, [hasUnsavedChanges]);

  // Handle field add
  const handleAddField = useCallback((field) => {
    setFields(prev => [...prev, field]);
    setHasUnsavedChanges(true);
  }, []);

  // Handle field update
  const handleUpdateField = useCallback((fieldId, updates) => {
    setFields(prev =>
      prev.map(field =>
        field.id === fieldId ? { ...field, ...updates } : field
      )
    );
    setHasUnsavedChanges(true);
  }, []);

  // Handle field remove
  const handleRemoveField = useCallback((fieldId) => {
    setFields(prev => prev.filter(field => field.id !== fieldId));
    setHasUnsavedChanges(true);
  }, []);

  // Handle fields reorder
  const handleReorderFields = useCallback((fields) => {
    setFields(fields);
    setHasUnsavedChanges(true);
  }, []);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!selectedEventId) {
      warning('请先选择一个事件');
      return;
    }

    // Validate fields
    const errors = fields.flatMap(field => validateField(field));
    if (errors.length > 0) {
      error('字段配置有错误:\n' + errors.join('\n'));
      return;
    }

    const config = {
      name: configName || `配置_${new Date().toISOString()}`,
      gameGid: urlGameGid,
      eventId: selectedEventId,
      fields,
      mode: sqlMode
    };

    saveMutation.mutate(config);
  }, [selectedEventId, fields, configName, urlGameGid, sqlMode, saveMutation]);

  // 保存最新的handleSave到ref
  handleSaveRef.current = handleSave;

  // Handle close
  const handleClose = useCallback(() => {
    if (hasUnsavedChanges) {
      setConfirmState({
        open: true,
        title: '确认关闭',
        message: '有未保存的更改，确定要关闭吗？',
        onConfirm: () => {
          setConfirmState(s => ({ ...s, open: false }));
          navigate(-1);
        }
      });
      return;
    }
    navigate(-1); // Go back to previous page
  }, [hasUnsavedChanges, navigate]);

  // 保存最新的handleClose到ref
  handleCloseRef.current = handleClose;

  // Handle SQL mode toggle
  const handleModeToggle = useCallback((mode) => {
    setSqlMode(mode);
    setHasUnsavedChanges(true);
  }, []);

  // Handle HQL content change (memoized to prevent unnecessary re-renders)
  const handleHQLContentChange = useCallback((content) => {
    setCustomHQL(content);
    setHasUnsavedChanges(true);
  }, []);

  // Handle fields change (memoized to prevent unnecessary re-renders of FieldCanvas)
  const handleFieldsChange = useCallback((newFields) => {
    setFields(newFields);
    setHasUnsavedChanges(true);
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl/Cmd + S to save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        handleSaveRef.current?.();
      }
      // Escape to close
      if (e.key === 'Escape') {
        handleCloseRef.current?.();
      }
      // Ctrl/Cmd + Shift + F to format HQL
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'F') {
        e.preventDefault();
        hqlPreviewRef.current?.format();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []); // 空依赖数组，使用ref来获取最新的函数

  // Get selected event details (memoized to prevent recalculation on every render)
  // 必须在所有return之前调用，避免违反Hooks规则
  const selectedEvent = useMemo(
    () => events.find(e => e.id === selectedEventId),
    [events, selectedEventId]
  );

  // Memoize disabled state for save button to prevent unnecessary re-renders
  const isSaveDisabled = useMemo(
    () => !selectedEventId || fields.length === 0 || saveMutation.isLoading,
    [selectedEventId, fields.length, saveMutation.isLoading]
  );

  // Loading state
  if (eventsLoading || configLoading) {
    return (
      <div className="field-builder-page">
        <div className="loading-state">
          <i className="bi bi-arrow-repeat"></i>
          <p>加载中...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (eventsError || configError) {
    return (
      <div className="field-builder-page">
        <div className="error-state">
          <span>⚠️</span>
          <p>加载失败</p>
          <Button variant="outline-primary" onClick={() => navigate(-1)}>
            返回
          </Button>
        </div>
      </div>
    );
  }

  // Invalid gameGid
  if (!urlGameGid) {
    return (
      <div className="field-builder-page">
        <div className="error-state">
          <span>⚠️</span>
          <p>缺少游戏上下文</p>
          <Button variant="outline-primary" onClick={() => navigate('/games')}>
            选择游戏
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="field-builder-page" data-testid="field-builder-page">
      {/* Page Header */}
      <div className="page-header glass-card" data-testid="page-header">
        <div className="header-left">
          <h1>字段构建器</h1>
          {selectedEvent && (
            <div className="header-context">
              <span className="badge badge-primary">{selectedEvent.name}</span>
              <span className="text-secondary">
                {fields.length} 个字段
              </span>
            </div>
          )}
        </div>

        <div className="header-actions">
          {hasUnsavedChanges && (
            <span className="unsaved-indicator">
              ⚠️
              未保存
            </span>
          )}

          <div className="sql-mode-toggle">
            <Button
              variant={sqlMode === 'view' ? 'primary' : 'outline-secondary'}
              size="sm"
              onClick={() => handleModeToggle('view')}
            >
              视图模式
            </Button>
            <Button
              variant={sqlMode === 'procedure' ? 'primary' : 'outline-secondary'}
              size="sm"
              onClick={() => handleModeToggle('procedure')}
            >
              存储过程
            </Button>
          </div>

          <Button
            variant="outline-secondary"
            onClick={handleClose}
            disabled={saveMutation.isLoading}
            data-testid="close-button"
          >
            关闭
          </Button>
          <Button
            variant="primary"
            onClick={handleSave}
            disabled={isSaveDisabled}
            data-testid="save-button"
          >
            {saveMutation.isLoading ? '保存中...' : '保存'}
          </Button>
        </div>
      </div>

      {/* Three-Panel Layout */}
      <div className="field-builder-layout">
        {/* Left Panel: Event Selector */}
        <div className="event-selector-panel glass-card" data-testid="event-selector-panel">
          {eventsLoading ? (
            <div className="loading-state">
              <i className="bi bi-arrow-repeat spin"></i>
              <p>加载事件中...</p>
            </div>
          ) : eventsError ? (
            <div className="error-state">
              <i className="bi bi-exclamation-triangle"></i>
              <p>加载事件失败</p>
            </div>
          ) : (
            <FieldEventSelector
              events={events}
              selectedEventId={selectedEventId}
              onEventSelect={handleEventSelect}
            />
          )}
        </div>

        {/* Center Panel: Field Canvas */}
        <div className="field-canvas-panel glass-card" data-testid="field-canvas-panel">
          {!selectedEventId ? (
            <div className="panel-content">
              <div className="empty-state">
                <i className="bi bi-arrow-left"></i>
                <p>请从左侧选择一个事件</p>
              </div>
            </div>
          ) : (
            <FieldCanvas
              fields={fields}
              parameters={parameters}
              onFieldsChange={handleFieldsChange}
              onAddField={handleAddField}
              onRemoveField={handleRemoveField}
              onUpdateField={handleUpdateField}
              onReorderFields={handleReorderFields}
              isLoading={parametersLoading}
              hasError={parametersError}
            />
          )}
        </div>

        {/* Right Panel: HQL Preview */}
        <HQLPreview
          ref={hqlPreviewRef}
          hqlContent={hqlPreview}
          sqlMode={sqlMode}
          onModeChange={setSqlMode}
          onContentChange={handleHQLContentChange}
          readOnly={false}
          fields={fields}
          isLoading={hqlLoading}
          data-testid="hql-preview-panel"
        />
      </div>

      <ConfirmDialog
        open={confirmState.open}
        title={confirmState.title}
        message={confirmState.message}
        confirmText="确认"
        cancelText="取消"
        variant="warning"
        onConfirm={confirmState.onConfirm}
        onCancel={() => setConfirmState(s => ({ ...s, open: false }))}
      />
    </div>
  );
}

export default FieldBuilder;
