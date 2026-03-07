// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * Breadcrumb Component
 * 面包屑导航组件
 * 
 * 放置在顶部Header区域
 */

import React from 'react';
import { Link } from 'react-router-dom';
import './Breadcrumb.css';

export interface BreadcrumbItem {
  label: string;
  to?: string;
  active?: boolean;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  separator?: string;
}

export function Breadcrumb({ items, separator = '>' }) {
  return (
    <nav className="breadcrumb" aria-label="面包屑导航">
      <ol className="breadcrumb-list">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;

          return (
            <li key={index} className={`breadcrumb-item ${isLast ? 'active' : ''}`}>
              {item.to && !isLast ? (
                <Link to={item.to} className="breadcrumb-link">
                  {item.label}
                </Link>
              ) : (
                <span className="breadcrumb-current">{item.label}</span>
              )}
              {!isLast && (
                <span className="breadcrumb-separator">{separator}</span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

// Memoize to prevent unnecessary re-renders when parent updates
const MemoizedBreadcrumb = React.memo(Breadcrumb);
MemoizedBreadcrumb.displayName = 'MemoizedBreadcrumb';

export default MemoizedBreadcrumb;
