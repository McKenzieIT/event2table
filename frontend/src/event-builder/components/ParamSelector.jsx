/**
 * ParamSelector Component
 * 参数字段选择器组件
 */
import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchParams } from "@shared/api/eventNodeBuilderApi";
import { SearchInput } from "@shared/ui";

export default function ParamSelector({ eventId, onAddField, disabled }) {
  const [searchQuery, setSearchQuery] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["params", eventId, searchQuery],
    queryFn: () => fetchParams(eventId),
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
      return data.data.params;
    }

    // 兼容旧格式: data.data 直接是数组
    if (data.data && Array.isArray(data.data)) {
      return data.data;
    }

    console.warn('[ParamSelector] Unexpected data structure:', data);
    return [];
  }, [data]);

  // 过滤参数
  const filteredParams = debouncedSearch
    ? params.filter(
        (p) =>
          (p.param_name_cn && p.param_name_cn.includes(debouncedSearch)) ||
          (p.param_name && p.param_name.includes(debouncedSearch)),
      )
    : params;

  const handleDoubleClick = (param) => {
    console.log("[ParamSelector] Double clicked param:", param);
    console.log(
      "[ParamSelector] Calling onAddField with:",
      "param",
      param.param_name,
      param.param_name_cn || param.param_name,
      param.id,
    );
    onAddField(
      "param",
      param.param_name,
      param.param_name_cn || param.param_name,
      param.id,
    );
    console.log("[ParamSelector] onAddField called completed");

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

  const handleDragStart = (e, param) => {
    console.log("[ParamSelector] Drag started:", param);
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
            <div className="dropdown-loading">加载中...</div>
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
                title="双击或拖拽添加到画布"
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
