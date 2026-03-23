import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useOutletContext, useSearchParams, useNavigate } from 'react-router-dom';

// Components
import EventNodeBuilderErrorBoundary from '../components/ErrorBoundary';
import PageHeader from '../components/PageHeader';
import { QuickActionButtons } from '../components/QuickActionButtons';
import { LeftSidebar } from '../components/LeftSidebar';
import { RightSidebar } from '../components/RightSidebar';
import FieldCanvas from '../components/FieldCanvas';
import { FieldConfigModal } from '../components/modals/FieldConfigModal';
import { ConfigListModal } from '../components/modals/ConfigListModal';
import { WhereBuilderModal } from '../components/WhereBuilder/WhereBuilderModal';
import { HQLPreviewModal } from '../components/HQLPreview/HQLPreviewModal';
import { NodeConfigModal } from '../components/modals/NodeConfigModal';
import { FieldSelectionModal } from '../components/FieldSelectionModal';
import { ConfirmDialog } from '@shared/ui';
import { LoadingState } from './components/LoadingState';
import { PerformancePanel } from './components/PerformancePanel';
import { DebugPanel } from './components/DebugPanel';
import ErrorBoundary from '@shared/components/ErrorBoundary';

// Hooks
import { useToast } from '@features/canvas/components/hooks/useToast';
import { useGameContext } from '@shared/hooks/useGameContext';
import { useEventNodeBuilder } from '@shared/hooks/useEventNodeBuilder';
import { useEventNodeBuilderData } from "./hooks/useEventNodeBuilderData";

// Types
import type { Game } from '@shared/hooks/useGameContext';
import type { Event } from '@shared/types/api-types';
import type { CanvasField, WhereCondition } from '@shared/hooks/useEventNodeBuilder';
import type { OutletContext, ConfigData, FieldUpdate, DragDropField, ConfirmState } from "./EventNodeBuilder.types";

// 样式
import './EventNodeBuilder.css';

