import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@apollo/client';
import { useGameStore } from '@/stores/gameStore';
import {
  SelectGamePrompt,
  Input,
  Select,
  Badge,
  Spinner,
  SearchInput,
  useToast
} from '@shared/ui';
import { GET_PARAMETERS_MANAGEMENT } from '@/graphql/queries';
import ParameterDetailDrawer from '@analytics/components/parameters/ParameterDetailDrawer';
import { NavLinkWithGameContext } from '@shared/components';
import './ParametersList.css';

/**
 * 参数管理页面 (GraphQL版本)
 *
 * 已迁移到GraphQL:
 * - 使用Apollo Client替代React Query + fetch
 * - 使用GraphQL查询GET_PARAMETERS_MANAGEMENT
 * - 自动类型检查（通过GraphQL Code Generator）
 *
 * 最佳实践应用:
 * - useMemo优化过滤计算
 * - useCallback优化事件处理
 * - 提前返回优化
 * - Apollo Client缓存优化
 * - 游戏上下文验证
 */

/**
 * 获取参数类型对应的Badge variant
 */
const getTypeBadgeVariant = (baseType) => {
  const variantMap = {
    'string': 'info',
    'int': 'success',
    'bigint': 'warning',
    'float': 'primary',
    'boolean': 'danger',
    'datetime': 'info',
    'array': 'primary',
    'map': 'secondary'
  };
  return variantMap[baseType] || 'secondary';
};

