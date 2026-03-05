// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * CodeBlock Component
 * Reusable syntax highlighting component with copy functionality
 *
 * Features:
 * - Syntax highlighting using react-syntax-highlighter
 * - vscDarkPlus theme (VS Code Dark+)
 * - Line numbers (optional)
 * - Copy to clipboard button
 * - Configurable max height with scroll
 *
 * @component CodeBlock
 *
 * @example
 * <CodeBlock
 *   code="SELECT * FROM table"
 *   language="sql"
 *   showLineNumbers={true}
 *   maxHeight="400px"
 * />
 */

import React, { useState, useCallback } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './CodeBlock.css';

interface CodeBlockProps {
  /** Code content to display */
  code: string;
  /** Programming language for syntax highlighting */
  language?: string;
  /** Whether to show line numbers */
  showLineNumbers?: boolean;
  /** Maximum height of the code block */
  maxHeight?: string;
  /** Additional CSS class name */
  className?: string;
}

/**
 * CodeBlock Component
 */
export default function CodeBlock({
  code,
  language = 'sql',
  showLineNumbers = true,
  maxHeight = '400px',
  className = ''
}: CodeBlockProps): React.JSX.Element {
  const [copied, setCopied] = useState(false);

  // Copy to clipboard handler
  const handleCopy = useCallback(async () => {
    if (!code) return;

    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);

      // Toast notification
      if (window.toast) {
        window.toast.success('已复制到剪贴板');
      }
    } catch (error) {
      console.error('[CodeBlock] 复制失败:', error);
      if (window.toast) {
        window.toast.error('复制失败，请手动复制');
      }
    }
  }, [code]);

  // Handle empty code
  if (!code) {
    return (
      <div className={`code-block code-block--empty ${className}`}>
        <div className="code-block__placeholder">
          <i className="bi bi-code-slash"></i>
          <span>暂无代码内容</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`code-block ${className}`}>
      {/* Copy Button */}
      <button
        className={`code-block__copy-btn ${copied ? 'copied' : ''}`}
        onClick={handleCopy}
        title={copied ? '已复制' : '复制到剪贴板'}
        type="button"
      >
        <i className={`bi ${copied ? 'bi-check-lg' : 'bi-clipboard'}`}></i>
        {copied ? '已复制' : '复制'}
      </button>

      {/* Syntax Highlighter */}
      <SyntaxHighlighter
        language={language}
        style={vscDarkPlus}
        showLineNumbers={showLineNumbers}
        startingLineNumber={1}
        customStyle={{
          margin: 0,
          padding: '16px',
          borderRadius: '8px',
          fontSize: '0.875rem',
          maxHeight: maxHeight,
          overflow: 'auto',
          background: 'transparent'
        }}
        wrapLines={true}
        wrapLongLines={true}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  );
}

CodeBlock.displayName = 'CodeBlock';
