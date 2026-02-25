// @ts-nocheck - TypeScript检查暂禁用
import React from 'react';
import { Button } from '../Button/Button';
import './EmptyState.css';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
  variant?: 'default' | 'search' | 'list' | 'error';
}

const DEFAULT_ICONS = {
  default: 'bi bi-inbox',
  search: 'bi bi-search',
  list: 'bi bi-collection',
  error: 'bi bi-exclamation-circle',
};

const DEFAULT_TITLES = {
  default: '暂无内容',
  search: '未找到结果',
  list: '暂无数据',
  error: '出错了',
};

const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className = '',
  variant = 'default'
}) => {
  const defaultIcon = !icon && (variant !== 'custom');
  const defaultTitle = !title && (variant !== 'custom');

  return (
    <div className={`empty-state-component ${className}`}>
      {icon ? (
        <div className="empty-state__icon">{icon}</div>
      ) : defaultIcon ? (
        <div className="empty-state__icon">
          <i className={DEFAULT_ICONS[variant]}></i>
        </div>
      ) : null}
      
      <h3 className="empty-state__title">
        {title || DEFAULT_TITLES[variant]}
      </h3>
      
      {description && <p className="empty-state__description">{description}</p>}
      
      {action && (
        <Button variant="primary" onClick={action.onClick}>
          {action.label}
        </Button>
      )}
    </div>
  );
};

// 预设变体组件
EmptyState.Search = function SearchEmptyState({ 
  title = '未找到搜索结果',
  description,
  action,
  className 
}: Omit<EmptyStateProps, 'variant'> & { variant?: 'search' }) {
  return (
    <EmptyState 
      variant="search"
      title={title}
      description={description}
      action={action}
      className={className}
    />
  );
};

EmptyState.List = function ListEmptyState({
  title = '暂无数据',
  description,
  action,
  className
}: Omit<EmptyStateProps, 'variant'>) {
  return (
    <EmptyState 
      variant="list"
      title={title}
      description={description}
      action={action}
      className={className}
    />
  );
};

export default EmptyState;
