/**
 * Data Preview Modal Component
 * Displays preview data for HQL execution results
 *
 * Features:
 * - Table view of result data
 * - Pagination support
 * - Loading states
 * - Error handling
 * - Export to CSV
 *
 * @version 1.0.0
 * @date 2026-01-29
 */

import React, { useState, useEffect } from 'react';
import { BaseModal, Pagination, Button, Spinner } from '@shared/ui';
import './DataPreviewModal.css';
import type { DataPreviewModalProps, PreviewDataResponse } from './types';

export default function DataPreviewModal({
  isOpen,
  onClose,
  sql,
  outputFields = [],
  gameData
}: DataPreviewModalProps): React.JSX.Element | null {
  const [data, setData] = useState<PreviewDataResponse['data'] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<number>(1);
  const [pageSize] = useState<number>(10);
  const [exporting, setExporting] = useState<boolean>(false);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setPage(1);
      setError(null);
      // Auto-load preview when modal opens
      loadPreviewData();
    }
  }, [isOpen, sql]);

  // Load preview data from backend
  const loadPreviewData = async (): Promise<void> => {
    if (!sql) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/canvas/api/preview-results', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sql,
          output_fields: outputFields || [],
          limit: 100 // Get more rows for local pagination
        })
      });

      const result: PreviewDataResponse = await response.json();

      if (result.success && result.data) {
        setData(result.data);
      } else {
        setError(result.message || 'Failed to load preview data');
      }
    } catch (err) {
      console.error('[DataPreviewModal] Error loading preview:', err);
      setError('Network error: Failed to load preview data');
    } finally {
      setLoading(false);
    }
  };

  // Export to CSV
  const handleExportCSV = (): void => {
    if (!data || !data.columns || !data.rows) return;

    setExporting(true);

    try {
      // Create CSV content
      const csvRows: string[] = [];
      csvRows.push(data.columns.join(','));

      data.rows.forEach(row => {
        csvRows.push(row.map(cell =>
          typeof cell === 'string' ? `"${cell.replace(/"/g, '""')}"` : cell
        ).join(','));
      });

      const csvContent = csvRows.join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `preview_${gameData?.name || 'data'}_${new Date().toISOString().slice(0, 10)}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('[DataPreviewModal] Export error:', err);
    } finally {
      setExporting(false);
    }
  };

  // Calculate pagination
  const totalPages = data ? Math.ceil(data.row_count / pageSize) : 1;
  const startIndex = (page - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentRows = data ? data.rows.slice(startIndex, endIndex) : [];

  // Format cell value for display
  const formatCellValue = (value: unknown, column: string): React.ReactNode => {
    if (value === null || value === undefined) {
      return <span className="null-value">NULL</span>;
    }

    if (typeof value === 'boolean') {
      return <span className={`boolean-value ${value}`}>{value.toString()}</span>;
    }

    if (typeof value === 'number') {
      return <span className="number-value">{value.toLocaleString()}</span>;
    }

    return String(value);
  };

  if (!isOpen) return null;

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      title="数据预览"
      size="xl"
      className="data-preview-modal"
    >
      <div className="data-preview-content">
        {/* Header Actions */}
        <div className="preview-header">
          <div className="preview-info">
            {data && (
              <>
                <span className="row-count">{data.row_count} 行</span>
                <span className="execution-time">
                  执行时间: {data.execution_time_ms}ms
                </span>
              </>
            )}
          </div>
          <div className="preview-actions">
            <Button
              variant="secondary"
              size="sm"
              onClick={loadPreviewData}
              loading={loading}
              title="刷新数据"
            >
              {loading ? '加载中...' : '刷新'}
            </Button>
            {data && data.rows.length > 0 && (
              <Button
                variant="success"
                size="sm"
                onClick={handleExportCSV}
                loading={exporting}
                title="导出CSV"
              >
                {exporting ? '导出中...' : '导出CSV'}
              </Button>
            )}
          </div>
        </div>

        {/* Loading State */}
        {loading && !data && (
          <div className="preview-loading">
            <Spinner size="lg" />
            <p>正在加载预览数据...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="preview-error">
            <div className="error-icon">⚠️</div>
            <div className="error-message">{error}</div>
            <Button
              variant="danger"
              size="sm"
              onClick={loadPreviewData}
            >
              重试
            </Button>
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && data && data.rows.length === 0 && (
          <div className="preview-empty">
            <div className="empty-icon">📭</div>
            <p>无数据返回</p>
          </div>
        )}

        {/* Data Table */}
        {!loading && !error && data && data.rows.length > 0 && (
          <div className="preview-table-container">
            <table className="preview-table">
              <thead>
                <tr>
                  <th className="row-number-header">#</th>
                  {data.columns.map((column, index) => (
                    <th key={index}>{column}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {currentRows.map((row, rowIndex) => (
                  <tr key={startIndex + rowIndex}>
                    <td className="row-number">{startIndex + rowIndex + 1}</td>
                    {row.map((cell, cellIndex) => (
                      <td key={cellIndex}>
                        {formatCellValue(cell, data.columns[cellIndex])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            {totalPages > 1 && (
              <Pagination
                currentPage={page}
                totalPages={totalPages}
                pageSize={pageSize}
                totalItems={data.row_count}
                onPageChange={setPage}
                showPageSize={false}
                className="preview-pagination"
              />
            )}
          </div>
        )}

        {/* Footer Info */}
        {data && !loading && !error && (
          <div className="preview-footer">
            <div className="field-info">
              <strong>字段数:</strong> {data.columns.length}
            </div>
            <div className="sample-notice">
              ℹ️ 显示预览数据 (最多 {data.row_count} 行)
            </div>
          </div>
        )}
      </div>
    </BaseModal>
  );
}
