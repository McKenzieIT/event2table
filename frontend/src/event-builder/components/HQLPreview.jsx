import React, { useState, useCallback, useEffect, forwardRef, useImperativeHandle } from 'react';
import PropTypes from 'prop-types';
import CodeMirror from '@uiw/react-codemirror';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { getBasicExtensions } from '@shared/utils/codemirrorConfig';
import { formatSQL as formatHQL } from '@shared/utils/sqlFormatter';
import { Spinner } from '@shared/ui';
import { usePromiseConfirm } from '@shared/hooks/usePromiseConfirm';
import './HQLPreview.css';

/**
 * HQL预览组件
 *
 * 功能:
 * - 双模式显示（预览/编辑）
 * - SQL语法高亮
 * - 支持 View/Procedure/Custom 三种模式
 * - 复制到剪贴板
 * - 下载为文件
 * - 实时预览（防抖300ms）
 *
 * @component HQLPreview
 *
 * @example
 * <HQLPreview
 *   hqlContent="-- Generated HQL"
 *   sqlMode="view"
 *   onModeChange={(mode) => console.log(mode)}
 *   onContentChange={(content) => console.log(content)}
 *   fields={fields}
 *   isLoading={false}
 * />
 */

/**
 * 主组件
 *
 * @param {Object} props - 组件属性
 * @param {string} props.hqlContent - HQL内容
 * @param {string} props.sqlMode - SQL模式 ('view' | 'procedure' | 'custom')
 * @param {Function} props.onModeChange - 模式切换回调
 * @param {Function} props.onContentChange - 内容变化回调
 * @param {boolean} [props.readOnly=false] - 是否只读
 * @param {Array} props.fields - 字段数组
 * @param {boolean} props.isLoading - 是否加载中
 */
