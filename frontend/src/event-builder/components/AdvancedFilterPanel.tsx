/**
 * 高级筛选面板组件
 * Advanced Filter Panel Component
 *
 * @description 提供高级筛选功能（今日修改、事件筛选、字段数范围）
 */

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { eventNodesApi } from "@shared/api/eventNodes";
import type { EventNodeFilters } from "@shared/types/eventNodes";
import { Button, Checkbox } from "@shared/ui";

/**
 * Props接口
 */
interface AdvancedFilterPanelProps {
  show: boolean;
  filters: EventNodeFilters;
  updateFilters: (updates: Partial<EventNodeFilters>) => void;
  gameGid: number | null;
}

/**
 * 高级筛选面板组件
 */
export function AdvancedFilterPanel({
  show,
  filters,
  updateFilters,
  gameGid,
}: AdvancedFilterPanelProps) {
  // 加载事件列表（用于筛选下拉框）
  const { data: eventsData, isLoading: eventsLoading } = useQuery({
    queryKey: ["events", gameGid],
    queryFn: async () => {
      if (!gameGid) return { data: { events: [] } };
      return eventNodesApi.getEvents(gameGid);
    },
    enabled: show && !!gameGid,
    staleTime: 60000, // 1分钟内不重新获取
  });

  const events = eventsData?.data?.events || [];

  if (!show) {
    return null;
  }

  return (
    <div className="glass-card mb-4">
      <div className="p-4">
        <div className="row g-3 align-items-end">
          {/* 今日修改 */}
          <div className="col-auto">
            <div className="form-check mb-2">
              <input
                className="form-check-input"
                type="checkbox"
                id="todayModified"
                checked={filters.todayModified}
                onChange={(e) =>
                  updateFilters({ todayModified: e.target.checked })
                }
              />
              <label className="form-check-label" htmlFor="todayModified">
                今日修改
              </label>
            </div>
            <div
              className="form-text text-muted"
              style={{ fontSize: "0.75rem" }}
            >
              包含今天新增和修改的节点
            </div>
          </div>

          <div className="col-auto">
            <div className="vr" style={{ height: "40px" }}></div>
          </div>

          {/* 事件筛选 */}
          <div className="col-auto">
            <label htmlFor="filterEventId" className="form-label">
              关联事件
            </label>
            <select
              className="form-select"
              id="filterEventId"
              value={filters.eventId}
              onChange={(e) => updateFilters({ eventId: e.target.value })}
              disabled={eventsLoading}
              style={{ minWidth: "200px" }}
            >
              <option value="">全部事件</option>
              {events.map((event) => (
                <option key={event.id} value={event.id.toString()}>
                  {event.event_name} ({event.event_name_cn})
                </option>
              ))}
            </select>
          </div>

          <div className="col-auto">
            <div className="vr" style={{ height: "40px" }}></div>
          </div>

          {/* 字段数范围 */}
          <div className="col-auto">
            <label className="form-label d-block">字段数范围</label>
            <div className="d-flex gap-2 align-items-center">
              <input
                type="number"
                className="form-control"
                style={{ width: "100px" }}
                placeholder="最小"
                min="0"
                value={filters.fieldCountMin}
                onChange={(e) =>
                  updateFilters({ fieldCountMin: e.target.value })
                }
              />
              <span className="text-muted">-</span>
              <input
                type="number"
                className="form-control"
                style={{ width: "100px" }}
                placeholder="最大"
                min="0"
                value={filters.fieldCountMax}
                onChange={(e) =>
                  updateFilters({ fieldCountMax: e.target.value })
                }
              />
            </div>
          </div>

          {/* 清空按钮 */}
          <div className="col-auto ms-auto">
            <Button
              variant="ghost"
              size="sm"
              onClick={() =>
                updateFilters({
                  todayModified: false,
                  eventId: "",
                  fieldCountMin: "",
                  fieldCountMax: "",
                })
              }
            >
              清空筛选
            </Button>
          </div>
        </div>

        {/* 活跃筛选标签 */}
        {(filters.todayModified ||
          filters.eventId ||
          filters.fieldCountMin ||
          filters.fieldCountMax) && (
          <div className="mt-3 pt-3 border-top">
            <div className="d-flex gap-2 align-items-center flex-wrap">
              <span className="text-muted small me-2">活跃筛选:</span>

              {filters.todayModified && (
                <span className="badge bg-primary">
                  今日修改
                  <button
                    type="button"
                    className="btn-close btn-close-white ms-2"
                    style={{ fontSize: "0.5rem" }}
                    onClick={() => updateFilters({ todayModified: false })}
                  ></button>
                </span>
              )}

              {filters.eventId && (
                <span className="badge bg-primary">
                  事件:{" "}
                  {events.find((e) => e.id.toString() === filters.eventId)
                    ?.event_name || filters.eventId}
                  <button
                    type="button"
                    className="btn-close btn-close-white ms-2"
                    style={{ fontSize: "0.5rem" }}
                    onClick={() => updateFilters({ eventId: "" })}
                  ></button>
                </span>
              )}

              {(filters.fieldCountMin || filters.fieldCountMax) && (
                <span className="badge bg-primary">
                  字段数: {filters.fieldCountMin || "0"} -{" "}
                  {filters.fieldCountMax || "∞"}
                  <button
                    type="button"
                    className="btn-close btn-close-white ms-2"
                    style={{ fontSize: "0.5rem" }}
                    onClick={() =>
                      updateFilters({ fieldCountMin: "", fieldCountMax: "" })
                    }
                  ></button>
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
