/**
 * Skeleton Component - Loading Placeholder
 * 
 * Provides various skeleton loading states for different content types.
 * Includes Table, Form, Card, and inline variants.
 * 
 * @example
 * // Table skeleton with columns
 * <Skeleton type="table" columns={5} rows={10} />
 * 
 * @example
 * // Form skeleton
 * <Skeleton type="form" fields={4} />
 * 
 * @example
 * // Card skeleton
 * <Skeleton type="card" count={6} />
 */

import React, { memo } from 'react';
import './Skeleton.css';

const Skeleton = memo(({
  type = 'inline',
  rows = 5,
  columns,
  fields = 4,
  count = 3,
  height,
  className = '',
  ...props
}) => {
  const skeletonClass = [
    'skeleton-wrapper',
    `skeleton-${type}`,
    className
  ].filter(Boolean).join(' ');

  switch (type) {
    case 'table':
      return (
        <div className={skeletonClass} style={height ? { height } : {}} {...props}>
          {/* Table Header */}
          <div className="skeleton-table-header">
            {columns && Array.from({ length: columns }).map((_, i) => (
              <div key={`header-${i}`} className="skeleton-cell skeleton-animate" />
            ))}
          </div>
          {/* Table Rows */}
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <div key={`row-${rowIndex}`} className="skeleton-table-row">
              {columns && Array.from({ length: columns }).map((_, colIndex) => (
                <div key={`cell-${rowIndex}-${colIndex}`} className="skeleton-cell skeleton-animate" />
              ))}
            </div>
          ))}
        </div>
      );

    case 'form':
      return (
        <div className={skeletonClass} {...props}>
          {Array.from({ length: fields }).map((_, i) => (
            <div key={`field-${i}`} className="skeleton-form-field">
              <div className="skeleton-label skeleton-animate" />
              <div className="skeleton-input skeleton-animate" />
            </div>
          ))}
          <div className="skeleton-form-actions">
            <div className="skeleton-button skeleton-animate" />
            <div className="skeleton-button skeleton-animate" />
          </div>
        </div>
      );

    case 'card':
      return (
        <div className={skeletonClass} {...props}>
          {Array.from({ length: count }).map((_, i) => (
            <div key={`card-${i}`} className="skeleton-card-item">
              <div className="skeleton-card-icon skeleton-animate" />
              <div className="skeleton-card-content">
                <div className="skeleton-title skeleton-animate" />
                <div className="skeleton-text skeleton-animate" />
                <div className="skeleton-text short skeleton-animate" />
              </div>
              <div className="skeleton-card-actions">
                <div className="skeleton-button skeleton-animate" />
                <div className="skeleton-button skeleton-animate" />
              </div>
            </div>
          ))}
        </div>
      );

    case 'inline':
    default:
      return (
        <div className={skeletonClass} style={height ? { height } : {}} {...props}>
          {Array.from({ length: rows }).map((_, i) => (
            <div key={`inline-${i}`} className="skeleton-line skeleton-animate" />
          ))}
        </div>
      );
  }
});

Skeleton.displayName = 'Skeleton';

// Export individual skeleton types for convenience
export const SkeletonTable = memo((props) => <Skeleton type="table" {...props} />);
export const SkeletonForm = memo((props) => <Skeleton type="form" {...props} />);
export const SkeletonCard = memo((props) => <Skeleton type="card" {...props} />);
export const SkeletonInline = memo((props) => <Skeleton type="inline" {...props} />);

SkeletonTable.displayName = 'SkeletonTable';
SkeletonForm.displayName = 'SkeletonForm';
SkeletonCard.displayName = 'SkeletonCard';
SkeletonInline.displayName = 'SkeletonInline';

export default Skeleton;
