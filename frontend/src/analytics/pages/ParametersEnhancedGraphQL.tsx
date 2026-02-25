/**
 * ParametersEnhancedGraphQL - 增强参数管理页面(GraphQL版本)
 *
 * 完整迁移自ParametersEnhanced.jsx,保留所有功能:
 * - 参数列表展示
 * - 搜索和分类过滤
 * - 参数绑定到库
 *
 * 使用GraphQL API替代REST API
 * 使用TypeScript提供类型安全
 */

import React, { useState, useMemo } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import { SelectGamePrompt } from '@shared/ui/SelectGamePrompt';
import { Button, SearchInput, Spinner } from '@shared/ui';
import { BindToLibraryButton } from '@shared/components/BindToLibraryButton';
import { useParametersManagement } from '@/graphql/hooks';
import './ParametersEnhanced.css';

interface Parameter {
  id: number;
  eventId: number;
  paramName: string;
  paramNameCn?: string;
  paramType: string;
  paramDescription?: string;
  jsonPath?: string;
  isActive: boolean;
  version: number;
  usageCount?: number;
  eventsCount?: number;
  isCommon?: boolean;
  eventCode?: string;
  eventName?: string;
  gameGid?: number;
  createdAt?: string;
  updatedAt?: string;
  category?: string;
  library_id?: number;
}

interface GameContext {
  gid: number;
  name: string;
}

/**
 * 增强参数管理页面(GraphQL版本)
 * 提供高级参数管理功能
 * 需要游戏上下文
 */
function ParametersEnhancedGraphQL() {
  const { currentGame } = useOutletContext<{ currentGame: GameContext }>();
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Game context check - show prompt if no game selected
  if (!currentGame) {
    return <SelectGamePrompt message="查看增强参数管理需要先选择游戏" />;
  }

  // GraphQL query
  const { data: paramsData, loading: isLoading, error } = useParametersManagement(
    currentGame.gid,
    'all',
    undefined
  );

  // Get parameters list
  const parameters: Parameter[] = useMemo(() => {
    return paramsData?.parametersManagement || [];
  }, [paramsData]);

  // 客户端过滤（useMemo优化）
  const filteredParameters = useMemo(() => {
    return parameters.filter(param => {
      const matchesSearch = param.paramName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           param.paramNameCn?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || param.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [parameters, searchTerm, selectedCategory]);

  const categories = useMemo(() => {
    return ['all', ...new Set(parameters.map(p => p.category).filter(Boolean) as string[])];
  }, [parameters]);

  if (isLoading) {
    return (
      <div className="loading-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spinner size="lg" label="加载中..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p>加载失败: {error.message}</p>
        <Button variant="primary" onClick={() => window.location.reload()}>
          重试
        </Button>
      </div>
    );
  }

  return (
    <div className="parameters-enhanced-container">
      <div className="page-header">
        <h1>增强参数管理</h1>
        <p className="text-secondary">游戏: {currentGame.name} (GraphQL)</p>
        <Link to="/parameters">
          <Button variant="outline-secondary">
            返回
          </Button>
        </Link>
      </div>

      <div className="toolbar glass-card">
        <SearchInput
          placeholder="搜索参数..."
          value={searchTerm}
          onChange={(value: string) => setSearchTerm(value)}
        />
        <select
          className="category-filter"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat === 'all' ? '全部分类' : cat}
            </option>
          ))}
        </select>
      </div>

      <div className="parameters-grid">
        {filteredParameters.length === 0 ? (
          <div className="empty-state">
            <p className="text-secondary">
              {searchTerm ? '没有找到匹配的参数' : '暂无参数数据'}
            </p>
          </div>
        ) : (
          filteredParameters.map(param => (
            <div key={param.id} className="param-card glass-card">
              <div className="param-header">
                <h3>{param.paramName}</h3>
                <span className="badge">{param.paramType}</span>
              </div>
              <p className="param-description">{param.paramDescription || '暂无描述'}</p>
              <div className="param-meta">
                <span className="category">{param.category || '未分类'}</span>
                {param.isCommon && <span className="common-badge">公参</span>}
                {/* 未绑定库的参数显示绑定按钮 */}
                {!param.library_id && (
                  <BindToLibraryButton
                    paramId={param.id}
                    paramName={param.paramName}
                  />
                )}
              </div>
              <div className="param-stats">
                <span className="stat-item">
                  <i className="bi bi-graph-up"></i>
                  使用次数: {param.usageCount || 0}
                </span>
                <span className="stat-item">
                  <i className="bi bi-diagram-3"></i>
                  事件数: {param.eventsCount || 0}
                </span>
              </div>
              <div className="param-footer">
                <span className={`status-badge ${param.isActive ? 'active' : 'inactive'}`}>
                  {param.isActive ? '活跃' : '停用'}
                </span>
                <span className="version">v{param.version}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ParametersEnhancedGraphQL;
