import React from 'react';
import { Spinner } from '../Spinner/Spinner';
import './PageLoader.css';

interface PageLoaderProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  fullPage?: boolean;
  className?: string;
}

export const PageLoader: React.FC<PageLoaderProps> = ({ 
  message = '加载中...', 
  size = 'lg',
  fullPage = true,
  className = '' 
}) => {
  const content = (
    <div className={`page-loader ${fullPage ? 'page-loader--full' : ''} ${className}`}>
      <Spinner size={size} />
      {message && <p className="page-loader__message">{message}</p>}
    </div>
  );

  if (fullPage) {
    return (
      <div className="page-loader__overlay">
        {content}
      </div>
    );
  }

  return content;
};

export default PageLoader;
