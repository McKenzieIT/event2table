import React from 'react';
import { EmptyState } from '@shared/ui';

/**
 * Props for DropZone component
 */
export interface DropZoneProps {
  /** Active state */
  isActive?: boolean;
  /** Drop callback */
  onDrop: (parameter: any) => void;
  /** Native drop callback */
  onNativeDrop: (e: React.DragEvent) => void;
  /** Native drag over callback */
  onNativeDragOver: (e: React.DragEvent) => void;
  /** Native drag leave callback */
  onNativeDragLeave: (e: React.DragEvent) => void;
  /** Children */
  children?: React.ReactNode;
}

/**
 * DropZone Component
 */
export const DropZone: React.FC<DropZoneProps> = ({
  isActive = false,
  onDrop,
  onNativeDrop,
  onNativeDragOver,
  onNativeDragLeave,
  children,
}) => {
  return (
    <div
      className={`drop-zone ${isActive ? 'active' : ''}`}
      onDrop={onNativeDrop}
      onDragOver={onNativeDragOver}
      onDragLeave={onNativeDragLeave}
    >
      {children}
    </div>
  );
};

DropZone.displayName = 'DropZone';
