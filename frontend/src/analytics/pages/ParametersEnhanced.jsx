import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useOutletContext } from 'react-router-dom';
import { SelectGamePrompt } from '@shared/ui/SelectGamePrompt';
import { Button, SearchInput, Spinner } from '@shared/ui';
import { BindToLibraryButton } from '@shared/components/BindToLibraryButton';
import './ParametersEnhanced.css';

/**
 * 增强参数管理页面
 * 提供高级参数管理功能
 * 需要游戏上下文
 */
function ParametersEnhanced() {
  const { currentGame } = useOutletContext();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  // Game context check - show prompt if no game selected
  if (!currentGame) {
    return <SelectGamePrompt message="查看增强参数管理需要先选择游戏" />;
  }

  const { data: parameters = [], isLoading } = useQuery({
    queryKey: ['parameters', currentGame.gid],
    queryFn: async () => {
      const response = await fetch(`/api/parameters/all?game_gid=${currentGame.gid}`);
      if (!response.ok) throw new Error('加载失败');
      return response.json();
    },
    enabled: !!currentGame // Only execute when currentGame exists
  });

  // 客户端过滤（useMemo优化）
  const filteredParameters = useMemo(() => {
    return parameters.filter(param => {
      const matchesSearch = param.name?.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || param.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [parameters, searchTerm, selectedCategory]);

  const categories = useMemo(() => {
    return ['all', ...new Set(parameters.map(p => p.category).filter(Boolean))];
  }, [parameters]);

  if (isLoading) {
    return (
      <div className="loading-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '400px' }}>
        <Spinner size="lg" label="加载中..." />
      </div>
    );
  }

  return (
    <div className="parameters-enhanced-container">
      <div className="page-header">
        <h1>增强参数管理</h1>
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
              {cat === 'all' ? '全部分类' : cat}
            </option>
          ))}
        </select>
      </div>

      <div className="parameters-grid">
        {filteredParameters.map(param => (
          <div key={param.id} className="param-card glass-card">
            <div className="param-header">
              <h3>{param.name}</h3>
              <span className="badge">{param.type}</span>
            </div>
            <p className="param-description">{param.description || '暂无描述'}</p>
            <div className="param-meta">
              <span className="category">{param.category}</span>
              {param.isCommon && <span className="common-badge">公参</span>}
              {/* 未绑定库的参数显示绑定按钮 */}
              {!param.library_id && (
                <BindToLibraryButton
                  paramId={param.id}
                  paramName={param.name}
                  templateId={param.template_id}
                />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ParametersEnhanced;
