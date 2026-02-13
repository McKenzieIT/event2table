import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
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
import { fetchAllParameters } from '@shared/api/parameters';
import ParameterDetailDrawer from '@analytics/components/parameters/ParameterDetailDrawer';
import './ParametersList.css';

/**
 * 参数管理页面
 *
 * 显示和管理事件参数
 * ✅ 修复: 使用game_gid而非game_id,参数去重显示
 * 最佳实践应用:
 * - useMemo优化过滤计算
 * - useCallback优化事件处理
 * - 提前返回优化
 * - React Query并行加载数据
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

function ParametersList() {
  const { currentGame } = useGameStore();
  const { success, error: showError, warning } = useToast();

  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [selectedParam, setSelectedParam] = useState(null); // 选中的参数对象
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // ✅ 关键修复: 使用useMemo稳定gameGid引用,避免不必要的重渲染
  const gameGid = useMemo(() => currentGame?.gid, [currentGame?.gid]);

  // ✅ 使用防抖搜索,避免频繁触发API请求
  // searchTerm/typeFilter: UI状态,立即更新
  // debouncedSearch/debouncedType: 查询状态,延迟500ms更新
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [debouncedType, setDebouncedType] = useState('');

  // 防抖效果: 延迟更新查询状态
  // ✅ 关键修复: 移除debouncedSearch/debouncedType从依赖项,避免循环
  useEffect(() => {
    // 设置防抖定时器
    const timer = setTimeout(() => {
      // 只在值真正变化时更新
      if (searchTerm !== debouncedSearch || typeFilter !== debouncedType) {
        setDebouncedSearch(searchTerm);
        setDebouncedType(typeFilter);
      }
    }, 500); // 500ms防抖延迟

    return () => clearTimeout(timer);
  }, [searchTerm, typeFilter]); // ✅ 只依赖searchTerm和typeFilter

  // ✅ 修复: 使用正确的API端点和game_gid
  // queryKey使用防抖后的值,避免频繁重新执行
  const { data: paramsData, isLoading, error, refetch } = useQuery({
    queryKey: ['parameters', gameGid, debouncedSearch, debouncedType],
    queryFn: () => fetchAllParameters(gameGid, {
      search: debouncedSearch,
      type: debouncedType
    }),
    enabled: !!gameGid, // ✅ 只在有游戏时才执行查询
    retry: 0,
    staleTime: 10000
  });

  // 显式验证：确保paramsData和data存在
  let parameters = [];
  let total = 0;

  if (paramsData && typeof paramsData === 'object') {
    if (paramsData.data && typeof paramsData.data === 'object') {
      if (Array.isArray(paramsData.data.parameters)) {
        parameters = paramsData.data.parameters;
      } else {
        console.warn('[ParametersList] paramsData.data.parameters is not an array');
      }
      total = paramsData.data.total || 0;
    } else {
      console.warn('[ParametersList] paramsData.data is missing');
    }
  } else {
    console.warn('[ParametersList] Invalid paramsData object');
  }

  // 处理参数点击 - 打开详情抽屉
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
    // 导出功能
    warning('导出功能待实现');
  }, [warning]);

  // ✅ 修复: Hooks 调用完成后再进行条件渲染
  // Game context check - show prompt if no game selected
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

  // 后端已处理筛选,前端直接使用
  const filteredParameters = parameters;

  // 统计数据 - 移除useMemo避免依赖问题,直接计算
  const uniqueParamNames = new Set(parameters.map(p => p.param_name)).size;
  const commonParamsCount = parameters.filter(p => p.is_common === 1).length;
  const totalEvents = parameters.reduce((sum, p) => sum + (p.events_count || 0), 0);
  const avgParamsPerEvent = uniqueParamNames > 0 ? (totalEvents / uniqueParamNames).toFixed(1) : 0;

  const stats = {
    totalParams: total,
    uniqueParamNames,
    commonParamsCount,
    avgParamsPerEvent
  };

  return (
    <div className="parameters-list-container">
      {/* Page Header */}
      <div className="page-header">
        <div className="header-title">
          <div className="icon-box">
            <i className="bi bi-sliders"></i>
          </div>
          <div>
            <h1>参数管理</h1>
            <p>管理和配置事件参数</p>
          </div>
        </div>
        <div className="header-actions">
          <Link to="/parameter-usage" className="btn btn-outline-info">
            <i className="bi bi-graph-up-arrow"></i>
            使用分析
          </Link>
          <Link to="/parameter-history" className="btn btn-outline-dark">
            <i className="bi bi-clock-history"></i>
            变更历史
          </Link>
          <Link to="/parameter-network" className="btn btn-outline-secondary">
            <i className="bi bi-diagram-3"></i>
            关系网络
          </Link>
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
            onChange={(value) => setSearchTerm(value)}
          />
        </div>

        <Select
          className="glass-select"
          value={typeFilter}
          onChange={(value) => setTypeFilter(value)}
          options={[
            { value: '', label: '所有类型' },
            { value: 'string', label: '字符串' },
            { value: 'int', label: '整数' },
            { value: 'bigint', label: '长整数' },
            { value: 'float', label: '浮点数' },
            { value: 'boolean', label: '布尔值' },
            { value: 'array', label: '数组' },
            { value: 'map', label: 'Map' }
          ]}
        />

        {(searchTerm || typeFilter) && (
          <button
            className="btn btn-outline-secondary btn-sm"
            onClick={() => {
              setSearchTerm('');
              setTypeFilter('');
            }}
          >
            <i className="bi bi-x-circle"></i>
            清除筛选
          </button>
        )}
      </div>

      {/* Parameters Table */}
      <div className="table-card glass-card">
        <div className="card-header">
          <h6>
            <i className="bi bi-table"></i>
            参数列表
            <Badge variant="primary">{filteredParameters.length}</Badge>
          </h6>
          <button className="btn btn-sm btn-outline-primary" onClick={handleExport}>
            <i className="bi bi-download"></i>
            导出
          </button>
        </div>

        <div className="table-wrapper">
          <table className="oled-table">
            <thead>
              <tr>
                <th>参数名</th>
                <th>参数中文名</th>
                <th>类型</th>
                <th>使用事件数</th>
                <th>使用频率</th>
                <th>公参</th>
                <th style={{width: '100px'}}>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredParameters.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center">
                    <div className="empty-state">
                      <i className="bi bi-inbox"></i>
                      <p>暂无参数数据</p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredParameters.map((param, index) => (
                  <tr
                    key={`${param.param_name}-${index}`}
                    className="parameter-row"
                    style={{cursor: 'pointer'}}
                    onClick={() => handleParameterClick(param)}
                  >
                    <td><code>{param.param_name}</code></td>
                    <td>{param.param_name_cn || '-'}</td>
                    <td>
                      <Badge variant={getTypeBadgeVariant(param.base_type)}>
                        {param.base_type}
                      </Badge>
                    </td>
                    <td>{param.events_count || 0}</td>
                    <td>{param.usage_count || 0}</td>
                    <td>
                      {param.is_common ? (
                        <Badge variant="success">是</Badge>
                      ) : (
                        <Badge variant="secondary">否</Badge>
                      )}
                    </td>
                    <td>
                      <button
                        className="btn btn-sm btn-outline-primary"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleParameterClick(param);
                        }}
                      >
                        <i className="bi bi-eye"></i>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* 参数详情抽屉 */}
      {selectedParam && (
        <ParameterDetailDrawer
          show={isDrawerOpen}
          paramName={selectedParam.param_name}
          gameGid={gameGid}
          onClose={handleCloseDrawer}
        />
      )}
    </div>
  );
}

export default ParametersList;
