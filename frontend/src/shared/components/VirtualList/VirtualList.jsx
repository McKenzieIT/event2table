import React, { useRef, useCallback, memo } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
import './VirtualList.css';

/**
 * 通用虚拟滚动列表组件
 * 
 * @param {Array} items - 数据项数组
 * @param {Function} renderItem - 渲染每一项的函数 (item, index, virtualItem) => ReactNode
 * @param {number} estimateSize - 估计每项高度（默认60px）
 * @param {number} overscan - 预渲染的额外项数（默认5）
 * @param {string} className - 容器类名
 * @param {Object} containerStyle - 容器样式
 * @param {boolean} isLoading - 是否加载中
 * @param {ReactNode} skeleton - 骨架屏组件
 */
const VirtualList = memo(({
  items = [],
  renderItem,
  estimateSize = 60,
  overscan = 5,
  className = '',
  containerStyle = {},
  isLoading = false,
  skeleton = null,
  ...props
}) => {
  const parentRef = useRef(null);

  // 创建虚拟化实例
  const rowVirtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: useCallback(() => estimateSize, [estimateSize]),
    overscan,
  });

  // 获取虚拟项
  const virtualItems = rowVirtualizer.getVirtualItems();

  // 加载状态显示骨架屏
  if (isLoading) {
    return skeleton || <DefaultSkeleton count={10} itemHeight={estimateSize} />;
  }

  // 空状态
  if (items.length === 0) {
    return (
      <div className="virtual-list-empty" role="status" aria-live="polite">
        <p>暂无数据</p>
      </div>
    );
  }

  return (
    <div
      ref={parentRef}
      className={`virtual-list-container ${className}`}
      style={{
        height: '100%',
        overflow: 'auto',
        ...containerStyle
      }}
      {...props}
    >
      <div
        style={{
          height: `${rowVirtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualItems.map(virtualItem => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualItem.size}px`,
              transform: `translateY(${virtualItem.start}px)`,
            }}
          >
            {renderItem(items[virtualItem.index], virtualItem.index, virtualItem)}
          </div>
        ))}
      </div>
    </div>
  );
});

VirtualList.displayName = 'VirtualList';

/**
 * 默认骨架屏组件
 */
const DefaultSkeleton = memo(({ count = 10, itemHeight = 60 }) => (
  <div className="virtual-list-skeleton">
    {Array.from({ length: count }).map((_, i) => (
      <div
        key={i}
        className="skeleton-row"
        style={{ height: `${itemHeight}px` }}
      >
        <div className="skeleton-cell skeleton-animate"></div>
      </div>
    ))}
  </div>
));

DefaultSkeleton.displayName = 'DefaultSkeleton';

export { VirtualList, DefaultSkeleton };
export default VirtualList;
