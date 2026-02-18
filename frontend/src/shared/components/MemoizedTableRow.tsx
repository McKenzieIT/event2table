import React from 'react';

interface TableRowProps<T> {
  item: T;
  onClick?: (item: T) => void;
  compareKey?: keyof T;
  children: (item: T) => React.ReactNode;
}

export function MemoizedTableRow<T>({
  item,
  onClick,
  compareKey = 'id',
  children
}: TableRowProps<T>) {
  return (
    <tr
      className="parameter-row"
      style={{ cursor: 'pointer' }}
      onClick={() => onClick?.(item)}
      tabIndex={0}
      role="button"
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.(item);
        }
      }}
    >
      {children(item)}
    </tr>
  );
}

export const MemoizedTableRowMemo = React.memo(
  MemoizedTableRow,
  (prevProps, nextProps) => {
    const prevId = prevProps.item[prevProps.compareKey];
    const nextId = nextProps.item[nextProps.compareKey];
    return prevId === nextId;
  }
);