const EventNodeBuilder = React.memo(function EventNodeBuilder(): React.JSX.Element {
  // 路由和上下文
  const { currentGame } = (useOutletContext() as OutletContext) || {};
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // Toast
  const { success, error, warning } = useToast();
  const [confirmState, setConfirmState] = useState<ConfirmState>({
    open: false,
    onConfirm: () => {},
    title: '',
    message: ''
  });

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

  // 使用自定义 hook 处理数据加载和保存
  const { saveMutation } = useEventNodeBuilderData({
    gameData,
    configIdParam,
    selectedEvent,
    canvasFields,
    nodeConfig,
    whereConditions,
    onSetSelectedEvent: setSelectedEvent,
    onSetCanvasFields: setCanvasFields,
    onSetWhereConditions: setWhereConditions,
    onSetNodeConfig: setNodeConfig,
  });

  // UI状态
  const [editingField, setEditingField] = useState<CanvasField | null>(null);
  const [showConfigList, setShowConfigList] = useState<boolean>(false);
  const [showWhereConfig, setShowWhereConfig] = useState<boolean>(false);
  const [showHQLDetails, setShowHQLDetails] = useState<boolean>(false);
  const [showNodeConfig, setShowNodeConfig] = useState<boolean>(false);
  const [showFieldSelection, setShowFieldSelection] = useState<boolean>(false);

  // 性能分析和调试模式面板状态
  const [showPerformancePanel, setShowPerformancePanel] = useState<boolean>(false);
  const [showDebugPanel, setShowDebugPanel] = useState<boolean>(false);

  // V2 API功能切换（默认启用V2）
  const [useV2API, setUseV2API] = useState<boolean>(true);

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
            const game = result.data.find((g: Game) => String(g.gid) === String(gameGidParam));
            if (game) {
              selectGame(game);
              return;
            }
          }
        } catch (err) {
          console.error('[EventNodeBuilder] Failed to fetch game:', err);
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

    // Show field selection modal when event is selected
    if (selectedEvent) {
      setShowFieldSelection(true);
    }
  }, [selectedEvent, clearCanvas]);

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

    const configData: ConfigData = {
      game_gid: gameData!.gid,
      event_id: (selectedEvent as Event).id,
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
      filter_conditions: JSON.stringify({
        custom_where: whereConditions.length > 0
          ? whereConditions.map(c => `${c.field || ''} ${c.operator || '='} '${c.value || ''}'`).join(' AND ')
          : '',
        conditions: whereConditions
      }),
    };

    saveMutation.mutate(configData);
  }, [gameData, selectedEvent, canvasFields, nodeConfig, whereConditions, saveMutation, warning]);

  // 处理字段编辑
  const handleFieldEdit = useCallback((field: CanvasField) => {
    setEditingField(field);
  }, []);

  // 处理字段删除
  const handleFieldDelete = useCallback((fieldId: string) => {
    removeField(fieldId);
  }, [removeField]);

  // 处理字段保存
  const handleFieldSave = useCallback(async (updates: FieldUpdate) => {
    if (!editingField) return;

    // 检查是否需要同步更新参数中文名称
    if (editingField.fieldType === 'param' && updates.displayName && updates.displayName !== editingField.displayName) {
      setConfirmState({
        open: true,
        title: '确认同步更新',
        message: `检测到您修改了参数字段的中文名称：\n\n原名称：${editingField.displayName}\n新名称：${updates.displayName}\n\n是否同步更新参数数据库中的中文名称？`,
        onConfirm: async () => {
          setConfirmState(s => ({ ...s, open: false }));
          try {
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
          } catch (err) {
            const errorObj = err as Error;
            console.error('[EventNodeBuilder] 更新参数异常:', err);
            error(`更新参数异常：${errorObj.message}`);
          }
        }
      });
    }

    // 更新字段
    updateField(editingField.id, updates as Partial<CanvasField>);
    setEditingField(null);
  }, [editingField, updateField, error]);

  /**
   * Handle batch fields added from FieldSelectionModal or QuickActionButtons
   */
  const handleFieldsAdded = useCallback((fields: Array<{
    fieldType?: string;
    type?: string;
    fieldName?: string;
    name?: string;
    displayName?: string;
    paramId?: number | null;
    jsonPath?: string | null;
  }>) => {
    if (!Array.isArray(fields)) return;

    fields.forEach((field) => {
      const fieldType = field.fieldType || field.type || 'param';
      const fieldName = field.fieldName || field.name || '';
      const displayName = field.displayName || fieldName;

      addFieldToCanvas(
        fieldType,
        fieldName,
        displayName,
        field.paramId,
        field.jsonPath
      );
    });

    success(`已添加 ${fields.length} 个字段到画布`);
  }, [addFieldToCanvas, success]);

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
    return <LoadingState />;
  }

  return (
    <EventNodeBuilderErrorBoundary>
      <ErrorBoundary>
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
          >
            {/* Quick Action Buttons in Header */}
            {selectedEvent && (
              <QuickActionButtons
                eventId={(selectedEvent as Event).id}
                onFieldsAdded={handleFieldsAdded}
              />
            )}
          </PageHeader>

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
              onAddField={(field: DragDropField) => {
                // Handle drag-drop from canvas
                if (field.fieldType) {
                  // FieldSelectorPanel passes dataType, but drag-drop uses hive_type
                  const hiveType = (field as any).dataType || field.hive_type;
                  addFieldToCanvas(field.fieldType, field.fieldName!, field.displayName!, field.paramId, undefined, hiveType);
                } else if (field.type) {
                  // Handle from @dnd-kit system
                  const fieldType = field.type === 'parameter' ? 'param' : field.type;
                  addFieldToCanvas(fieldType, field.name!, field.alias || field.name!, field.sourceId, field.hive_type);
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

          {/* Field Selection Modal */}
          {showFieldSelection && selectedEvent && (
            <FieldSelectionModal
              isOpen={showFieldSelection}
              onClose={() => setShowFieldSelection(false)}
              eventId={(selectedEvent as Event).id}
              onFieldsAdded={handleFieldsAdded}
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
          <PerformancePanel
            show={showPerformancePanel}
            onClose={() => setShowPerformancePanel(false)}
          />

          {/* 调试模式面板 */}
          <DebugPanel
            show={showDebugPanel}
            onClose={() => setShowDebugPanel(false)}
          />
        </div>
      </ErrorBoundary>
    </EventNodeBuilderErrorBoundary>
  );
});

EventNodeBuilder.displayName = 'EventNodeBuilder';

export default EventNodeBuilder;