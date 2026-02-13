/**
 * HQL查看模态框组件
 * HQL View Modal Component
 *
 * @description 显示事件节点生成的HQL代码，支持语法高亮和复制
 */

import React, { useState, useEffect } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import toast from "react-hot-toast";
import { eventNodesApi } from "@shared/api/eventNodes";
import { Button } from "@shared/ui/Button";

/**
 * Props接口
 */
interface HQLViewModalProps {
  show: boolean;
  nodeId: number | null;
  onClose: () => void;
}

/**
 * HQL查看模态框组件
 */
export function HQLViewModal({ show, nodeId, onClose }: HQLViewModalProps) {
  const [hql, setHql] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  // Toast 辅助函数
  const success = (message: string) => toast.success(message);
  const error = (message: string) => toast.error(message);

  // 加载HQL代码
  useEffect(() => {
    if (!show || !nodeId) {
      return;
    }

    const fetchHql = async () => {
      setLoading(true);
      try {
        const response = await eventNodesApi.getHql(nodeId);
        setHql(response.data.hql);
      } catch (err) {
        console.error("Failed to fetch HQL:", err);
        error("加载HQL失败");
      } finally {
        setLoading(false);
      }
    };

    fetchHql();
  }, [show, nodeId, error]);

  // 重置状态
  useEffect(() => {
    if (!show) {
      setHql("");
      setLoading(false);
      setCopied(false);
    }
  }, [show]);

  // 复制到剪贴板
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(hql);
      setCopied(true);
      success("已复制到剪贴板");
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
      error("复制失败");
    }
  };

  // 重新生成HQL
  const handleRegenerate = async () => {
    if (!nodeId) return;

    setLoading(true);
    try {
      const response = await eventNodesApi.getHql(nodeId);
      setHql(response.data.hql);
      success("HQL已重新生成");
    } catch (err) {
      console.error("Failed to regenerate HQL:", err);
      error("重新生成失败");
    } finally {
      setLoading(false);
    }
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
      aria-labelledby="hqlModalLabel"
    >
      <div className="modal-dialog modal-xl modal-dialog-centered modal-dialog-scrollable">
        <div className="modal-content">
          {/* 模态框头部 */}
          <div className="modal-header">
            <h5 className="modal-title" id="hqlModalLabel">
              <i className="bi bi-code text-primary me-2"></i>
              HQL代码预览
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
                <p className="mt-3 text-muted">加载HQL代码中...</p>
              </div>
            ) : hql ? (
              <div className="position-relative">
                <SyntaxHighlighter
                  language="sql"
                  style={vscDarkPlus}
                  showLineNumbers
                  customStyle={{
                    borderRadius: "8px",
                    fontSize: "0.9rem",
                    maxHeight: "60vh",
                    overflow: "auto",
                  }}
                >
                  {hql}
                </SyntaxHighlighter>
              </div>
            ) : (
              <div className="text-center p-5 text-muted">
                <i className="bi bi-exclamation-triangle display-4 mb-3"></i>
                <p>无法加载HQL代码</p>
              </div>
            )}
          </div>

          {/* 模态框底部 */}
          <div className="modal-footer">
            <Button
              variant="outline-secondary"
              className="me-auto"
              onClick={handleRegenerate}
              disabled={loading}
            >
              🔄 重新生成
            </Button>
            <Button
              variant="secondary"
              onClick={onClose}
            >
              关闭
            </Button>
            <Button
              variant="primary"
              onClick={handleCopy}
              disabled={loading || !hql}
            >
              {copied ? "✓ 已复制" : "📋 复制到剪贴板"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
