// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * ParamSelector Component
 * 参数字段选择器组件
 */
import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchParams } from "@shared/api/eventNodeBuilder";
import { SearchInput, Skeleton, ErrorState } from "@shared/ui";

/**
 * 参数接口
 */
export interface Param {
  id: number;
  param_name: string;
  param_name_cn?: string;
  json_path?: string;
  hive_type?: string;
}

/**
 * 组件Props接口
 */
export interface ParamSelectorProps {
  eventId?: number;
  onAddField: (
    fieldType: string,
    fieldName: string,
    displayName: string,
    paramId: number,
    jsonPath?: string
  ) => void;
  disabled?: boolean;
}

/**
 * ParamSelector Component
 */
export default function ParamSelector({ eventId, onAddField, disabled = false }: ParamSelectorProps) {
  const [searchQuery, setSearchQuery] = useState("");

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["params", eventId, searchQuery],
    queryFn: () => fetchParams(eventId!),
    enabled: !!eventId,
  });

  // 显式验证：从完整响应中提取参数数组
  // API 返回结构: {success: true, data: {params: [...], has_more, page, total}}
  const params = useMemo(() => {
    if (!data || typeof data !== 'object') {
      return [];
    }

    // 检查 data.data.params (新API格式)
    if (data.data && data.data.params && Array.isArray(data.data.params)) {
      return data.data.params as Param[];
    }

    // 兼容旧格式: data.data 直接是数组
    if (data.data && Array.isArray(data.data)) {
      return data.data as Param[];
    }

    console.warn('[ParamSelector] Unexpected data structure:', data);
    return [];
  }, [data]);

  // 过滤参数
  const filteredParams = searchQuery
    ? params.filter(
        (p) =>
          (p.param_name_cn && p.param_name_cn.includes(searchQuery)) ||
          (p.param_name && p.param_name.includes(searchQuery)),
      )
    : params;

  const handleDoubleClick = (param: Param) => {
    onAddField(
      "param",
      param.param_name,
      param.param_name_cn || param.param_name,
      param.id,
      param.json_path || `$.${param.param_name}`, // 添加 json_path 参数
    );

    // Add success animation
    const element = document.querySelector(
      `[data-param="${param.param_name}"]`,
    );
    if (element) {
      element.classList.add("double-click-success");
      setTimeout(() => {
        element.classList.remove("double-click-success");
      }, 600);
    }
  };

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>, param: Param) => {
    e.dataTransfer.effectAllowed = "copy";
    // 设置多种格式以确保兼容性
    const dragData = {
      type: "param",
      fieldType: "param",
      fieldName: param.param_name,
      displayName: param.param_name_cn || param.param_name,
      paramId: param.id,
    };

    // 使用多种格式设置数据
    e.dataTransfer.setData("application/json", JSON.stringify(dragData));
    e.dataTransfer.setData("text/plain", JSON.stringify(dragData));
  };

  return (
    <div className="sidebar-section glass-card-dark">
      <div className="section-header">
        <h3>
          <i className="bi bi-gear"></i>
          参数字段
        </h3>
        <i className="bi bi-chevron-down toggle-icon"></i>
      </div>
      <div className="section-content">
        <div className="search-box">
          <SearchInput
            placeholder="搜索参数..."
            value={searchQuery}
            onChange={(value) => setSearchQuery(value)}
            disabled={disabled}
          />
        </div>
        <div className="dropdown-list">
          {!eventId ? (
            <div className="dropdown-placeholder">请先选择事件</div>
          ) : isLoading ? (
            <div className="dropdown-loading">
              <Skeleton type="inline" rows={5} height={40} />
            </div>
          ) : isError ? (
            <ErrorState
              message="无法加载参数列表"
              error={error as Error}
              onRetry={refetch}
            />
          ) : filteredParams.length === 0 ? (
            <div className="dropdown-placeholder">没有找到参数</div>
          ) : (
            filteredParams.map((param) => (
              <div
                key={param.id}
                data-testid={`param-${param.param_name}`}
                data-param={param.param_name}
                className="dropdown-item"
                draggable
                onDragStart={(e) => handleDragStart(e, param)}
                onDoubleClick={() => handleDoubleClick(param)}
              >
                <span>{param.param_name_cn || param.param_name}</span>
                <small>{param.param_name}</small>
              </div>
            ))
          )}
        </div>
        <p className="help-text">双击参数添加到画布</p>
      </div>
    </div>
  );
}
