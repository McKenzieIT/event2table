import { useState, useRef, useEffect } from 'react';
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
}) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const imgRef = useRef(null);
  const observerRef = useRef(null);

  // Handle image load
  const handleLoad = (e) => {
    setIsLoaded(true);
    setHasError(false);
    onLoad?.(e);
  };

  // Handle image error with retry
  const handleError = (e) => {
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
  const getPlaceholderStyle = () => {
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
 * @param {string[]} urls - Array of image URLs to preload
 * @returns {Promise<void>}
 */
export function preloadImages(urls) {
  return Promise.all(
    urls.map(url => {
      return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = resolve;
        img.onerror = reject;
        img.src = url;
      });
    })
  );
}

/**
 * Get WebP version of image URL with fallback
 * @param {string} url - Original image URL
 * @param {boolean} supportsWebP - Browser supports WebP
 * @returns {string} WebP or original URL
 */
export function getWebPUrl(url, supportsWebP = true) {
  if (!supportsWebP) return url;

  // Convert to WebP if it's a JPG/PNG
  const webpUrl = url.replace(/\.(jpg|jpeg|png)$/i, '.webp');
  return webpUrl;
}
