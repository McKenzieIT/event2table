/**
 * PerformanceMonitor Component
 *
 * Development-only component that displays real-time performance metrics
 * Shows FPS, memory usage, and other performance indicators
 *
 * Usage: Add to App.jsx in development mode
 */

import React, { useState, useEffect, useRef } from 'react';
import './PerformanceMonitor.css';

interface PerformanceMetrics {
  fps: number;
  memory: number;
  loadTime: number;
  interactionTime: number;
}

interface PerformanceMonitorProps {
  enabled?: boolean;
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  onFPSUpdate?: (fps: number) => void;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  enabled = process.env.NODE_ENV === 'development',
  position = 'top-right',
  onFPSUpdate
}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 0,
    memory: 0,
    loadTime: 0,
    interactionTime: 0
  });

  const [isVisible, setIsVisible] = useState(true);
  const frameCount = useRef(0);
  const lastTime = useRef(performance.now());
  const animationFrameId = useRef<number>();

  // Measure FPS
  useEffect(() => {
    if (!enabled || !isVisible) return;

    function measureFrame() {
      frameCount.current++;
      const currentTime = performance.now();

      if (currentTime >= lastTime.current + 1000) {
        const fps = Math.round((frameCount.current * 1000) / (currentTime - lastTime.current));

        setMetrics((prev) => {
          const updated = { ...prev, fps };
          if (onFPSUpdate) {
            onFPSUpdate(fps);
          }
          return updated;
        });

        frameCount.current = 0;
        lastTime.current = currentTime;
      }

      animationFrameId.current = requestAnimationFrame(measureFrame);
    }

    animationFrameId.current = requestAnimationFrame(measureFrame);

    return () => {
      if (animationFrameId.current) {
        cancelAnimationFrame(animationFrameId.current);
      }
    };
  }, [enabled, isVisible, onFPSUpdate]);

  // Measure memory usage
  useEffect(() => {
    if (!enabled || !isVisible) return;

    const interval = setInterval(() => {
      if (performance.memory) {
        const memory = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024);
        setMetrics((prev) => ({ ...prev, memory }));
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [enabled, isVisible]);

  // Measure page load time
  useEffect(() => {
    if (!enabled) return;

    const loadTime = performance.timing
      ? performance.timing.loadEventEnd - performance.timing.navigationStart
      : 0;

    if (loadTime > 0) {
      setMetrics((prev) => ({ ...prev, loadTime }));
    }
  }, [enabled]);

  // Get FPS color
  const getFPSColor = (fps: number): string => {
    if (fps >= 55) return '#52c41a'; // Green
    if (fps >= 45) return '#faad14'; // Yellow
    return '#ff4d4f'; // Red
  };

  // Get memory color
  const getMemoryColor = (memory: number): string => {
    if (memory < 100) return '#52c41a';
    if (memory < 200) return '#faad14';
    return '#ff4d4f';
  };

  if (!enabled || !isVisible) return null;

  return (
    <div className={`performance-monitor ${position}`}>
      <div className="perf-header">
        <span>Performance Monitor</span>
        <button
          onClick={() => setIsVisible(false)}
          className="perf-close"
          aria-label="Close"
        >
          ×
        </button>
      </div>

      <div className="perf-metrics">
        <div className="perf-metric">
          <span className="perf-label">FPS</span>
          <span
            className="perf-value"
            style={{ color: getFPSColor(metrics.fps) }}
          >
            {metrics.fps}
          </span>
        </div>

        <div className="perf-metric">
          <span className="perf-label">Memory</span>
          <span
            className="perf-value"
            style={{ color: getMemoryColor(metrics.memory) }}
          >
            {metrics.memory} MB
          </span>
        </div>

        {metrics.loadTime > 0 && (
          <div className="perf-metric">
            <span className="perf-label">Load</span>
            <span className="perf-value">{metrics.loadTime} ms</span>
          </div>
        )}
      </div>

      <div className="perf-status">
        {metrics.fps >= 55 ? (
          <span className="perf-status-good">Excellent</span>
        ) : metrics.fps >= 45 ? (
          <span className="perf-status-warning">Fair</span>
        ) : (
          <span className="perf-status-bad">Poor</span>
        )}
      </div>
    </div>
  );
};

/**
 * PerformanceMonitor.css
 */
const css = `
.performance-monitor {
  position: fixed;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  color: #fff;
  padding: 12px;
  border-radius: 8px;
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 12px;
  min-width: 150px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
}

.performance-monitor.top-left {
  top: 20px;
  left: 20px;
}

.performance-monitor.top-right {
  top: 20px;
  right: 20px;
}

.performance-monitor.bottom-left {
  bottom: 20px;
  left: 20px;
}

.performance-monitor.bottom-right {
  bottom: 20px;
  right: 20px;
}

.perf-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

.perf-close {
  background: none;
  border: none;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.perf-close:hover {
  background: rgba(255, 255, 255, 0.1);
}

.perf-metrics {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.perf-metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.perf-label {
  color: rgba(255, 255, 255, 0.7);
}

.perf-value {
  font-weight: 600;
  font-size: 14px;
}

.perf-status {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
  font-weight: 600;
}

.perf-status-good {
  color: #52c41a;
}

.perf-status-warning {
  color: #faad14;
}

.perf-status-bad {
  color: #ff4d4f;
}
`;

// Export CSS for use in CSS file
export const performanceMonitorCSS = css;

export default PerformanceMonitor;
