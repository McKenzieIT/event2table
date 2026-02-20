import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link, useOutletContext } from 'react-router-dom';
import { SelectGamePrompt, SearchInput } from '@shared/ui';
import EmptyState from '@shared/ui/EmptyState/EmptyState';
import './ParameterCompare.css';

/**
 * 参数对比组件
 * 对比两个参数的详细信息
 * 最佳实践: useMemo + useCallback + 并行加载
 * 需要游戏上下文
 */
function ParameterCompare() {
  const { currentGame } = useOutletContext();
  const [selectedParam1, setSelectedParam1] = useState(null);
  const [selectedParam2, setSelectedParam2] = useState(null);
  const [search1, setSearch1] = useState('');
  const [search2, setSearch2] = useState('');

  // Game context check - show prompt if no game selected
  if (!currentGame) {
    return <SelectGamePrompt message="查看参数对比需要先选择游戏" />;
  }

  // 加载所有参数
  const { data: allParameters = [], isLoading } = useQuery({
    queryKey: ['parameters', 'all', currentGame.gid, 'v2'], // v2 to force cache refresh
    queryFn: async () => {
      const response = await fetch(`/api/parameters/all?game_gid=${currentGame.gid}`);
      if (!response.ok) throw new Error('加载参数失败');
      const result = await response.json();
      // API 返回格式: { data: { parameters: [...], total: 100 } }
      return result.data?.parameters || [];
    },
    enabled: !!currentGame // Only execute when currentGame exists
  });

  // 客户端过滤（useMemo优化）
  const filteredParams1 = useMemo(() => {
    const term = search1.toLowerCase();
    return allParameters.filter(param => {
      return param.param_name?.toLowerCase().includes(term) ||
             param.param_name_cn?.toLowerCase().includes(term) ||
             param.event_name?.toLowerCase().includes(term);
    });
  }, [allParameters, search1]);

  const filteredParams2 = useMemo(() => {
    const term = search2.toLowerCase();
    return allParameters.filter(param => {
      return param.param_name?.toLowerCase().includes(term) ||
             param.param_name_cn?.toLowerCase().includes(term) ||
             param.event_name?.toLowerCase().includes(term);
    });
  }, [allParameters, search2]);

  // 选择参数
  const selectParam1 = useCallback((param) => {
    setSelectedParam1(param);
  }, []);

  const selectParam2 = useCallback((param) => {
    setSelectedParam2(param);
  }, []);

  // 对比字段定义
  const comparisonFields = useMemo(() => [
    { key: 'param_name', label: '参数名称 (英文)' },
    { key: 'param_name_cn', label: '参数名称 (中文)' },
    { key: 'param_type', label: '参数类型' },
    { key: 'param_description', label: '参数描述' },
    { key: 'is_common_param', label: '是否公参', transform: v => v ? '是' : '否' },
    { key: 'event_name', label: '所属事件' },
    { key: 'game_name', label: '所属游戏' }
  ], []);

  // 渲染参数列表
  const renderParamList = useCallback((params, selectedParam, onSelect) => {
    if (params.length === 0) {
      return (
        <EmptyState
          icon={<i className="bi bi-inbox" aria-hidden="true"></i>}
          title="未找到匹配的参数"
          description="尝试调整搜索条件"
        />
      );
    }

    return params.map(param => (
      <div
        key={param.id}
        className={`param-item ${selectedParam?.id === param.id ? 'selected' : ''}`}
        onClick={() => onSelect(param)}
      >
        <div>
          <div className="param-item-name">{param.param_name}</div>
          <div className="param-item-event">
            {param.event_name} - {param.game_name}
          </div>
        </div>
        <i className="bi bi-chevron-right"></i>
      </div>
    ));
  }, []);

  // 提前返回优化
  if (isLoading) {
    return <div className="loading">加载中...</div>;
  }

  const canShowComparison = selectedParam1 && selectedParam2;

  return (
    <div className="parameter-compare-container">
      {/* Page Header */}
      <div className="page-header glass-card">
        <div className="header-content">
          <div className="header-left">
            <i className="bi bi-columns header-icon"></i>
            <div>
              <h1>参数对比</h1>
              <p>对比两个参数的详细信息</p>
            </div>
          </div>
          <Link to="/parameters" className="btn btn-outline-primary">
            <i className="bi bi-arrow-left"></i>
            返回参数管理
          </Link>
        </div>
      </div>

      {/* Parameter Selection */}
      <div className="compare-container">
        {/* Parameter 1 */}
        <div className="parameter-selector glass-card">
          <div className="selector-header">
            <i className="bi bi-1-circle selector-icon"></i>
            <h5>选择参数 A</h5>
          </div>
          <div className="search-box">
            <SearchInput
              value={search1}
              onChange={(value) => setSearch1(value)}
              placeholder="搜索参数..."
            />
          </div>
          <div className="param-list">
            {renderParamList(filteredParams1, selectedParam1, selectParam1)}
          </div>
        </div>

        {/* Parameter 2 */}
        <div className="parameter-selector glass-card">
          <div className="selector-header">
            <i className="bi bi-2-circle selector-icon-alt"></i>
            <h5>选择参数 B</h5>
          </div>
          <div className="search-box">
            <SearchInput
              value={search2}
              onChange={(value) => setSearch2(value)}
              placeholder="搜索参数..."
            />
          </div>
          <div className="param-list">
            {renderParamList(filteredParams2, selectedParam2, selectParam2)}
          </div>
        </div>
      </div>

      {/* Comparison Result */}
      {canShowComparison && (
        <div className="comparison-result glass-card">
          <h4 className="comparison-title">
            <i className="bi bi-file-earmark-diff"></i>
            对比结果
          </h4>
          <table className="comparison-table">
            <thead>
              <tr>
                <th style={{ width: '20%' }}>属性</th>
                <th style={{ width: '40%' }}>参数 A</th>
                <th style={{ width: '40%' }}>参数 B</th>
              </tr>
            </thead>
            <tbody>
              {comparisonFields.map(field => {
                const val1 = selectedParam1[field.key];
                const val2 = selectedParam2[field.key];
                const displayVal1 = field.transform ? field.transform(val1) : (val1 || '-');
                const displayVal2 = field.transform ? field.transform(val2) : (val2 || '-');
                const isSame = JSON.stringify(val1) === JSON.stringify(val2);
                const diffClass = isSame ? 'diff-same' : 'diff-different';

                return (
                  <tr key={field.key}>
                    <td><strong>{field.label}</strong></td>
                    <td className="value-cell">
                      {displayVal1}
                      {isSame ? (
                        <span className="badge badge-success">
                          <i className="bi bi-check"></i> 相同
                        </span>
                      ) : (
                        <span className="badge badge-warning">
                          <i className="bi bi-x"></i> 不同
                        </span>
                      )}
                    </td>
                    <td className="value-cell">{displayVal2}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* No Selection State */}
      {!canShowComparison && (
        <div className="no-selection-state glass-card">
          <div className="selection-icon">
            <i className="bi bi-columns"></i>
          </div>
          <h3>选择参数进行对比</h3>
          <p>在上方分别选择两个参数，查看详细对比信息</p>
        </div>
      )}
    </div>
  );
}

export default ParameterCompare;
