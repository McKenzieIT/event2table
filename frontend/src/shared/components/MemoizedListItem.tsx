import React from 'react';

interface ListItemProps<T> {
  item: T;
  onClick?: (item: T) => void;
  onDelete?: (id: string | number) => void;
  renderContent: (item: T) => React.ReactNode;
  compareKey?: keyof T;
}

export function MemoizedListItem<T extends { id?: string | number }>({
  item,
  onClick,
  onDelete,
  renderContent,
  compareKey = 'id'
}: ListItemProps<T>) {
  return (
    <div 
      className="list-item" 
      onClick={() => onClick?.(item)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick?.(item)}
    >
      {renderContent(item)}
      {onDelete && item.id && (
        <button 
          onClick={(e) => {
            e.stopPropagation();
            onDelete(item.id!);
          }}
          className="btn-delete"
          aria-label="删除"
        >
          删除
        </button>
      )}
    </div>
  );
}

export const MemoizedListItemMemo = React.memo(
  MemoizedListItem,
  (prevProps, nextProps) => {
    const prevId = prevProps.item[prevProps.compareKey];
    const nextId = nextProps.item[nextProps.compareKey];
    return prevId === nextId;
  }
);
