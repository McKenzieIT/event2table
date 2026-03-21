// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
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
 * @migrated-to-typescript 2026-02-27
 */

import React, { useState, useEffect, useRef, useMemo, ChangeEvent, KeyboardEvent, Suspense } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Modal, EmptyState, Spinner } from '@shared/ui';
import { formatSQL, calculateSQLStats } from '@shared/utils/sqlFormatter';
import { usePromiseConfirm } from '@shared/hooks/usePromiseConfirm';
import { LazyDataPreviewModal } from '@shared/utils/lazyModals';
import './HQLResultModal.css';

// ============================================
// Type Definitions
// ============================================

/**
 * HQL Result Modal-specific game data structure
 */
export interface HQLResultModalGameData {
  ods_db?: string;
  gid?: string | number;
  name?: string;
  [key: string]: unknown;
}

/**
 * Output field structure
 */
export interface OutputField {
  field_name?: string;
  fieldName?: string;
  field_type?: string;
  fieldType?: string;
  alias?: string;
  [key: string]: unknown;
}

/**
 * HQL statistics
 */
interface SQLStats {
  characterCount: number;
  lineCount: number;
  keywordCount: number;
}

/**
 * Format type for HQL display
 */
type HQLFormat = 'raw' | 'formatted';

/**
 * Component Props
 */
export interface HQLResultModalProps {
  /** Whether the modal is open */
  isOpen: boolean;
  /** The HQL content to display */
  hql: string;
  /** Callback when modal is closed */
  onClose: () => void;
  /** Callback to regenerate HQL */
  onRegenerate?: () => void;
  /** Game data for context */
  gameData?: HQLResultModalGameData | null;
  /** Flow name for file download */
  flowName?: string;
  /** Output fields for data preview */
  outputFields?: OutputField[];
}

// ============================================
// Toast Notification Utility
// ============================================

/**
 * Toast notification types
 */
type ToastType = 'info' | 'success' | 'error' | 'warning';

/**
 * Show toast notification
 * @param message - The message to display
 * @param type - The type of toast
 * @param duration - Duration in milliseconds
 */
