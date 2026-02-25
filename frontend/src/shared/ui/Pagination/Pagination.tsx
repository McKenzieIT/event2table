import React, { useMemo } from 'react';
import './Pagination.css';

export interface PaginationProps {
  currentPage: number;
  totalPages: number;
  pageSize: number;
  totalItems: number;
  onPageChange: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  pageSizeOptions?: number[];
  showPageSize?: boolean;
  showPageInfo?: boolean;
  className?: string;
}

const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  pageSize,
  totalItems,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [10, 25, 50, 100],
  showPageSize = true,
  showPageInfo = true,
  className = '',
}) => {
  const startItem = useMemo(() => {
    return (currentPage - 1) * pageSize + 1;
  }, [currentPage, pageSize]);

  const endItem = useMemo(() => {
    return Math.min(currentPage * pageSize, totalItems);
  }, [currentPage, pageSize, totalItems]);

  const visiblePages = useMemo(() => {
    const pages: (number | '...')[] = [];
    const maxVisible = 5;
    
    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    
    return pages;
  }, [currentPage, totalPages]);

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
      onPageChange(page);
    }
  };

  if (totalItems === 0) {
    return null;
  }

  return (
    <div className={`pagination ${className}`.trim()}>
      {showPageInfo && (
        <div className="pagination__info">
          显示第 {startItem} 到 {endItem} 条，共 {totalItems} 条
        </div>
      )}

      <div className="pagination__controls">
        <button
          className="pagination__btn pagination__btn--nav"
          onClick={() => goToPage(1)}
          disabled={currentPage === 1}
          title="首页"
        >
          <i className="bi bi-chevron-double-left"></i>
        </button>

        <button
          className="pagination__btn pagination__btn--nav"
          onClick={() => goToPage(currentPage - 1)}
          disabled={currentPage === 1}
          title="上一页"
        >
          <i className="bi bi-chevron-left"></i>
        </button>

        <div className="pagination__pages">
          {visiblePages.map((page, index) => (
            page === '...' ? (
              <span key={`ellipsis-${index}`} className="pagination__ellipsis">...</span>
            ) : (
              <button
                key={page}
                className={`pagination__btn pagination__btn--num ${
                  page === currentPage ? 'pagination__btn--active' : ''
                }`}
                onClick={() => goToPage(page)}
              >
                {page}
              </button>
            )
          ))}
        </div>

        <button
          className="pagination__btn pagination__btn--nav"
          onClick={() => goToPage(currentPage + 1)}
          disabled={currentPage === totalPages}
          title="下一页"
        >
          <i className="bi bi-chevron-right"></i>
        </button>

        <button
          className="pagination__btn pagination__btn--nav"
          onClick={() => goToPage(totalPages)}
          disabled={currentPage === totalPages}
          title="末页"
        >
          <i className="bi bi-chevron-double-right"></i>
        </button>
      </div>

      {showPageSize && onPageSizeChange && (
        <div className="pagination__size">
          <select
            className="pagination__size-select"
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
          >
            {pageSizeOptions.map(size => (
              <option key={size} value={size}>
                每页 {size} 条
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
};

export default React.memo(Pagination);
