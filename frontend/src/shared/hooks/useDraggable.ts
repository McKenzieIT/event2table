import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Draggable Configuration
 */
export interface DraggableConfig {
  /** Selector for the drag handle element */
  handle?: string;
  /** Boundary constraint: 'parent', 'window', or custom HTMLElement */
  bounds?: 'parent' | 'window' | HTMLElement;
  /** Grid snapping: [x, y] step values */
  grid?: [number, number];
  /** Whether dragging is enabled */
  enabled?: boolean;
  /** Callback when drag starts */
  onDragStart?: () => void;
  /** Callback when dragging */
  onDrag?: (position: Position) => void;
  /** Callback when drag ends */
  onDragEnd?: (position: Position) => void;
}

/**
 * Position type
 */
export interface Position {
  x: number;
  y: number;
}

/**
 * useDraggable Hook
 * 
 * Provides drag functionality for elements with boundary constraints,
 * grid snapping, and custom drag handles.
 * 
 * @param config - Draggable configuration
 * @returns Draggable state and handlers
 * 
 * @example
 * ```tsx
 * const { position, handlers, isDragging, reset } = useDraggable({
 *   enabled: true,
 *   bounds: 'window',
 *   grid: [10, 10],
 * });
 * 
 * <div
 *   style={{ transform: `translate(${position.x}px, ${position.y}px)` }}
 *   {...handlers}
 * >
 *   Drag me
 * </div>
 * ```
 */
export function useDraggable(config: DraggableConfig = {}) {
  const {
    enabled = true,
    bounds,
    grid,
    onDragStart,
    onDrag,
    onDragEnd,
  } = config;

  const [position, setPosition] = useState<Position>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef<Position>({ x: 0, y: 0 });
  const elementRef = useRef<HTMLElement | null>(null);

  // Calculate boundary constraints
  const getBounds = useCallback((): { left: number; top: number; right: number; bottom: number } => {
    if (!elementRef.current) {
      return { left: 0, top: 0, right: window.innerWidth, bottom: window.innerHeight };
    }

    const elementRect = elementRef.current.getBoundingClientRect();

    if (bounds === 'parent' && elementRef.current.parentElement) {
      const parentRect = elementRef.current.parentElement.getBoundingClientRect();
      return {
        left: parentRect.left - elementRect.left + position.x,
        top: parentRect.top - elementRect.top + position.y,
        right: parentRect.right - elementRect.right + position.x,
        bottom: parentRect.bottom - elementRect.bottom + position.y,
      };
    }

    if (bounds instanceof HTMLElement) {
      const boundsRect = bounds.getBoundingClientRect();
      return {
        left: boundsRect.left - elementRect.left + position.x,
        top: boundsRect.top - elementRect.top + position.y,
        right: boundsRect.right - elementRect.right + position.x,
        bottom: boundsRect.bottom - elementRect.bottom + position.y,
      };
    }

    // Default to window bounds
    return {
      left: -elementRect.left + position.x,
      top: -elementRect.top + position.y,
      right: window.innerWidth - elementRect.right + position.x,
      bottom: window.innerHeight - elementRect.bottom + position.y,
    };
  }, [bounds, position]);

  // Apply grid snapping
  const snapToGrid = useCallback((value: number, gridStep: number): number => {
    if (!gridStep || gridStep <= 0) return value;
    return Math.round(value / gridStep) * gridStep;
  }, []);

  // Handle mouse down
  const handleMouseDown = useCallback((event: React.MouseEvent) => {
    if (!enabled) return;

    // 只在拖拽句柄上按下时才开始拖拽
    // 如果点击的是按钮、输入框等交互元素，不启动拖拽
    const target = event.target as HTMLElement;
    const isInteractiveElement = 
      target.tagName === 'BUTTON' ||
      target.tagName === 'INPUT' ||
      target.tagName === 'SELECT' ||
      target.tagName === 'TEXTAREA' ||
      target.tagName === 'A' ||
      target.closest('button') ||
      target.closest('a');

    if (isInteractiveElement) return;

    event.preventDefault();
    setIsDragging(true);
    dragStartRef.current = {
      x: event.clientX - position.x,
      y: event.clientY - position.y,
    };
    onDragStart?.();
  }, [enabled, position, onDragStart]);

  // Handle touch start
  const handleTouchStart = useCallback((event: React.TouchEvent) => {
    if (!enabled) return;

    const touch = event.touches[0];
    if (!touch) return;

    event.preventDefault();
    setIsDragging(true);
    dragStartRef.current = {
      x: touch.clientX - position.x,
      y: touch.clientY - position.y,
    };
    onDragStart?.();
  }, [enabled, position, onDragStart]);

  // Handle mouse move
  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (event: MouseEvent) => {
      const boundsRect = getBounds();
      let newX = event.clientX - dragStartRef.current.x;
      let newY = event.clientY - dragStartRef.current.y;

      // Apply grid snapping
      if (grid) {
        newX = snapToGrid(newX, grid[0]);
        newY = snapToGrid(newY, grid[1]);
      }

      // Apply boundary constraints
      newX = Math.max(boundsRect.left, Math.min(boundsRect.right, newX));
      newY = Math.max(boundsRect.top, Math.min(boundsRect.bottom, newY));

      const newPosition = { x: newX, y: newY };
      setPosition(newPosition);
      onDrag?.(newPosition);
    };

    const handleTouchMove = (event: TouchEvent) => {
      const touch = event.touches[0];
      if (!touch) return;

      const boundsRect = getBounds();
      let newX = touch.clientX - dragStartRef.current.x;
      let newY = touch.clientY - dragStartRef.current.y;

      // Apply grid snapping
      if (grid) {
        newX = snapToGrid(newX, grid[0]);
        newY = snapToGrid(newY, grid[1]);
      }

      // Apply boundary constraints
      newX = Math.max(boundsRect.left, Math.min(boundsRect.right, newX));
      newY = Math.max(boundsRect.top, Math.min(boundsRect.bottom, newY));

      const newPosition = { x: newX, y: newY };
      setPosition(newPosition);
      onDrag?.(newPosition);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      onDragEnd?.(position);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    window.addEventListener('touchmove', handleTouchMove);
    window.addEventListener('touchend', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleMouseUp);
    };
  }, [isDragging, grid, getBounds, snapToGrid, position, onDrag, onDragEnd]);

  // Reset position
  const reset = useCallback(() => {
    setPosition({ x: 0, y: 0 });
  }, []);

  // Set position manually
  const setPositionManually = useCallback((newPosition: Position) => {
    setPosition(newPosition);
  }, []);

  // Event handlers to spread on the element
  const handlers = {
    onMouseDown: handleMouseDown,
    onTouchStart: handleTouchStart,
    ref: elementRef,
    style: {
      cursor: enabled ? (isDragging ? 'grabbing' : 'grab') : 'default',
      userSelect: 'none' as const,
    },
  };

  return {
    position,
    isDragging,
    handlers,
    reset,
    setPosition: setPositionManually,
    elementRef,
  };
}

export default useDraggable;