function showToastNotification(
  message: string,
  type: ToastType = 'info',
  duration: number = 3000
): void {
  // Create toast element
  const toast = document.createElement('div');
  toast.className = `hql-toast hql-toast-${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  // Trigger animation
  setTimeout(() => toast.classList.add('hql-toast-show'), 10);

  // Auto remove
  setTimeout(() => {
    toast.classList.remove('hql-toast-show');
    setTimeout(() => document.body.removeChild(toast), 300);
  }, duration);
}

// ============================================
// Main Component
// ============================================

/**
 * HQL Result Modal Component
 *
 * @example
 * ```tsx
 * <HQLResultModal
 *   isOpen={true}
 *   hql={generatedHQL}
 *   onClose={handleClose}
 *   onRegenerate={handleRegenerate}
 *   gameData={gameData}
 *   flowName="my_flow"
 *   outputFields={fields}
 * />
 * ```
 */
const HQLResultModal: React.FC<HQLResultModalProps> = ({
  isOpen,
  hql,
  onClose,
  onRegenerate,
  gameData,
  flowName = 'flow',
  outputFields = []
}) => {
  // ============================================
  // State
  // ============================================

  const [editedHQL, setEditedHQL] = useState<string>(hql);
  const [initialHQL, setInitialHQL] = useState<string>(hql);
  const [hasChanges, setHasChanges] = useState<boolean>(false);
  const [format, setFormat] = useState<HQLFormat>('formatted');
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);
  const [showDataPreview, setShowDataPreview] = useState<boolean>(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Promise-based confirm dialog
  const { confirm, ConfirmDialogComponent } = usePromiseConfirm();

  // ============================================
  // Effects
  // ============================================

  /**
   * Update local state when hql prop changes
   */
  useEffect(() => {
    if (isOpen) {
      setEditedHQL(hql);
      setInitialHQL(hql);
      setHasChanges(false);
      setIsEditing(false);
      setFormat('formatted');
    }
  }, [hql, isOpen]);

  /**
   * Handle ESC key to close modal
   */
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent<Document>) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };

    window.addEventListener('keydown', handleEsc as unknown as EventListener);
    return () => window.removeEventListener('keydown', handleEsc as unknown as EventListener);
  }, [isOpen, hasChanges]);

  // ============================================
  // Computed Values
  // ============================================

  /**
   * Format HQL based on selected format
   */
  const displayHQL = useMemo(() => {
    if (!hql) return '';
    if (isEditing) return editedHQL; // In edit mode, show edited version
    if (format === 'raw') return hql;
    return formatSQL(hql);
  }, [hql, format, isEditing, editedHQL]);

  /**
   * Calculate statistics for current display
   */
  const stats = useMemo((): SQLStats => {
    return calculateSQLStats(displayHQL);
  }, [displayHQL]);

  // ============================================
  // Event Handlers
  // ============================================

  /**
   * Handle HQL content change
   */
  const handleHQLChange = (e: ChangeEvent<HTMLTextAreaElement>): void => {
    const newHQL = e.target.value;
    setEditedHQL(newHQL);
    setHasChanges(newHQL !== initialHQL);
  };

  /**
   * Copy HQL to clipboard
   */
  const handleCopy = async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(displayHQL);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      // Fallback method
      const textarea = document.createElement('textarea');
      textarea.value = displayHQL;
      document.body.appendChild(textarea);
      textarea.select();
      try {
        document.execCommand('copy');
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      } catch (e) {
        showToastNotification('复制失败，请手动复制', 'error', 3000);
      }
      document.body.removeChild(textarea);
    }
  };

  /**
   * Download HQL as file
   */
  const handleDownload = (): void => {
    try {
      const blob = new Blob([displayHQL], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${flowName}_${gameData?.gid || 'output'}_${Date.now()}.hql`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      showToastNotification('下载成功', 'success', 2000);
    } catch (err) {
      showToastNotification('下载失败', 'error', 3000);
    }
  };

  /**
   * Enable edit mode
   */
  const handleEnableEdit = (): void => {
    setEditedHQL(displayHQL);
    setIsEditing(true);
  };

  /**
   * Save edit
   */
  const handleSaveEdit = (): void => {
    showToastNotification('编辑已保存（仅用于展示）', 'success', 2000);
    setIsEditing(false);
  };

  /**
   * Cancel edit
   */
  const handleCancelEdit = (): void => {
    setIsEditing(false);
    setEditedHQL(initialHQL);
    setHasChanges(false);
  };

  /**
   * Regenerate HQL
   */
  const handleRegenerate = async (): Promise<void> => {
    if (hasChanges) {
      if (await confirm('重新生成将覆盖您的修改，是否继续？')) {
        onClose(); // Close current modal
        onRegenerate?.(); // Trigger regeneration
      }
    } else {
      onClose();
      onRegenerate?.();
    }
  };

  /**
   * Close modal (with confirmation if there are changes)
   */
  const handleClose = async (): Promise<void> => {
    if (hasChanges) {
      if (await confirm('您有未保存的修改，确定要关闭吗？')) {
        onClose();
      }
    } else {
      onClose();
    }
  };

  /**
   * Handle Tab key in textarea
   */
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>): void => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const start = e.currentTarget.selectionStart;
      const end = e.currentTarget.selectionEnd;
      const newValue =
        editedHQL.substring(0, start) + '    ' + editedHQL.substring(end);
      setEditedHQL(newValue);
      // Set cursor position
      setTimeout(() => {
        if (e.currentTarget) {
          e.currentTarget.selectionStart = e.currentTarget.selectionEnd = start + 4;
        }
      }, 0);
    }
  };

  // ============================================
  // Render
  // ============================================

  if (!isOpen) return null;

  // Empty state when no HQL is provided
  if (!hql) {
    return (
      <Modal
        isOpen={isOpen}
        onClose={handleClose}
        title="HQL生成结果"
        size="lg"
      >
        <div className="hql-result-modal">
          <EmptyState
            icon={<i className="bi bi-code-slash" style={{ fontSize: '48px' }} />}
            title="没有HQL内容"
            description="生成HQL时出错或画布为空"
          />
          <div className="modal-footer">
            <button className="btn btn-secondary" onClick={handleClose}>
              关闭
            </button>
          </div>
        </div>
      </Modal>
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
      size="xl"
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

      {/* Data Preview Modal - Lazy loaded */}
      {showDataPreview && (
        <Suspense fallback={<Spinner size="lg" label="加载中..." />}>
          <LazyDataPreviewModal
            isOpen={showDataPreview}
            onClose={() => setShowDataPreview(false)}
            sql={displayHQL}
            outputFields={outputFields}
            gameData={gameData}
          />
        </Suspense>
      )}

      {/* Promise-based confirm dialog */}
      <ConfirmDialogComponent />
    </BaseModal>
  );
};

export default HQLResultModal;
