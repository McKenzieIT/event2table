/**
 * ParametersEnhancedGraphQL - 增强参数管理页面(GraphQL版本)
 *
 * 完整迁移自ParametersEnhanced.jsx,保留所有功能:
 * - 参数列表展示(卡片式)
 * - 搜索功能
 * - 分类过滤
 * - 公参标识
 * - 绑定到库功能
 *
 * 使用GraphQL API替代REST API
 */

import React, { useState, useMemo } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import { SelectGamePrompt } from '@shared/ui/SelectGamePrompt';
import { Button, SearchInput, Spinner } from '@shared/ui';
import { BindToLibraryButton } from '@shared/components/BindToLibraryButton';
import { useAllParametersByGame } from '@/graphql/hooks';
import './ParametersEnhanced.css';

/**
 * 增强参数管理页面(GraphQL版本)
 * 提供高级参数管理功能
 * 需要游戏上下文
 */
function ParametersEnhancedGraphQL() {
  const { currentGame } = useOutletContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Game context check - show prompt if no game selected
  if (!currentGame) {
    return <SelectGamePrompt message="查看增强参数管理需要先选择游戏" />;
  }

  // GraphQL query - Fetch all parameters for the game
  const { data: parametersData = {}, loading: isLoading, error, refetch } = useAllParametersByGame(currentGame.gid);

  const parameters = parametersData?.parametersManagement || [];

  // 客户端过滤（useMemo优化）
  const filteredParameters = useMemo(() => {
    return parameters.filter(param => {
      const matchesSearch = param.paramName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           param.paramNameCn?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || param.eventCode === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [parameters, searchTerm, selectedCategory]);

  // Get unique event codes as categories
  const categories = useMemo(() => {
    const eventCodes = new Set(parameters.map(p => p.eventCode).filter(Boolean));
    return ['all', ...Array.from(eventCodes).sort()];
  }, [parameters]);

  if (isLoading) {
    return (
      <div className="loading-container">
        <Spinner size="lg" label="加载中..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <p>加载失败: {error.message}</p>
        <Button variant="primary" onClick={() => refetch()}>重试</Button>
      </div>
    );
  }

  return (
    <div className="parameters-enhanced-container">
      <div className="page-header">
        <h1>增强参数管理 (GraphQL)</h1>
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
          onChange={(value) => setSearchTerm(value)}
        />
        <select
          className="category-filter"
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat === 'all' ? '全部事件' : cat}
            </option>
          ))}
        </select>
      </div>

      <div className="parameters-grid">
        {filteredParameters.length === 0 ? (
          <div className="empty-state">
            <p>没有找到匹配的参数</p>
          </div>
        ) : (
          filteredParameters.map(param => (
            <div key={param.id} className="param-card glass-card">
              <div className="param-header">
                <h3>{param.paramNameCn || param.paramName}</h3>
                <span className="badge">{param.paramType}</span>
              </div>
              <p className="param-description">{param.paramDescription || '暂无描述'}</p>
              <div className="param-meta">
                <span className="category">{param.eventName || param.eventCode}</span>
                {param.isCommon && <span className="common-badge">公参</span>}
                <span className="usage-count">使用次数: {param.usageCount || 0}</span>
                {/* 未绑定库的参数显示绑定按钮 */}
                {param.isCommon && (
                  <BindToLibraryButton
                    paramId={param.id}
                    paramName={param.paramName}
                  />
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default ParametersEnhancedGraphQL;
