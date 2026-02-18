/**
 * EventNodeBuilder Component
 * 事件节点构建器主容器组件
 * 用于创建和管理事件节点配置
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useOutletContext, useSearchParams, useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';

// 组件导入
import PageHeader from '@event-builder/components/PageHeader';
import LeftSidebar from '@event-builder/components/LeftSidebar';
import FieldCanvas from '@event-builder/components/FieldCanvas';
import RightSidebar from '@event-builder/components/RightSidebar';
import FieldConfigModal from '@event-builder/components/modals/FieldConfigModal';
import ConfigListModal from '@event-builder/components/modals/ConfigListModal';
import WhereConfigModal from '@event-builder/components/modals/WhereConfigModal';
import WhereBuilderModal from '@event-builder/components/WhereBuilder/WhereBuilderModal';
import HQLPreviewModal from '@event-builder/components/HQLPreview/HQLPreviewModal';
import NodeConfigModal from '@event-builder/components/modals/NodeConfigModal';
import EventNodeBuilderErrorBoundary from '@event-builder/components/ErrorBoundary';
import PerformanceIndicator from '@event-builder/components/HQLPreviewV2/PerformanceIndicator';
import DebugViewer from '@event-builder/components/HQLPreviewV2/DebugViewer';
import { Button } from '@shared/ui/Button';
import { useToast } from '@shared/ui/Toast/Toast';
import { ConfirmDialog } from '@shared/ui/ConfirmDialog/ConfirmDialog';

// Hooks
import { useEventNodeBuilder } from '@shared/hooks/useEventNodeBuilder';
import { useGameContext } from '@shared/hooks/useGameContext';

// API
import { saveConfig, loadConfig } from '@shared/api/eventNodeBuilder';

// 样式
import './EventNodeBuilder.css';

export default function EventNodeBuilder() {
  // 路由和上下文
  const { currentGame } = useOutletContext() || {};
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // Toast
  const { success, error, warning } = useToast();
  const [confirmState, setConfirmState] = useState({ open: false, onConfirm: () => {}, title: '', message: '' });

  // URL 参数
  const configIdParam = searchParams.get('config_id');
  const gameGidParam = searchParams.get('game_gid');

  // 使用统一的useGameContext
  const { currentGame: gameData, selectGame, currentGameGid } = useGameContext();

  // 自定义 Hook
  const {
    selectedEvent,
    setSelectedEvent,
    canvasFields,
    setCanvasFields,
    addFieldToCanvas,
    removeField,
    updateField,
    reorderFields,
    clearCanvas,
    whereConditions,
    setWhereConditions,
    nodeConfig,
    setNodeConfig,
    resetAll,
  } = useEventNodeBuilder(gameData?.gid);

  // UI状态
  const [editingField, setEditingField] = useState(null);
  const [showConfigList, setShowConfigList] = useState(false);
  const [showWhereConfig, setShowWhereConfig] = useState(false);
  const [showHQLDetails, setShowHQLDetails] = useState(false);
  const [showNodeConfig, setShowNodeConfig] = useState(false);

  // 性能分析和调试模式面板状态
  const [showPerformancePanel, setShowPerformancePanel] = useState(false);
  const [showDebugPanel, setShowDebugPanel] = useState(false);

  // V2 API功能切换（默认启用V2）
  const [useV2API, setUseV2API] = useState(true);

  // 保存配置 mutation
  const saveMutation = useMutation({
    mutationFn: (configData) => saveConfig(configData),
    onSuccess: (result) => {
      success(`配置 "${result.data.name_en}" 保存成功！`);
    },
    onError: (error) => {
      error('保存失败: ' + (error.message || '未知错误'));
    },
  });

  // 加载游戏数据 - 简化版，使用统一useGameContext
  useEffect(() => {
    const loadGameData = async () => {
      // 1. 如果useGameContext已有游戏数据，直接使用
      if (gameData) {
        return;
      }

      // 2. 从URL参数加载（仅当没有游戏数据时）
      if (gameGidParam) {
        try {
          const response = await fetch('/api/games');
          const result = await response.json();
          if (result.success && Array.isArray(result.data)) {
            const game = result.data.find(g => String(g.gid) === String(gameGidParam));
            if (game) {
              selectGame(game);
              return;
            }
          }
        } catch (error) {
          console.error('[EventNodeBuilder] Failed to fetch game:', error);
        }
      }

      // 3. 如果仍然没有游戏数据，显示警告
      if (!gameData && !gameGidParam) {
        console.warn('[EventNodeBuilder] No game data available');
      }
    };

    loadGameData();
  }, [gameGidParam, gameData, selectGame]);

  // Clear canvas when selected event changes
  useEffect(() => {
    // Clear canvas fields and WHERE conditions when switching events
    // This ensures users start fresh with each new event selection
    clearCanvas();
  }, [selectedEvent, clearCanvas]);

  // 加载配置（编辑模式）
  useEffect(() => {
    if (configIdParam && gameData) {
      loadConfig(configIdParam).then(result => {
        if (result.success && result.data) {
          const config = result.data;
          // 设置事件
          if (config.event) {
            setSelectedEvent(config.event);
          }
          // 设置字段
          if (config.base_fields && Array.isArray(config.base_fields)) {
            setCanvasFields(config.base_fields.map((f, index) => ({
              id: Date.now() + index,
              fieldType: f.field_type,
              fieldName: f.field_name,
              displayName: f.display_name,
              alias: f.alias || '',
              order: index + 1,
              paramId: f.param_id,
            })));
          }
          // 设置WHERE条件
          if (config.filter_conditions) {
            try {
              const where = typeof config.filter_conditions === 'string'
                ? JSON.parse(config.filter_conditions)
                : config.filter_conditions;
              setWhereConditions(where);
            } catch (e) {
              console.error('[EventNodeBuilder] Failed to parse WHERE conditions:', e);
            }
          }
          // 设置节点配置
          setNodeConfig({
            nameEn: config.name_en || '',
            nameCn: config.name_cn || '',
            description: config.description || '',
          });
        }
      });
    }
  }, [configIdParam, gameData]);

  // 处理保存配置
  const handleSaveConfig = useCallback(() => {
    if (!selectedEvent) {
      warning('请先选择事件');
      return;
    }
    if (canvasFields.length === 0) {
      warning('请至少添加一个字段');
      return;
    }
    if (!nodeConfig.nameEn.trim()) {
      warning('请输入节点英文名称');
      return;
    }
    if (!nodeConfig.nameCn.trim()) {
      warning('请输入节点中文名称');
      return;
    }

    const configData = {
      game_gid: gameData.gid,
      event_id: selectedEvent.id,
      name_en: nodeConfig.nameEn.trim(),
      name_cn: nodeConfig.nameCn.trim(),
      description: nodeConfig.description.trim(),
      base_fields: canvasFields.map(f => ({
        field_type: f.fieldType,
        field_name: f.fieldName,
        display_name: f.displayName,
        alias: f.alias,
        order: f.order,
        param_id: f.paramId,
      })),
      // 将 whereConditions 数组转换为后端期望的字典格式
      filter_conditions: JSON.stringify({
        custom_where: whereConditions.length > 0
          ? whereConditions.map(c => `${c.field || ''} ${c.operator || '='} '${c.value || ''}'`).join(' AND ')
          : '',
        conditions: whereConditions
      }),
    };

    saveMutation.mutate(configData);
  }, [gameData, selectedEvent, canvasFields, nodeConfig, whereConditions, saveMutation]);

  // 处理字段编辑
  const handleFieldEdit = useCallback((field) => {
    setEditingField(field);
  }, []);

  // 处理字段删除
  const handleFieldDelete = useCallback((fieldId) => {
    removeField(fieldId);
  }, [removeField]);

  // 处理字段保存
  const handleFieldSave = useCallback(async (updates) => {
    // 检查是否需要同步更新参数中文名称
    if (editingField.fieldType === 'param' && updates.displayName && updates.displayName !== editingField.displayName) {
      setConfirmState({
        open: true,
        title: '确认同步更新',
        message: `检测到您修改了参数字段的中文名称：\n\n原名称：${editingField.displayName}\n新名称：${updates.displayName}\n\n是否同步更新参数数据库中的中文名称？`,
        onConfirm: async () => {
          setConfirmState(s => ({ ...s, open: false }));
          try {
            // 调用API更新参数中文名称
            const response = await fetch('/event_node_builder/api/update-param-name', {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                param_id: editingField.paramId,
                new_name_cn: updates.displayName,
              }),
            });

            const result = await response.json();
            if (result.success) {
              // 参数中文名称已更新
            } else {
              console.error('[EventNodeBuilder] 更新参数失败:', result.error);
              error(`更新参数失败：${result.error || '未知错误'}`);
            }
          } catch (error) {
            console.error('[EventNodeBuilder] 更新参数异常:', error);
            error(`更新参数异常：${error.message}`);
          }
        }
      });
    }

    // 更新字段
    updateField(editingField.id, updates);
    setEditingField(null);
  }, [editingField, updateField]);

  // 处理清空画布
  const handleClearCanvas = useCallback(() => {
    if (canvasFields.length === 0) return;
    setConfirmState({
      open: true,
      title: '确认清空画布',
      message: '确定要清空画布吗？所有字段和WHERE条件将被删除。',
      onConfirm: () => {
        setConfirmState(s => ({ ...s, open: false }));
        clearCanvas();
      }
    });
  }, [canvasFields.length, clearCanvas]);

  // 加载状态
  if (!gameData) {
    return (
      <div className="event-node-builder-loading">
        <h2>请先选择游戏</h2>
        <p>事件节点构建器需要游戏上下文才能正常工作</p>
        <Button variant="primary" onClick={() => navigate('/games')}>
          前往选择游戏
        </Button>
      </div>
    );
  }

  return (
    <EventNodeBuilderErrorBoundary>
      <div className="event-node-builder" data-testid="event-node-builder">
        <PageHeader
          gameData={gameData}
          onClearCanvas={handleClearCanvas}
          onSaveConfig={handleSaveConfig}
          onLoadConfig={() => setShowConfigList(true)}
          onOpenNodeConfig={() => setShowNodeConfig(true)}
          useV2API={useV2API}
          setUseV2API={setUseV2API}
          showPerformancePanel={showPerformancePanel}
          setShowPerformancePanel={setShowPerformancePanel}
          showDebugPanel={showDebugPanel}
          setShowDebugPanel={setShowDebugPanel}
        />

        <div className="workspace" data-testid="event-node-builder-workspace">
          <LeftSidebar
            gameGid={Number(gameData.gid)}
            selectedEvent={selectedEvent}
            onEventSelect={setSelectedEvent}
            onAddField={addFieldToCanvas}
          />

          <FieldCanvas
            fields={canvasFields}
            onFieldsChange={reorderFields}
            onUpdateField={handleFieldEdit}
            onRemoveField={handleFieldDelete}
            onReorderFields={reorderFields}
            onAddField={(field) => {
              // Handle drag-drop from canvas
              if (field.fieldType) {
                addFieldToCanvas(field.fieldType, field.fieldName, field.displayName, field.paramId);
              } else if (field.type) {
                // Handle from @dnd-kit system
                const fieldType = field.type === 'parameter' ? 'param' : field.type;
                addFieldToCanvas(fieldType, field.name, field.alias || field.name, field.sourceId);
              }
            }}
          />

          <RightSidebar
            gameGid={Number(gameData.gid)}
            selectedEvent={selectedEvent}
            fields={canvasFields}
            whereConditions={whereConditions}
            onWhereConditionsChange={setWhereConditions}
            onShowWhereModal={() => setShowWhereConfig(true)}
            onShowHQLDetails={() => setShowHQLDetails(true)}
          />
        </div>

        {/* 模态框 */}
        {editingField && (
          <FieldConfigModal
            field={editingField}
            onSave={handleFieldSave}
            onClose={() => setEditingField(null)}
            data-testid="field-config-modal"
          />
        )}

        {showConfigList && (
          <ConfigListModal
            gameGid={gameData.gid}
            onSelect={(config) => {
              navigate(`/event-node-builder?config_id=${config.id}&game_gid=${gameData.gid}`);
            }}
            onClose={() => setShowConfigList(false)}
            data-testid="config-list-modal"
          />
        )}

        {showWhereConfig && (
          <WhereBuilderModal
            isOpen={showWhereConfig}
            onClose={() => setShowWhereConfig(false)}
            conditions={whereConditions}
            onConditionsChange={setWhereConditions} // ✅ 新增：实时更新
            onApply={(conditions) => {
              setWhereConditions(conditions);
            }}
            canvasFields={canvasFields}
            selectedEvent={selectedEvent}
            data-testid="where-builder-modal"
          />
        )}

        {showHQLDetails && (
          <HQLPreviewModal
            isOpen={showHQLDetails}
            onClose={() => setShowHQLDetails(false)}
            canvasFields={canvasFields}
            whereConditions={whereConditions}
            gameData={gameData}
            selectedEvent={selectedEvent}
            useV2API={useV2API}
            data-testid="hql-preview-modal"
          />
        )}

        {showNodeConfig && (
          <NodeConfigModal
            config={nodeConfig}
            onChange={setNodeConfig}
            onClose={() => setShowNodeConfig(false)}
            disabled={!selectedEvent || canvasFields.length === 0}
            data-testid="node-config-modal"
          />
        )}

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

        {/* 性能分析面板 */}
        {showPerformancePanel && (
          <div className="panel-overlay" onClick={() => setShowPerformancePanel(false)}>
            <div className="panel-container performance-panel" onClick={(e) => e.stopPropagation()}>
              <div className="panel-header">
                <h3>
                  <i className="bi bi-speedometer2"></i> 性能分析
                </h3>
                <button className="btn btn-sm btn-outline-secondary" onClick={() => setShowPerformancePanel(false)}>
                  <i className="bi bi-x"></i> 关闭
                </button>
              </div>
              <div className="panel-body">
                <div className="panel-placeholder">
                  <i className="bi bi-info-circle"></i>
                  <p>性能数据将在HQL生成后显示</p>
                  <small>请先选择事件并添加字段，然后生成HQL以查看性能分析</small>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 调试模式面板 */}
        {showDebugPanel && (
          <div className="panel-overlay" onClick={() => setShowDebugPanel(false)}>
            <div className="panel-container debug-panel" onClick={(e) => e.stopPropagation()}>
              <div className="panel-header">
                <h3>
                  <i className="bi bi-bug"></i> 调试模式
                </h3>
                <button className="btn btn-sm btn-outline-secondary" onClick={() => setShowDebugPanel(false)}>
                  <i className="bi bi-x"></i> 关闭
                </button>
              </div>
              <div className="panel-body">
                <div className="panel-placeholder">
                  <i className="bi bi-info-circle"></i>
                  <p>调试信息将在HQL生成后显示</p>
                  <small>请先选择事件并添加字段，然后生成HQL以查看调试信息</small>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </EventNodeBuilderErrorBoundary>
  );
}