function ParametersListGraphQL() {
  const { currentGame } = useGameStore();
  const { success, error: showError, warning } = useToast();

  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [selectedParam, setSelectedParam] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // 使用useMemo稳定gameGid引用
  const gameGid = useMemo(() => currentGame?.gid, [currentGame?.gid]);

  // 防抖搜索
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [debouncedType, setDebouncedType] = useState('');

  // 防抖效果
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm !== debouncedSearch || typeFilter !== debouncedType) {
        setDebouncedSearch(searchTerm);
        setDebouncedType(typeFilter);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm, typeFilter]);

  // 使用GraphQL查询参数管理数据
  const { data: paramsData, loading: isLoading, error, refetch } = useQuery(GET_PARAMETERS_MANAGEMENT, {
    variables: {
      gameGid: gameGid,
      mode: 'all',
      eventId: null
    },
    skip: !gameGid,
    fetchPolicy: 'cache-and-network',
    pollInterval: 60000, // 每分钟轮询一次
  });

  // 处理参数数据
  const parameters = paramsData?.parametersManagement || [];

  // 客户端过滤（搜索和类型）
  const filteredParameters = useMemo(() => {
    let filtered = parameters;

    // 搜索过滤
    if (debouncedSearch) {
      filtered = filtered.filter(p =>
        p.paramName?.toLowerCase().includes(debouncedSearch.toLowerCase()) ||
        p.paramNameCn?.toLowerCase().includes(debouncedSearch.toLowerCase())
      );
    }

    // 类型过滤
    if (debouncedType) {
      filtered = filtered.filter(p => p.paramType === debouncedType);
    }

    return filtered;
  }, [parameters, debouncedSearch, debouncedType]);

  // 统计数据
  const stats = useMemo(() => {
    const uniqueParamNames = new Set(parameters.map(p => p.paramName)).size;
    const commonParamsCount = parameters.filter(p => p.isCommon).length;
    const totalEvents = parameters.reduce((sum, p) => sum + (p.eventsCount || 0), 0);
    const avgParamsPerEvent = uniqueParamNames > 0 ? (totalEvents / uniqueParamNames).toFixed(1) : 0;

    return {
      totalParams: parameters.length,
      uniqueParamNames,
      commonParamsCount,
      avgParamsPerEvent
    };
  }, [parameters]);

  // 获取所有参数类型（用于过滤）
  const paramTypes = useMemo(() => {
    const types = new Set(parameters.map(p => p.paramType).filter(Boolean));
    return Array.from(types).sort();
  }, [parameters]);

  // 处理参数点击
  const handleParameterClick = useCallback((param) => {
    setSelectedParam(param);
    setIsDrawerOpen(true);
  }, []);

  // 关闭抽屉
  const handleCloseDrawer = useCallback(() => {
    setIsDrawerOpen(false);
    setSelectedParam(null);
  }, []);

  const handleExport = useCallback(() => {
    warning('导出功能待实现');
  }, [warning]);

  // Game context check
  if (!currentGame) {
    return <SelectGamePrompt message="查看参数管理需要先选择游戏" />;
  }

  // 错误状态
  if (error) {
    return (
      <div className="parameters-list-container">
        <div className="error-state">
          <i className="bi bi-exclamation-triangle text-warning"></i>
          <h3>加载参数失败</h3>
          <p>{error.message}</p>
          <button className="btn btn-primary" onClick={() => {
            refetch();
            success('正在重新加载...');
          }}>
            重试
          </button>
        </div>
      </div>
    );
  }

  // 加载状态
  if (isLoading) {
    return (
      <div className="parameters-list-container">
        <div className="loading-container">
          <Spinner size="lg" label="正在加载参数..." />
        </div>
      </div>
    );
  }

  return (
    <div className="parameters-list-container">
      {/* Page Header */}
      <div className="page-header">
        <div className="header-title">
          <div className="icon-box">
            <i className="bi bi-sliders"></i>
          </div>
          <div>
            <h1>参数管理 (GraphQL版本)</h1>
            <p>管理和配置事件参数</p>
          </div>
        </div>
        <div className="header-actions">
          <NavLinkWithGameContext to="/parameter-usage" className="btn btn-outline-info">
            <i className="bi bi-graph-up-arrow"></i>
            使用分析
          </NavLinkWithGameContext>
          <NavLinkWithGameContext to="/parameter-history" className="btn btn-outline-dark">
            <i className="bi bi-clock-history"></i>
            变更历史
          </NavLinkWithGameContext>
          <NavLinkWithGameContext to="/parameter-network" className="btn btn-outline-secondary">
            <i className="bi bi-diagram-3"></i>
            关系网络
          </NavLinkWithGameContext>
          <Link to={`/common-params?game_gid=${gameGid}`} className="btn btn-outline-success">
            <i className="bi bi-table"></i>
            进入公参管理
          </Link>
          <button className="btn btn-primary" onClick={handleExport}>
            <i className="bi bi-download"></i>
            导出Excel
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card glass-card">
          <div className="stat-content">
            <div className="stat-number">{stats.totalParams}</div>
            <div className="stat-label">
              <i className="bi bi-list-ul"></i> 总参数数
            </div>
          </div>
        </div>

        <div className="stat-card glass-card purple">
          <div className="stat-content">
            <div className="stat-number">{stats.uniqueParamNames}</div>
            <div className="stat-label">
              <i className="bi bi-tag"></i> 唯一参数名
            </div>
          </div>
        </div>

        <div className="stat-card glass-card green">
          <div className="stat-content">
            <div className="stat-number">{stats.commonParamsCount}</div>
            <div className="stat-label">
              <i className="bi bi-table"></i> 公参数量
            </div>
          </div>
        </div>

        <div className="stat-card glass-card orange">
          <div className="stat-content">
            <div className="stat-number">{stats.avgParamsPerEvent}</div>
            <div className="stat-label">
              <i className="bi bi-graph-up"></i> 平均参数/事件
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="filter-bar glass-card">
        <div className="filter-group">
          <SearchInput
            placeholder="搜索参数名..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <Select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="type-filter"
          >
            <option value="">全部类型</option>
            {paramTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </Select>
        </div>
        <div className="filter-info">
          显示 {filteredParameters.length} / {parameters.length} 个参数
        </div>
      </div>

      {/* Parameters Table */}
      <div className="parameters-table-container glass-card">
        <table className="parameters-table">
          <thead>
            <tr>
              <th>参数名</th>
              <th>中文名</th>
              <th>类型</th>
              <th>事件</th>
              <th>是否公参</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {filteredParameters.map((param) => (
              <tr key={param.id}>
                <td>
                  <span
                    className="param-name-link"
                    onClick={() => handleParameterClick(param)}
                  >
                    {param.paramName}
                  </span>
                </td>
                <td>{param.paramNameCn || '-'}</td>
                <td>
                  <Badge variant={getTypeBadgeVariant(param.paramType)}>
                    {param.paramType || 'unknown'}
                  </Badge>
                </td>
                <td>
                  <span className="event-name">{param.eventName || '-'}</span>
                </td>
                <td>
                  {param.isCommon ? (
                    <Badge variant="success">是</Badge>
                  ) : (
                    <Badge variant="secondary">否</Badge>
                  )}
                </td>
                <td>
                  <div className="action-buttons">
                    <button
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => handleParameterClick(param)}
                    >
                      详情
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Parameter Detail Drawer */}
      <ParameterDetailDrawer
        isOpen={isDrawerOpen}
        onClose={handleCloseDrawer}
        parameter={selectedParam}
      />
    </div>
  );
}

export default ParametersListGraphQL;
