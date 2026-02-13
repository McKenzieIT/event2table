/**
 * PageHeader Component
 * 页面头部组件
 */
import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@shared/ui/Button';

export default function PageHeader({ gameData, onClearCanvas, onSaveConfig, onLoadConfig, onOpenNodeConfig, useV2API, setUseV2API }) {
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
        {/* V2 API 版本切换 */}
        {setUseV2API && (
          <div className="api-version-toggle">
            <label htmlFor="v2-api-toggle" style={{ marginRight: '8px', fontSize: '14px' }}>
              使用新版API (V2):
            </label>
            <input
              id="v2-api-toggle"
              type="checkbox"
              checked={useV2API}
              onChange={(e) => setUseV2API(e.target.checked)}
              style={{ marginRight: '16px' }}
            />
            {useV2API && (
              <span style={{
                fontSize: '12px',
                padding: '4px 8px',
                background: 'rgba(6, 182, 212, 0.2)',
                borderRadius: '4px',
                color: '#06b6d4'
              }}>
                🚀 性能分析 + 调试模式
              </span>
            )}
          </div>
        )}
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
