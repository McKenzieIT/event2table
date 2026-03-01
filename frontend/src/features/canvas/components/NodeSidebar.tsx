import React, { useState, useEffect } from "react";
import { useEventConfigs } from '../hooks/useEventConfigs';
import { Button, Spinner } from '@shared/ui';
import SearchBar from "./SearchBar";
import "./NodeSidebar.css";
import type { NodeSidebarProps, EventConfig, GameData } from "./types";

export default function NodeSidebar({
  gameData,
  savedConfigs,
  onConfigsLoad,
  onAddNode,
}: NodeSidebarProps): React.JSX.Element {
  const [isOpen, setIsOpen] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>("");

  // Use React Query hook to fetch event configs
  const { data, isLoading, error, refetch } = useEventConfigs(gameData?.gid || 0);

  // Call onConfigsLoad when data changes
  useEffect(() => {
    if (data && onConfigsLoad) {
      onConfigsLoad(data);
    }
  }, [data, onConfigsLoad]);

  // 搜索过滤逻辑
  const filteredConfigs = savedConfigs.filter((config) => {
    if (!searchTerm) return true;

    const term = searchTerm.toLowerCase();
    const nameMatch = config.name_cn?.toLowerCase().includes(term);
    const eventMatch = config.event_name_cn?.toLowerCase().includes(term);
    const eventNameMatch = config.event_name?.toLowerCase().includes(term);

    return nameMatch || eventMatch || eventNameMatch;
  });

  // 双击配置节点处理
  const onDoubleClickConfig = (config: EventConfig): void => {
    if (onAddNode) {
      const position = { x: 100, y: 100 };
      onAddNode({
        type: "saved-config",
        configId: config.id,
        label: config.name_cn || '',
        eventCnName: config.event_name_cn,
        eventName: config.event_name,
        fieldCount: config.base_fields ? config.base_fields.length : 0,
        icon: "⚙️",
        data: config,
        position,
      } as any);
    }
  };

  // 拖拽已保存的配置节点
  const onDragConfigStart = (event: React.DragEvent, config: EventConfig): void => {
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify({
        type: "saved-config",
        configId: config.id,
        label: config.name_cn,
        eventCnName: config.event_name_cn,
        eventName: config.event_name,
        fieldCount: config.base_fields ? config.base_fields.length : 0,
        icon: "⚙️",
      }),
    );
    event.dataTransfer.effectAllowed = "move";
  };

  // 拖拽连接节点
  const onDragConnectionStart = (event: React.DragEvent, connectionType: string): void => {
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify({
        type: connectionType,
        label: connectionType === "union_all" ? "UNION ALL" : "JOIN",
        icon: connectionType === "union_all" ? "🔀" : "🔗",
      }),
    );
    event.dataTransfer.effectAllowed = "move";
  };

  // 拖拽输出节点
  const onDragOutputStart = (event: React.DragEvent): void => {
    event.dataTransfer.setData(
      "application/reactflow",
      JSON.stringify({
        type: "output",
        label: "输出",
        icon: "📤",
      }),
    );
    event.dataTransfer.effectAllowed = "move";
  };

  return (
    <div className={`node-sidebar ${isOpen ? "open" : "closed"}`}>
      <div className="node-sidebar-header">
        <h3>节点库</h3>
        <Button
          onClick={() => setIsOpen(!isOpen)}
          variant="ghost"
          size="sm"
          className="toggle-btn"
          title={isOpen ? "收起侧边栏" : "展开侧边栏"}
        >
          {isOpen ? "◀" : "▶"}
        </Button>
      </div>

      {isOpen && (
        <div className="node-sidebar-content">
          <section className="node-sidebar-section">
            <SearchBar onSearch={setSearchTerm} />
          </section>

          <section className="node-sidebar-section">
            <h4>已保存配置</h4>
            {isLoading && (
              <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
                <Spinner size="md" label="加载中..." />
              </div>
            )}
            {error && (
              <div className="error-message">
                {(error as any).message || "加载配置失败"}
                <Button onClick={() => refetch()} variant="outline-primary" size="sm" className="retry-btn">
                  重试
                </Button>
              </div>
            )}
            {!isLoading && !error && (
              <div className="node-list">
                {filteredConfigs.length === 0 ? (
                  <p className="empty-message">
                    {searchTerm ? "没有找到匹配的配置" : "暂无保存的配置"}
                  </p>
                ) : (
                  filteredConfigs.map((config) => (
                    <div
                      key={config.id!}
                      className="node-sidebar-node saved-node"
                      draggable
                      onDragStart={(e) => onDragConfigStart(e, config)}
                      onDoubleClick={() => onDoubleClickConfig(config)}
                      title={`拖拽添加: ${config.name_cn}\n双击快速添加`}
                    >
                      <span className="node-icon">⚙️</span>
                      <div className="node-info">
                        <span className="node-label">{config.name_cn}</span>
                        <span className="node-sublabel">
                          {config.event_name_cn}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}
          </section>

          <section className="node-sidebar-section">
            <h4>连接节点</h4>
            <div className="node-list">
              <div
                className="node-sidebar-node connection-node"
                draggable
                onDragStart={(e) => onDragConnectionStart(e, "union_all")}
                onDoubleClick={() =>
                  onAddNode?.({
                    type: "union_all",
                    label: "UNION ALL",
                    icon: "🔀",
                  })
                }
                title="拖拽添加: UNION ALL 连接节点&#10;双击快速添加"
              >
                <span className="node-icon">🔀</span>
                <div className="node-info">
                  <span className="node-label">UNION ALL</span>
                  <span className="node-sublabel">合并多个查询结果</span>
                </div>
              </div>
              <div
                className="node-sidebar-node connection-node"
                draggable
                onDragStart={(e) => onDragConnectionStart(e, "join")}
                onDoubleClick={() =>
                  onAddNode?.({
                    type: "join",
                    label: "JOIN",
                    icon: "🔗",
                  })
                }
                title="拖拽添加: JOIN 连接节点&#10;双击快速添加"
              >
                <span className="node-icon">🔗</span>
                <div className="node-info">
                  <span className="node-label">JOIN</span>
                  <span className="node-sublabel">关联多个数据源</span>
                </div>
              </div>
            </div>
          </section>

          <section className="node-sidebar-section">
            <h4>输出节点</h4>
            <div className="node-list">
              <div
                className="node-sidebar-node output-node"
                draggable
                onDragStart={onDragOutputStart}
                onDoubleClick={() =>
                  onAddNode?.({
                    type: "output",
                    label: "输出",
                    icon: "📤",
                  })
                }
                title="拖拽添加: 输出节点&#10;双击快速添加"
              >
                <span className="node-icon">📤</span>
                <div className="node-info">
                  <span className="node-label">输出</span>
                  <span className="node-sublabel">生成最终的HQL</span>
                </div>
              </div>
            </div>
          </section>

          <section className="node-sidebar-section">
            <h4>信息</h4>
            <div className="node-sidebar-info">
              <p>游戏: {gameData?.name}</p>
              <p>GID: {gameData?.gid}</p>
              <p>配置数: {savedConfigs.length}</p>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
