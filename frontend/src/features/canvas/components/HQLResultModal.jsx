/**
 * HQL Result Modal Component
 * Display HQL generation results with syntax highlighting, formatting, and export options
 *
 * Features:
 * - Prism.js syntax highlighting
 * - SQL formatting (sql-formatter library)
 * - Raw/Formatted toggle
 * - One-click copy
 * - File download
 * - Full-screen edit mode
 * - Data preview (NEW in v1.2.0)
 *
 * @version 1.2.0
 * @date 2026-01-29
 */

import React, { useState, useEffect, useRef, useMemo } from "react";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { BaseModal } from '@shared/ui/BaseModal';
import { formatSQL, calculateSQLStats } from '@shared/utils/sqlFormatter';
import DataPreviewModal from './DataPreviewModal';
import "./HQLResultModal.css";

export default function HQLResultModal({
  isOpen,
  hql,
  onClose,
  onRegenerate,
  gameData,
  flowName = 'flow',
  outputFields = []
}) {
  const [editedHQL, setEditedHQL] = useState(hql);
  const [initialHQL, setInitialHQL] = useState(hql);
  const [hasChanges, setHasChanges] = useState(false);
  const [format, setFormat] = useState('formatted'); // 'raw' | 'formatted'
  const [isEditing, setIsEditing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showDataPreview, setShowDataPreview] = useState(false);
  const textareaRef = useRef(null);

  // 当hql prop变化时更新本地状态
  useEffect(() => {
    if (isOpen) {
      setEditedHQL(hql);
      setInitialHQL(hql);
      setHasChanges(false);
      setIsEditing(false);
      setFormat('formatted');
    }
  }, [hql, isOpen]);

  // Format HQL based on selected format
  const displayHQL = useMemo(() => {
    if (!hql) return '';
    if (isEditing) return editedHQL; // In edit mode, show edited version
    if (format === 'raw') return hql;
    return formatSQL(hql);
  }, [hql, format, isEditing, editedHQL]);

  // Calculate statistics for current display
  const stats = useMemo(() => {
    return calculateSQLStats(displayHQL);
  }, [displayHQL]);

  // 监听内容变化
  const handleHQLChange = (e) => {
    const newHQL = e.target.value;
    setEditedHQL(newHQL);
    setHasChanges(newHQL !== initialHQL);
  };

  // 复制到剪贴板
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(displayHQL);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      // 降级方案
      const textarea = document.createElement("textarea");
      textarea.value = displayHQL;
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand("copy");
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (e) {
        showToastNotification("复制失败，请手动复制", "error", 3000);
      }
      document.body.removeChild(textarea);
    }
  };

  // 下载SQL文件
  const handleDownload = () => {
    try {
      const blob = new Blob([displayHQL], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${flowName}_${gameData?.gid || "output"}_${Date.now()}.hql`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      showToastNotification("下载成功", "success", 2000);
    } catch (err) {
      showToastNotification("下载失败", "error", 3000);
    }
  };

  // Enable edit mode
  const handleEnableEdit = () => {
    setEditedHQL(displayHQL);
    setIsEditing(true);
  };

  // Save edit
  const handleSaveEdit = () => {
    showToastNotification("编辑已保存（仅用于展示）", "success", 2000);
    setIsEditing(false);
  };

  // Cancel edit
  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedHQL(initialHQL);
    setHasChanges(false);
  };

  // 重新生成HQL
  const handleRegenerate = () => {
    if (hasChanges) {
      if (window.confirm("重新生成将覆盖您的修改，是否继续？")) {
        onClose(); // 关闭当前Modal
        onRegenerate(); // 触发重新生成
      }
    } else {
      onClose();
      onRegenerate();
    }
  };

  // 关闭Modal（如果有修改则确认）
  const handleClose = () => {
    if (hasChanges) {
      if (window.confirm("您有未保存的修改，确定要关闭吗？")) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  // ESC键关闭
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === "Escape" && isOpen) {
        handleClose();
      }
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [isOpen, hasChanges]);

  // Tab键支持
  const handleKeyDown = (e) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const start = e.target.selectionStart;
      const end = e.target.selectionEnd;
      const newValue =
        editedHQL.substring(0, start) + "    " + editedHQL.substring(end);
      setEditedHQL(newValue);
      // 设置光标位置
      setTimeout(() => {
        e.target.selectionStart = e.target.selectionEnd = start + 4;
      }, 0);
    }
  };

  if (!isOpen) return null;

  if (!hql) {
    return (
      <BaseModal
        isOpen={isOpen}
        onClose={handleClose}
        title="HQL生成结果"
        size="modal-lg"
      >
        <div className="hql-result-modal">
          <div className="empty-state">
            <i className="bi bi-code-slash" style={{ fontSize: '3rem', marginBottom: '1rem' }}></i>
            <h3>没有HQL内容</h3>
            <p>生成HQL时出错或画布为空</p>
          </div>
          <div className="modal-footer">
            <button className="btn btn-secondary" onClick={handleClose}>
              关闭
            </button>
          </div>
        </div>
      </BaseModal>
    );
  }

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={handleClose}
      title={
        <span>
          HQL生成结果
          {hasChanges && (
            <span className="hql-modal-changed-indicator"> ● 已修改</span>
          )}
        </span>
      }
      size="modal-xl"
    >
      <div className="hql-result-modal">
        {/* Toolbar */}
        <div className="hql-toolbar">
          <div className="toolbar-left">
            <button
              className={`btn btn-sm ${format === 'raw' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFormat('raw')}
              type="button"
              disabled={isEditing}
            >
              原始
            </button>
            <button
              className={`btn btn-sm ${format === 'formatted' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFormat('formatted')}
              type="button"
              disabled={isEditing}
            >
              格式化
            </button>
          </div>

          <div className="toolbar-right">
            <button
              className="btn btn-sm btn-outline-primary"
              onClick={handleCopy}
              type="button"
              title={copied ? '已复制' : '复制到剪贴板'}
            >
              <i className={`bi ${copied ? 'bi-check' : 'bi-clipboard'}`}></i>
              {copied ? '已复制' : '复制'}
            </button>
            <button
              className="btn btn-sm btn-outline-primary"
              onClick={handleDownload}
              type="button"
              title="下载为文件"
            >
              <i className="bi bi-download"></i>
              下载
            </button>
            <button
              className="btn btn-sm btn-outline-success"
              onClick={() => setShowDataPreview(true)}
              type="button"
              title="预览数据"
              disabled={!hql || outputFields.length === 0}
            >
              <i className="bi bi-table"></i>
              预览数据
            </button>
            {!isEditing && (
              <button
                className="btn btn-sm btn-outline-primary"
                onClick={handleEnableEdit}
                type="button"
                title="编辑HQL"
              >
                <i className="bi bi-pencil"></i>
                编辑
              </button>
            )}
            {onRegenerate && (
              <button
                className="btn btn-sm btn-primary"
                onClick={handleRegenerate}
                type="button"
                title="重新生成HQL"
              >
                <i className="bi bi-arrow-clockwise"></i>
                重新生成
              </button>
            )}
          </div>
        </div>

        {/* HQL Content Display */}
        <div className="hql-content">
          {!isEditing ? (
            // Preview mode with syntax highlighting
            <div className="hql-preview">
              <SyntaxHighlighter
                language="sql"
                style={vscDarkPlus}
                showLineNumbers
                startingLineNumber={1}
                customStyle={{
                  margin: 0,
                  borderRadius: '8px',
                  fontSize: '0.875rem',
                  maxHeight: '60vh',
                  overflow: 'auto'
                }}
              >
                {displayHQL}
              </SyntaxHighlighter>
            </div>
          ) : (
            // Edit mode
            <div className="hql-edit">
              <textarea
                ref={textareaRef}
                className="form-control hql-editor"
                value={editedHQL}
                onChange={handleHQLChange}
                onKeyDown={handleKeyDown}
                rows={20}
                style={{
                  fontFamily: "'JetBrains Mono', 'Courier New', monospace",
                  fontSize: '0.875rem',
                  minHeight: '60vh',
                  width: '100%'
                }}
                placeholder="在此编辑HQL..."
                spellCheck={false}
              />
              {hasChanges && (
                <div className="alert alert-warning mt-2">
                  <i className="bi bi-exclamation-triangle"></i>
                  {' '}您已修改HQL内容，修改仅用于展示
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer with statistics */}
        {!isEditing && (
          <div className="hql-footer">
            <span className="text-muted">
              <i className="bi bi-info-circle"></i>
              {' '}字符数: {stats.characterCount.toLocaleString()} |
              {' '}行数: {stats.lineCount} |
              {' '}关键字: {stats.keywordCount}
            </span>
          </div>
        )}

        {/* Edit mode buttons */}
        {isEditing && (
          <div className="modal-footer">
            <button className="btn btn-secondary" onClick={handleCancelEdit}>
              取消
            </button>
            <button className="btn btn-primary" onClick={handleSaveEdit}>
              <i className="bi bi-save"></i>
              保存编辑
            </button>
          </div>
        )}
      </div>

      {/* Data Preview Modal */}
      {showDataPreview && (
        <DataPreviewModal
          isOpen={showDataPreview}
          onClose={() => setShowDataPreview(false)}
          sql={displayHQL}
          outputFields={outputFields}
          gameData={gameData}
        />
      )}
    </BaseModal>
  );
}

// Toast通知函数（临时实现，后续可以统一到ToastNotification组件）
function showToastNotification(message, type = "info", duration = 3000) {
  // 创建Toast元素
  const toast = document.createElement("div");
  toast.className = `hql-toast hql-toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  // 触发动画
  setTimeout(() => toast.classList.add("hql-toast-show"), 10);

  // 自动移除
  setTimeout(() => {
    toast.classList.remove("hql-toast-show");
    setTimeout(() => document.body.removeChild(toast), 300);
  }, duration);
}
