import React, { useState, useEffect, useCallback, useMemo } from "react";
import { Link } from "react-router-dom";
import { Button, Card, Spinner } from "@shared/ui";
import { useToast } from "@shared/ui";
import "./Generate.css";

/**
 * HQL生成页面
 * 用于生成HQL语句
 *
 * ✅ 已修复：连接真实后端API
 * ✅ 已迁移：使用 @shared/ui 组件库
 * - 从/api/events获取事件列表
 * - 调用/api/generate生成HQL
 * - 使用 Toast 通知系统
 * - 性能优化：useCallback, useMemo, React.memo
 */
function Generate() {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [isLoadingEvents, setIsLoadingEvents] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

  const { success, error: toastError } = useToast();

  // 加载事件列表
  useEffect(() => {
    const fetchEvents = async () => {
      setIsLoadingEvents(true);
      try {
        const gameGid = localStorage.getItem("selectedGameGid") || "10000147";
        const response = await fetch(`/api/events?game_gid=${gameGid}`);

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (result.success) {
          setEvents(result.data.events || []);
        } else {
          toastError(result.error || "加载事件列表失败");
        }
      } catch (err) {
        console.error("Failed to fetch events:", err);
        toastError(
          `加载事件失败: ${err instanceof Error ? err.message : "未知错误"}`,
        );
      } finally {
        setIsLoadingEvents(false);
      }
    };

    fetchEvents();
  }, [toastError]);

  // 使用 useCallback 优化事件处理
  const handleEventSelect = useCallback((eventName) => {
    setSelectedEvent(eventName);
  }, []);

  const handleGenerate = useCallback(async () => {
    if (!selectedEvent) {
      toastError("请先选择事件");
      return;
    }

    setIsGenerating(true);

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          selected_events: [selectedEvent],
          date_str: "${bizdate}",
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      if (result.success) {
        success("HQL生成成功");
        // 跳转到结果页面
        window.location.href = `/#/generate-result?event=${selectedEvent}`;
      } else {
        toastError(result.error || "HQL生成失败");
      }
    } catch (err) {
      console.error("HQL generation error:", err);
      toastError(
        `生成失败: ${err instanceof Error ? err.message : "未知错误"}`,
      );
    } finally {
      setIsGenerating(false);
    }
  }, [selectedEvent, success, toastError]);

  // 使用 useMemo 优化计算
  const selectedEventData = useMemo(() => {
    return events.find(event => event.event_name === selectedEvent);
  }, [events, selectedEvent]);

  return (
    <div className="generate-container">
      <div className="page-header">
        <h1>HQL生成</h1>
        <Link to="/hql-manage">
          <Button variant="ghost">
            <i className="bi bi-arrow-left"></i>
            返回
          </Button>
        </Link>
      </div>

      <div className="generate-content">
        <Card className="event-selector">
          <Card.Body>
            <h3>选择事件</h3>
            {isLoadingEvents ? (
              <Spinner size="md" label="加载事件列表中..." />
            ) : (
              <div className="event-list">
                {events.length === 0 ? (
                  <p className="text-secondary">暂无事件</p>
                ) : (
                  events.map((event) => (
                    <div
                      key={event.id}
                      className={`event-item ${selectedEvent === event.event_name ? "selected" : ""}`}
                      onClick={() => handleEventSelect(event.event_name)}
                    >
                      <i className="bi bi-box-arrow-in-right"></i>
                      <span>{event.event_name_cn || event.event_name}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </Card.Body>
        </Card>

        <Card className="generate-panel">
          <Card.Body>
            <h3>生成配置</h3>
            <Button
              variant="primary"
              onClick={handleGenerate}
              disabled={!selectedEvent || isGenerating}
            >
              {isGenerating ? "生成中..." : "生成HQL"}
            </Button>

            {isGenerating && (
              <div className="loading-state">
                <Spinner size="sm" />
                <span>正在生成HQL语句...</span>
              </div>
            )}
          </Card.Body>
        </Card>
      </div>
    </div>
  );
}

// 使用 React.memo 优化性能
export default React.memo(Generate);
