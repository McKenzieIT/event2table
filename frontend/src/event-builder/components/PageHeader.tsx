// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * PageHeader Component
 * 页面头部组件
 */
import React, { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@shared/ui';

interface GameData {
  name: string;
  gid: string | number;
}

interface PageHeaderProps {
  gameData?: GameData | null;
  onClearCanvas?: () => void;
  onSaveConfig?: () => void;
  onLoadConfig?: () => void;
  onOpenNodeConfig?: () => void;
  useV2API?: boolean;
  setUseV2API?: (value: boolean) => void;
  showPerformancePanel?: boolean;
  setShowPerformancePanel?: (value: boolean) => void;
  showDebugPanel?: boolean;
  setShowDebugPanel?: (value: boolean) => void;
  children?: ReactNode;
}

export default function PageHeader({
  gameData,
  onClearCanvas,
  onSaveConfig,
  onLoadConfig,
  onOpenNodeConfig,
  useV2API,
  setUseV2API,
  showPerformancePanel = false,
  setShowPerformancePanel,
  showDebugPanel = false,
  setShowDebugPanel,
  children
}: PageHeaderProps) {
  return (
    <header className="page-header">
      <div className="header-left">
        <h1 className="page-title">
          📊 事件节点构建器
        </h1>
        {gameData && (
          <div className="header-info">
            <span>
              <strong>游戏:</strong> {gameData.name} | <strong>GID:</strong> {gameData.gid}
            </span>
          </div>
        )}
      </div>
      <div className="header-right">
        {/* Performance Analysis Panel (collapsible) */}
        {setShowPerformancePanel && (
          <button
            className={`btn btn-sm ${showPerformancePanel ? 'btn-info' : 'btn-outline-info'}`}
            onClick={() => setShowPerformancePanel(!showPerformancePanel)}
            style={{ marginRight: '8px' }}
            title="性能分析面板"
            type="button"
          >
            <i className="bi bi-speedometer2"></i> 性能分析
          </button>
        )}

        {/* Debug Mode Panel (collapsible) */}
        {setShowDebugPanel && (
          <button
            className={`btn btn-sm ${showDebugPanel ? 'btn-secondary' : 'btn-outline-secondary'}`}
            onClick={() => setShowDebugPanel(!showDebugPanel)}
            style={{ marginRight: '12px' }}
            title="调试模式面板"
            type="button"
          >
            <i className="bi bi-bug"></i> 调试模式
          </button>
        )}

        {/* Children (e.g., QuickActionButtons) */}
        {children}

        {onClearCanvas && (
          <Button variant="secondary" onClick={onClearCanvas}>
            清空画布
          </Button>
        )}
        {onOpenNodeConfig && (
          <Button variant="outline-primary" onClick={onOpenNodeConfig}>
            节点配置
          </Button>
        )}
        {onSaveConfig && (
          <Button variant="primary" onClick={onSaveConfig}>
            保存配置
          </Button>
        )}
        {onLoadConfig && (
          <Button variant="secondary" onLoadConfig={onLoadConfig}>
            加载配置
          </Button>
        )}
        <Link to="/canvas">
          <Button variant="outline-secondary">
            返回
          </Button>
        </Link>
      </div>
    </header>
  );
}
