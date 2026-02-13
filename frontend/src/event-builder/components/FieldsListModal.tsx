/**
 * 字段列表模态框组件
 * Fields List Modal Component
 *
 * @description 显示事件节点的所有字段配置
 */

import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import { eventNodesApi } from "@shared/api/eventNodes";
import type { EventNodeField } from "@shared/types/eventNodes";

/**
 * Props接口
 */
interface FieldsListModalProps {
  show: boolean;
  nodeId: number | null;
  nodeName?: string;
  onClose: () => void;
}

/**
 * 字段列表模态框组件
 */
export function FieldsListModal({
  show,
  nodeId,
  nodeName,
  onClose,
}: FieldsListModalProps) {
  const [fields, setFields] = useState<EventNodeField[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  // Toast 辅助函数
  const success = (message: string) => toast.success(message);
  const error = (message: string) => toast.error(message);

  // 加载字段列表
  useEffect(() => {
    if (!show || !nodeId) {
      return;
    }

    const fetchFields = async () => {
      setLoading(true);
      try {
        const response = await eventNodesApi.getFields(nodeId);
        const rawFields = response.data?.fields || [];

        // 转换后端 snake_case 到前端 camelCase
        const transformedFields = rawFields.map((field: any) => ({
          name: field.name || "",
          alias: field.alias || "",
          dataType: field.data_type || "unknown", // snake_case → camelCase
          baseType: field.base_type || "unknown", // snake_case → camelCase
          mapping: field.mapping || field.source || "", // 使用 source 作为映射
        }));

        setFields(transformedFields);
      } catch (err) {
        console.error("Failed to fetch fields:", err);
        // 不在这里调用 error，避免循环
      } finally {
        setLoading(false);
      }
    };

    fetchFields();
  }, [show, nodeId]); // 只依赖 show 和 nodeId

  // 重置状态
  useEffect(() => {
    if (!show) {
      setFields([]);
      setSearchTerm("");
    }
  }, [show]);

  // 过滤字段
  const filteredFields = fields.filter(
    (field) =>
      (field.name?.toLowerCase() || "").includes(searchTerm.toLowerCase()) ||
      (field.alias?.toLowerCase() || "").includes(searchTerm.toLowerCase()),
  );

  // 导出CSV
  const handleExportCSV = () => {
    if (filteredFields.length === 0) {
      error("没有可导出的字段");
      return;
    }

    const headers = ["字段名", "别名", "数据类型", "基础类型", "映射表达式"];
    const rows = filteredFields.map((field) => [
      field.name,
      field.alias,
      field.dataType,
      field.baseType,
      field.mapping || "",
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(",")),
    ].join("\n");

    const blob = new Blob(["\ufeff" + csvContent], {
      type: "text/csv;charset=utf-8;",
    });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);

    link.setAttribute("href", url);
    link.setAttribute("download", `${nodeName || "node"}_fields.csv`);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    success("字段列表已导出");
  };

  if (!show) {
    return null;
  }

  return (
    <div
      className={`modal fade ${show ? "show" : ""}`}
      style={{
        display: show ? "block" : "none",
        backgroundColor: "rgba(0,0,0,0.5)",
      }}
      tabIndex={-1}
      role="dialog"
      aria-labelledby="fieldsModalLabel"
    >
      <div className="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
        <div className="modal-content">
          {/* 模态框头部 */}
          <div className="modal-header">
            <h5 className="modal-title" id="fieldsModalLabel">
              <i className="bi bi-list-check text-info me-2"></i>
              字段列表
              {nodeName && (
                <span className="text-muted ms-2">({nodeName})</span>
              )}
            </h5>
            <button
              type="button"
              className="btn-close"
              onClick={onClose}
              aria-label="关闭"
            ></button>
          </div>

          {/* 模态框内容 */}
          <div className="modal-body">
            {loading ? (
              <div className="text-center p-5">
                <div className="spinner-border" role="status">
                  <span className="visually-hidden">加载中...</span>
                </div>
                <p className="mt-3 text-muted">加载字段列表中...</p>
              </div>
            ) : fields.length === 0 ? (
              <div className="text-center p-5 text-muted">
                <i className="bi bi-inbox display-4 mb-3"></i>
                <p>暂无字段配置</p>
              </div>
            ) : (
              <>
                {/* 工具栏 */}
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <div
                    className="flex-grow-1 me-3"
                    style={{ maxWidth: "400px" }}
                  >
                    <div className="position-relative">
                      <i className="bi bi-search position-absolute top-50 start-3 translate-middle-y text-muted"></i>
                      <input
                        type="text"
                        className="form-control ps-5"
                        placeholder="搜索字段名称或别名..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="text-muted">
                    共 <strong>{filteredFields.length}</strong> 个字段
                  </div>
                </div>

                {/* 字段表格 */}
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th style={{ width: "25%" }}>字段名</th>
                        <th style={{ width: "20%" }}>别名</th>
                        <th style={{ width: "15%" }}>数据类型</th>
                        <th style={{ width: "15%" }}>基础类型</th>
                        <th style={{ width: "25%" }}>映射表达式</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredFields.length === 0 ? (
                        <tr>
                          <td
                            colSpan={5}
                            className="text-center text-muted py-5"
                          >
                            没有找到匹配的字段
                          </td>
                        </tr>
                      ) : (
                        filteredFields.map((field, index) => (
                          <tr key={index}>
                            <td>
                              <code className="text-primary">
                                {field.name || "-"}
                              </code>
                            </td>
                            <td>{field.alias || "-"}</td>
                            <td>
                              <span className="badge bg-info text-dark">
                                {field.dataType}
                              </span>
                            </td>
                            <td>
                              <span className="badge bg-secondary">
                                {field.baseType}
                              </span>
                            </td>
                            <td>
                              {field.mapping ? (
                                <code
                                  className="text-muted"
                                  style={{ fontSize: "0.85em" }}
                                >
                                  {field.mapping}
                                </code>
                              ) : (
                                <span className="text-muted">-</span>
                              )}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>

          {/* 模态框底部 */}
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-outline-primary me-auto"
              onClick={handleExportCSV}
              disabled={loading || fields.length === 0}
            >
              <i className="bi bi-download me-2"></i>
              导出CSV
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
