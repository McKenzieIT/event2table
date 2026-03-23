import React, { useState } from 'react';

import { TablePaginationProps } from './Table.types';

/**
 * TablePagination Component
 * 
 * Renders pagination controls with support for:
 * - Page navigation
 * - Page size selection
 * - Quick jumper
 * - Total count display
 */
export const TablePagination = React.memo(({
  currentPage,
  pageSize,
  total,
  pageSizeOptions = [10, 20, 50, 100],
  onPageChange,
  showTotal,
  showSizeChanger = false,
  showQuickJumper = false,
  className = '',
}: TablePaginationProps) => {
  const [jumpPage, setJumpPage] = useState('');

  const totalPages = Math.ceil(total / pageSize);

  const handlePageChange = (page: number) => {
    const validPage = Math.max(1, Math.min(page, totalPages));
    onPageChange(validPage, pageSize);
  };

  const handlePageSizeChange = (newSize: number) => {
    onPageChange(1, newSize);
  };

  const handleJump = () => {
    const page = parseInt(jumpPage, 10);
    if (!isNaN(page) && page >= 1 && page <= totalPages) {
      handlePageChange(page);
      setJumpPage('');
    }
  };

  // ============================================================================
  // Page Number Generation - Extracted complex logic
  // ============================================================================

  const calculateVisiblePages = (currentPage: number, totalPages: number): Array<number | string> => {
    const pages: Array<number | string> = [];
    const maxVisible = 7;

    // Early return: show all pages if total is small
    if (totalPages <= maxVisible) {
      return Array.from({ length: totalPages }, (_, i) => i + 1);
    }

    pages.push(1);

    const halfVisible = Math.floor(maxVisible / 2);
    let start = Math.max(2, currentPage - halfVisible + 1);
    let end = Math.min(totalPages - 1, currentPage + halfVisible - 1);

    // Adjust for pages near the beginning
    if (currentPage <= halfVisible) {
      end = Math.min(totalPages - 1, maxVisible - 1);
    }

    // Adjust for pages near the end
    if (currentPage > totalPages - halfVisible) {
      start = Math.max(2, totalPages - maxVisible + 2);
    }

    // Add ellipsis before middle pages if needed
    if (start > 2) {
      pages.push('...');
    }

    // Add middle pages
    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    // Add ellipsis after middle pages if needed
    if (end < totalPages - 1) {
      pages.push('...');
    }

    pages.push(totalPages);

    return pages;
  };

  const renderPageNumbers = () => {
    return calculateVisiblePages(currentPage, totalPages);
  };

  const startItem = total === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, total);

  return (
    <div className={`table-pagination ${className}`}>
      {showTotal && (
        <div className="pagination-total">
          {showTotal(total, [startItem, endItem])}
        </div>
      )}
      
      <div className="pagination-controls">
        <button
          className="pagination-button"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
          aria-label="Previous page"
        >
          ‹
        </button>

        {renderPageNumbers().map((page, index) => (
          <button
            key={index}
            className={`pagination-button ${page === currentPage ? 'active' : ''}`}
            onClick={() => typeof page === 'number' && handlePageChange(page)}
            disabled={page === '...'}
          >
            {page}
          </button>
        ))}

        <button
          className="pagination-button"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          aria-label="Next page"
        >
          ›
        </button>
      </div>

      {showSizeChanger && (
        <div className="pagination-size-changer">
          <select
            value={pageSize}
            onChange={(e) => handlePageSizeChange(Number(e.target.value))}
            className="pagination-select"
          >
            {pageSizeOptions.map((size) => (
              <option key={size} value={size}>
                {size} / page
              </option>
            ))}
          </select>
        </div>
      )}

      {showQuickJumper && (
        <div className="pagination-jumper">
          <span>Go to</span>
          <input
            type="number"
            min={1}
            max={totalPages}
            value={jumpPage}
            onChange={(e) => setJumpPage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleJump()}
            className="pagination-input"
          />
          <button
            className="pagination-button pagination-go-button"
            onClick={handleJump}
            disabled={!jumpPage}
          >
            Go
          </button>
        </div>
      )}
    </div>
  );
});

TablePagination.displayName = 'TablePagination';
