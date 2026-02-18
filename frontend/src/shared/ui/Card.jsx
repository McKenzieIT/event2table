import React from 'react';
import './Card.css';

/**
 * Card 组件
 * 统一的卡片容器组件
 *
 * Props:
 * - as: React.ElementType - 渲染的HTML元素类型（默认'div'）
 * - variant: 'default' | 'elevated' | 'outlined' | 'glass' | 'glass-dark'
 * - padding: 'none' | 'sm' | 'md' | 'lg' | 'reset' - 'reset'表示不使用默认padding，由子元素控制
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
  // padding='reset' 时不添加padding类，由子元素自行控制padding
  const paddingClass = padding === 'reset' ? '' : `card-padding-${padding}`;
  
  return (
    <Component
      ref={ref}
      className={`card card-${variant} ${paddingClass} ${hover ? 'card-hover' : ''} ${className}`}
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
