/**
 * HQLPreviewWrapper - HQL预览V1/V2集成组件
 *
 * 功能：
 * - 提供V1/V2切换功能
 * - 整合所有V2组件
 * - 保持向后兼容
 */

import React, { useState } from 'react';
import HQLPreview from '../HQLPreview';
import { HQLPreviewPanelV2, MultiEventConfigV2, HQLHistoryV2 } from '../HQLPreviewV2';
import type { Event, Field, ConditionValue } from '@shared/types/api-types';
import './HQLPreviewWrapper.css';

interface V1Props {
  events: Array<{
    game_gid: number;
    event_id: number;
    event_name?: string;
    fields?: Field[];
  }>;
  fields: Field[];
  conditions?: Array<{
    field: string;
    operator: string;
    value?: ConditionValue;
    logicalOp?: 'AND' | 'OR';
  }>;
}

interface JoinCondition {
  leftEvent: Event;
  rightEvent: Event;
  leftField: string;
  rightField: string;
  operator: string;
}

interface HQLPreviewWrapperProps {
  // V1 props
  v1Props?: V1Props;

  // V2 props
  events: Array<{
    game_gid: number;
    event_id: number;
    event_name?: string;
    fields?: any[];
  }>;
  fields: Field[];
  conditions?: Array<{
    field: string;
    operator: string;
    value?: ConditionValue;
    logicalOp?: 'AND' | 'OR';
  }>;

  // 可选配置
  defaultVersion?: 'v1' | 'v2';
  showVersionSwitcher?: boolean;
  availableEvents?: Event[];

  // 回调函数
  onHQLGenerated?: (hql: string, version: 'v1' | 'v2') => void;
  onError?: (error: string, version: 'v1' | 'v2') => void;
}

export const HQLPreviewWrapper: React.FC<HQLPreviewWrapperProps> = ({
  v1Props,
  events,
  fields,
  conditions = [],
  defaultVersion = 'v2',
  showVersionSwitcher = true,
  availableEvents = [],
  onHQLGenerated,
  onError
}) => {
  const [version, setVersion] = useState<'v1' | 'v2'>(defaultVersion);
  const [v2History, setV2History] = useState<Field[]>([]);
  const [selectedEvents, setSelectedEvents] = useState<Event[]>([]);
  const [joinConditions, setJoinConditions] = useState<JoinCondition[]>([]);
  const [mode, setMode] = useState<'single' | 'join' | 'union'>('single');

  // V1模式渲染
  const renderV1 = () => {
    return <HQLPreview {...v1Props} />;
  };

  // V2模式渲染
  const renderV2 = () => {
    return (
      <div className="hql-preview-v2-container">
        {/* 版本切换器 */}
        {showVersionSwitcher && (
          <div className="version-switcher">
            <button
              className={`version-btn ${version === 'v1' ? 'active' : ''}`}
              onClick={() => setVersion('v1')}
            >
              V1 (旧版)
            </button>
            <button
              className={`version-btn ${version === 'v2' ? 'active' : ''}`}
              onClick={() => setVersion('v2')}
            >
              V2 (新版)
            </button>
          </div>
        )}

        {/* V2 组件区域 */}
        {version === 'v2' && (
          <>
            {/* 多事件配置 */}
            {mode !== 'single' && (
              <MultiEventConfigV2
                availableEvents={availableEvents}
                selectedEvents={selectedEvents}
                joinConditions={joinConditions}
                onEventsChange={setSelectedEvents}
                onJoinConditionsChange={setJoinConditions}
              />
            )}

            {/* HQL 预览面板 */}
            <HQLPreviewPanelV2
              events={events}
              fields={fields}
              conditions={conditions}
              mode={mode}
              apiBaseUrl="/hql-preview-v2"
              enableCache={true}
              enableHistory={true}
              debugMode={false}
              onHQLGenerated={(hql) => {
                // 添加到历史记录
                const historyItem = {
                  id: Date.now(),
                  hql,
                  timestamp: new Date().toISOString(),
                  events,
                  fields,
                  conditions,
                  mode,
                  options: {
                    sql_mode: 'VIEW',
                    include_comments: true
                  }
                };
                setV2History([historyItem, ...v2History].slice(0, 50)); // 保留最近50条

                if (onHQLGenerated) {
                  onHQLGenerated(hql, 'v2');
                }
              }}
              onError={(error) => {
                if (onError) {
                  onError(error, 'v2');
                }
              }}
            />

            {/* 历史版本 */}
            {v2History.length > 0 && (
              <HQLHistoryV2
                history={v2History}
                onRestore={(item) => {
                  if (onHQLGenerated) {
                    onHQLGenerated(item.hql, 'v2');
                  }
                }}
                onCompare={(v1, v2) => {
                  // TODO: 实现版本对比功能
                }}
              />
            )}
          </>
        )}
      </div>
    );
  };

  return (
    <div className="hql-preview-wrapper">
      {showVersionSwitcher && version === 'v1' ? (
        <>
          {/* V1 顶部切换器 */}
          <div className="version-switcher">
            <button
              className={`version-btn ${version === 'v1' ? 'active' : ''}`}
              onClick={() => setVersion('v1')}
            >
              V1 (旧版)
            </button>
            <button
              className={`version-btn ${version === 'v2' ? 'active' : ''}`}
              onClick={() => setVersion('v2')}
            >
              V2 (新版)
            </button>
          </div>
          {renderV1()}
        </>
      ) : version === 'v1' ? (
        renderV1()
      ) : (
        renderV2()
      )}
    </div>
  );
};

export default HQLPreviewWrapper;
