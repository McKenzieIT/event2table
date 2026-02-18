/**
 * PageHeader Component
 * 页面头部组件
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@shared/ui/Button';

export default function PageHeader({
  gameData,
  onClearCanvas,
  onSaveConfig,
  onLoadConfig,
  onOpenNodeConfig,
  useV2API,
  setUseV2API,
  showPerformancePanel,
  setShowPerformancePanel,
  showDebugPanel,
  setShowDebugPanel
}) {
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
        {/* 性能分析面板（可折叠） */}
        <button
          className={`btn btn-sm ${showPerformancePanel ? 'btn-info' : 'btn-outline-info'}`}
          onClick={() => setShowPerformancePanel(!showPerformancePanel)}
          style={{ marginRight: '8px' }}
          title="性能分析面板"
        >
          <i className="bi bi-speedometer2"></i> 性能分析
        </button>

        {/* 调试模式面板（可折叠） */}
        <button
          className={`btn btn-sm ${showDebugPanel ? 'btn-secondary' : 'btn-outline-secondary'}`}
          onClick={() => setShowDebugPanel(!showDebugPanel)}
          style={{ marginRight: '12px' }}
          title="调试模式面板"
        >
          <i className="bi bi-bug"></i> 调试模式
        </button>
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
          <Button variant="secondary" onClick={onLoadConfig}>
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
