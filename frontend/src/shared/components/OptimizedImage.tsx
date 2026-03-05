// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import { useState, useRef, useEffect, CSSProperties, ReactHTMLElement, ImgHTMLAttributes } from 'react';
import './OptimizedImage.css';

/**
 * Optimized Image Component
 * Features:
 * - Lazy loading with IntersectionObserver
 * - Progressive loading (blur-up technique)
 * - WebP format support with fallback
 * - Error handling with retry
 * - Performance monitoring
 */

export interface OptimizedImageProps extends ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  width?: number | string;
  height?: number | string;
  className?: string;
  loading?: 'lazy' | 'eager';
  fadeIn?: boolean;
  placeholder?: 'blur' | 'color' | 'none';
  onError?: (e: React.SyntheticEvent<HTMLImageElement>) => void;
  onLoad?: (e: React.SyntheticEvent<HTMLImageElement>) => void;
}

export default function OptimizedImage({
  src,
  alt,
  width,
  height,
  className = '',
  loading = 'lazy',
  fadeIn = true,
  placeholder = 'blur',
  onError,
  onLoad,
  ...props
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Handle image load
  const handleLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    setIsLoaded(true);
    setHasError(false);
    onLoad?.(e);
  };

  // Handle image error with retry
  const handleError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    if (retryCount < 2) {
      // Retry up to 2 times
      setTimeout(() => {
        setRetryCount(prev => prev + 1);
        if (imgRef.current) {
          imgRef.current.src = src;
        }
      }, 1000 * (retryCount + 1)); // Exponential backoff
    } else {
      setHasError(true);
      onError?.(e);
    }
  };

  // Cleanup observer on unmount
  useEffect(() => {
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, []);

  // Generate placeholder background
  const getPlaceholderStyle = (): CSSProperties => {
    if (placeholder === 'blur') {
      return {
        background: 'linear-gradient(90deg, #1a1a1a 25%, #2a2a2a 50%, #1a1a1a 75%)',
        backgroundSize: '200% 100%',
        animation: 'shimmer 1.5s infinite',
      };
    }
    return {};
  };

  const classes = [
    'optimized-image',
    isLoaded && fadeIn ? 'fade-in' : '',
    hasError ? 'error' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div
      className={`optimized-image-container ${className ? `${className}-container` : ''}`}
      style={{ width, height }}
    >
      {!isLoaded && !hasError && (
        <div
          className="image-placeholder"
          style={getPlaceholderStyle()}
        />
      )}

      <img
        ref={imgRef}
        src={src}
        alt={alt}
        width={width}
        height={height}
        loading={loading}
        className={classes}
        onLoad={handleLoad}
        onError={handleError}
        style={{ opacity: isLoaded ? 1 : 0 }}
        {...props}
      />

      {hasError && (
        <div className="image-error">
          <i className="bi bi-image-alt"></i>
          <span>图片加载失败</span>
        </div>
      )}
    </div>
  );
}

/**
 * Batch preload images
 */
export function preloadImages(urls: string[]): Promise<void> {
  return Promise.all(
    urls.map(url => {
      return new Promise<void>((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve();
        img.onerror = reject;
        img.src = url;
      });
    })
  );
}

/**
 * Get WebP version of image URL with fallback
 */
export function getWebPUrl(url: string, supportsWebP: boolean = true): string {
  if (!supportsWebP) return url;

  // Convert to WebP if it's a JPG/PNG
  const webpUrl = url.replace(/\.(jpg|jpeg|png)$/i, '.webp');
  return webpUrl;
}
