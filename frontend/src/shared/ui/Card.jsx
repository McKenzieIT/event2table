import React from 'react';
import './Card.css';

/**
 * Card 组件
 * 统一的卡片容器组件
 *
 * Props:
 * - as: React.ElementType - 渲染的HTML元素类型（默认'div'）
 * - variant: 'default' | 'elevated' | 'outlined' | 'glass' | 'glass-dark'
 * - padding: 'none' | 'sm' | 'md' | 'lg'
 * - hover: boolean - 是否启用hover效果
 * - className: string
 * - children: React.ReactNode
 * - ...props: 其他属性传递给渲染元素
 */
export const Card = React.forwardRef(({
  as: Component = 'div',
  variant = 'default',
  padding = 'md',
  hover = false,
  className = '',
  children,
  ...props
}, ref) => {
  return (
    <Component
      ref={ref}
      className={`card card-${variant} card-padding-${padding} ${hover ? 'card-hover' : ''} ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
});

Card.displayName = 'Card';

/**
 * CardHeader 卡片头部组件
 */
export const CardHeader = React.forwardRef(({
  className = '',
  children,
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={`card-header ${className}`}
      {...props}
    >
      {children}
    </div>
  );
});

CardHeader.displayName = 'CardHeader';

/**
 * CardBody 卡片内容组件
 */
export const CardBody = React.forwardRef(({
  className = '',
  children,
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={`card-body ${className}`}
      {...props}
    >
      {children}
    </div>
  );
});

CardBody.displayName = 'CardBody';

/**
 * CardFooter 卡片底部组件
 */
export const CardFooter = React.forwardRef(({
  className = '',
  children,
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={`card-footer ${className}`}
      {...props}
    >
      {children}
    </div>
  );
});

CardFooter.displayName = 'CardFooter';