const HQLPreview = forwardRef(({
  hqlContent = '',
  sqlMode = 'view',
  onModeChange,
  onContentChange,
  readOnly = false,
  fields = [],
  isLoading = false,
  onShowDetails
}, ref) => {
  // 确保 fields 是一个数组
  const safeFields = Array.isArray(fields) ? fields : [];

  // 状态管理
  const [isEditing, setIsEditing] = useState(false);
  const [copied, setCopied] = useState(false);
  const [editorContent, setEditorContent] = useState(hqlContent);
  const [hasModifications, setHasModifications] = useState(false);

  // 使用ref存储editorContent，避免handleFormat依赖editorContent
  const editorContentRef = React.useRef(editorContent);
  React.useEffect(() => {
    editorContentRef.current = editorContent;
  }, [editorContent]);

  // Promise-based confirm dialog
  const { confirm, ConfirmDialogComponent } = usePromiseConfirm();

  // 同步外部HQL内容到编辑器
  useEffect(() => {
    // 只有在非编辑状态下才自动更新
    if (!isEditing && !hasModifications) {
      setEditorContent(hqlContent);
    }
  }, [hqlContent, isEditing, hasModifications]);

  // 切换编辑模式
  const handleToggleEdit = useCallback(() => {
    setIsEditing(prev => {
      const newMode = !prev;
      // 切换到预览模式时，清空修改标记
      if (!newMode) {
        setHasModifications(false);
      }
      return newMode;
    });
  }, []);

  // 内容变化处理
  const handleEditorChange = useCallback((value) => {
    setEditorContent(value);
    setHasModifications(true);
    onContentChange?.(value);
  }, [onContentChange]);

  // 复制到剪贴板
  const handleCopy = useCallback(async () => {
    try {
      // 使用ref.current获取最新的editorContent
      await navigator.clipboard.writeText(editorContentRef.current);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);

      // Toast提示
      if (window.toast) {
        window.toast.success('已复制到剪贴板');
      } else {
        console.log('[HQLPreview] 已复制到剪贴板');
      }
    } catch (error) {
      console.error('[HQLPreview] 复制失败:', error);
      if (window.toast) {
        window.toast.error('复制失败，请手动复制');
      }
    }
  }, []); // 移除editorContent依赖，使用ref代替

  // 下载为文件
  const handleDownload = useCallback(() => {
    const filename = `hql_${sqlMode}_${Date.now()}.sql`;
    // 使用ref.current获取最新的editorContent
    const blob = new Blob([editorContentRef.current], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    if (window.toast) {
      window.toast.success(`已下载: ${filename}`);
    } else {
      console.log('[HQLPreview] 已下载:', filename);
    }
  }, [sqlMode]); // 移除editorContent依赖，使用ref代替

  // 模式切换
  const handleModeChange = useCallback(async (mode) => {
    if (hasModifications) {
      if (await confirm('切换模式将丢失当前编辑内容，确定要继续吗？')) {
        setHasModifications(false);
        onModeChange(mode);
      }
    } else {
      onModeChange(mode);
    }
  }, [hasModifications, onModeChange, confirm]);

  // 格式化SQL
  const handleFormat = useCallback(() => {
    try {
      // 使用ref.current获取最新的editorContent
      const formatted = formatHQL(editorContentRef.current);
      setEditorContent(formatted);
      setHasModifications(true);
      onContentChange?.(formatted);

      if (window.toast) {
        window.toast.success('SQL格式化成功');
      } else {
        console.log('[HQLPreview] SQL格式化成功');
      }
    } catch (error) {
      console.error('[HQLPreview] SQL格式化失败:', error);
      if (window.toast) {
        window.toast.error('SQL格式化失败，请检查语法');
      }
    }
  }, [onContentChange]); // 移除editorContent依赖，使用ref代替

  // 暴露格式化方法给父组件
  useImperativeHandle(ref, () => ({
    format: handleFormat
  }), [handleFormat]);

  // 空状态判断
  const isEmpty = !hqlContent && !editorContent;

  return (
    <div className="hql-preview-panel glass-card">
      {/* Header */}
      <div className="panel-header">
        <h3>
          <i className="bi bi-code-square"></i>
          HQL预览
          {hasModifications && (
            <span className="badge badge-warning ml-2">已修改</span>
          )}
        </h3>

        <div className="header-actions">
          {/* 模式切换 */}
          <div className="mode-switcher">
            <button
              className={`btn btn-sm ${sqlMode === 'view' ? 'btn-primary' : 'btn-outline-secondary'}`}
              onClick={() => handleModeChange('view')}
              disabled={readOnly}
              title="View模式 - 生成CREATE VIEW语句"
            >
              View
            </button>
            <button
              className={`btn btn-sm ${sqlMode === 'procedure' ? 'btn-primary' : 'btn-outline-secondary'}`}
              onClick={() => handleModeChange('procedure')}
              disabled={readOnly}
              title="Procedure模式 - 生成INSERT OVERWRITE语句"
            >
              Procedure
            </button>
            <button
              className={`btn btn-sm ${sqlMode === 'custom' ? 'btn-primary' : 'btn-outline-secondary'}`}
              onClick={() => handleModeChange('custom')}
              disabled={readOnly}
              title="自定义模式 - 完全手动编辑"
            >
              自定义
            </button>
          </div>

          {/* 操作按钮 */}
          {!isEmpty && (
            <>
              {!readOnly && (
                <>
                  <button
                    className="btn btn-sm btn-outline-secondary"
                    onClick={handleToggleEdit}
                    title={isEditing ? '切换到预览模式' : '切换到编辑模式'}
                  >
                    <i className={`bi bi-${isEditing ? 'eye' : 'pencil'}`}></i>
                    {isEditing ? '预览' : '编辑'}
                  </button>

                  <button
                    className="btn btn-sm btn-outline-secondary"
                    onClick={handleFormat}
                    title="格式化SQL (Ctrl/Cmd+Shift+F)"
                  >
                    <i className="bi bi-indent"></i>
                    格式化
                  </button>
                </>
              )}

              <button
                className="btn btn-sm btn-outline-secondary"
                onClick={handleCopy}
                title="复制到剪贴板"
              >
                <i className={`bi bi-clipboard${copied ? '-check' : ''}`}></i>
                {copied ? '已复制' : '复制'}
              </button>

              <button
                className="btn btn-sm btn-outline-primary"
                onClick={handleDownload}
                title="下载为文件"
              >
                <i className="bi bi-download"></i>
                下载
              </button>

              {onShowDetails && (
                <button
                  className="btn btn-sm btn-primary"
                  data-testid="open-hql-modal"
                  onClick={onShowDetails}
                  title="查看详情（全屏模式）"
                >
                  <i className="bi bi-fullscreen"></i>
                  查看详情
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="panel-content">
        {isLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '40px' }}>
            <Spinner size="lg" label="正在生成HQL..." />
          </div>
        ) : isEmpty ? (
          <div className="empty-state">
            <i className="bi bi-code-slash"></i>
            <p>添加字段后将在此处生成HQL</p>
          </div>
        ) : isEditing && !readOnly ? (
          // 编辑模式：CodeMirror
          <div className="hql-editor-wrapper">
            <CodeMirror
              value={editorContent}
              height="100%"
              extensions={getBasicExtensions(false)}
              onChange={handleEditorChange}
              basicSetup={{
                lineNumbers: true,
                highlightSpecialChars: true,
                foldGutter: true,
                drawSelection: true,
                dropCursor: true,
                allowMultipleSelections: true,
                indentOnInput: true,
                bracketMatching: true,
                closeBrackets: true,
                autocompletion: true,
                rectangularSelection: true,
                crosshairCursor: true,
                highlightActiveLineGutter: true,
                highlightSelectionMatches: true,
                closeBracketsKeymap: true,
                searchKeymap: true,
                foldKeymap: true,
                completionKeymap: true,
                lintKeymap: true
              }}
            />
          </div>
        ) : (
          // 预览模式：SyntaxHighlighter（轻量级）
          <div className="hql-preview-wrapper" data-testid="hql-preview-content">
            <SyntaxHighlighter
              language="sql"
              style={vscDarkPlus}
              customStyle={{
                background: 'transparent',
                padding: '16px',
                fontSize: '14px',
                lineHeight: '1.6'
              }}
              wrapLines={true}
              wrapLongLines={true}
              showLineNumbers={true}
            >
              {editorContent}
            </SyntaxHighlighter>
          </div>
        )}
      </div>

      {/* Footer */}
      {safeFields.length > 0 && (
        <div className="panel-footer">
          <small className="text-muted">
            <i className="bi bi-info-circle"></i>
            {' '}
            {safeFields.length} 个字段 | {sqlMode} 模式
            {hasModifications && ' | 已手动修改'}
          </small>
        </div>
      )}

      {/* Promise-based confirm dialog */}
      <ConfirmDialogComponent />
    </div>
  );
});

HQLPreview.displayName = 'HQLPreview';

HQLPreview.propTypes = {
  hqlContent: PropTypes.string,
  sqlMode: PropTypes.oneOf(['view', 'procedure', 'custom']),
  onModeChange: PropTypes.func,
  onContentChange: PropTypes.func,
  readOnly: PropTypes.bool,
  fields: PropTypes.arrayOf(PropTypes.object),
  isLoading: PropTypes.bool,
  onShowDetails: PropTypes.func
};

HQLPreview.defaultProps = {
  hqlContent: '',
  sqlMode: 'view',
  readOnly: false,
  fields: [],
  isLoading: false
};

export default HQLPreview;
