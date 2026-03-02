// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * canvasPerformanceMonitor.test.ts
 * Unit tests for Canvas Performance Monitor
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { CanvasPerformanceMonitor, PerformanceMetrics } from './canvasPerformanceMonitor';

describe('CanvasPerformanceMonitor', () => {
  let monitor: CanvasPerformanceMonitor;

  beforeEach(() => {
    monitor = new CanvasPerformanceMonitor();
  });

  afterEach(() => {
    monitor.stopMonitoring();
  });

  describe('initialization', () => {
    it('should initialize with zero metrics', () => {
      const metrics = monitor.getMetrics();
      expect(metrics.fps).toBe(0);
      expect(metrics.memory).toBe(0);
      expect(metrics.loadTime).toBe(0);
      expect(metrics.interactionTime).toBe(0);
    });

    it('should start with monitoring disabled', () => {
      const metrics = monitor.getMetrics();
      expect(metrics.fps).toBe(0);
    });
  });

  describe('startMonitoring', () => {
    it('should start monitoring', () => {
      monitor.startMonitoring();
      const metrics = monitor.getMetrics();
      // Metrics may still be 0 immediately after start
      expect(typeof metrics.fps).toBe('number');
    });

    it('should not start monitoring twice', () => {
      monitor.startMonitoring();
      const metrics1 = monitor.getMetrics();
      monitor.startMonitoring();
      const metrics2 = monitor.getMetrics();
      // Should not crash or reset
      expect(typeof metrics2.fps).toBe('number');
    });
  });

  describe('stopMonitoring', () => {
    it('should stop monitoring and return metrics', () => {
      monitor.startMonitoring();
      const metrics = monitor.stopMonitoring();

      expect(metrics).toHaveProperty('fps');
      expect(metrics).toHaveProperty('memory');
      expect(metrics).toHaveProperty('loadTime');
      expect(metrics).toHaveProperty('interactionTime');
      expect(typeof metrics.fps).toBe('number');
      expect(typeof metrics.memory).toBe('number');
    });

    it('should return current metrics when stopped', () => {
      monitor.measureLoadTime(100);
      const metrics = monitor.stopMonitoring();

      expect(metrics.loadTime).toBeGreaterThanOrEqual(0);
    });
  });

  describe('measureLoadTime', () => {
    it('should measure load time from start time', () => {
      const startTime = performance.now() - 1000; // 1 second ago
      const loadTime = monitor.measureLoadTime(startTime);

      expect(loadTime).toBeGreaterThan(0);
      expect(loadTime).toBeLessThan(2000); // Should be close to 1000ms
    });

    it('should update metrics with load time', () => {
      monitor.measureLoadTime(performance.now() - 500);
      const metrics = monitor.getMetrics();

      expect(metrics.loadTime).toBeGreaterThan(0);
    });
  });

  describe('measureInteractionTime', () => {
    it('should measure interaction time for synchronous callback', () => {
      const callback = () => 'result';
      const { result, time } = monitor.measureInteractionTime(callback);

      expect(result).toBe('result');
      expect(time).toBeGreaterThanOrEqual(0);
      expect(typeof time).toBe('number');
    });

    it('should measure interaction time for calculation', () => {
      const callback = () => {
        let sum = 0;
        for (let i = 0; i < 1000; i++) {
          sum += i;
        }
        return sum;
      };

      const { result, time } = monitor.measureInteractionTime(callback);

      expect(result).toBe(499500);
      expect(time).toBeGreaterThanOrEqual(0);
    });

    it('should update metrics with interaction time', () => {
      monitor.measureInteractionTime(() => 'test');
      const metrics = monitor.getMetrics();

      expect(metrics.interactionTime).toBeGreaterThanOrEqual(0);
    });

    it('should handle callback that throws error', () => {
      const callback = () => {
        throw new Error('Test error');
      };

      expect(() => {
        monitor.measureInteractionTime(callback);
      }).toThrow('Test error');
    });

    it('should return different times for different operations', () => {
      const fastOp = () => 1 + 1;
      const slowOp = () => {
        let result = 0;
        for (let i = 0; i < 10000; i++) {
          result += i;
        }
        return result;
      };

      const { time: fastTime } = monitor.measureInteractionTime(fastOp);
      const { time: slowTime } = monitor.measureInteractionTime(slowOp);

      expect(slowTime).toBeGreaterThanOrEqual(fastTime);
    });
  });

  describe('getMetrics', () => {
    it('should return copy of metrics', () => {
      const metrics1 = monitor.getMetrics();
      metrics1.fps = 999;

      const metrics2 = monitor.getMetrics();
      expect(metrics2.fps).not.toBe(999);
    });

    it('should return all required properties', () => {
      const metrics = monitor.getMetrics();

      expect(metrics).toHaveProperty('fps');
      expect(metrics).toHaveProperty('memory');
      expect(metrics).toHaveProperty('loadTime');
      expect(metrics).toHaveProperty('interactionTime');
    });

    it('should return number values for all metrics', () => {
      const metrics = monitor.getMetrics();

      expect(typeof metrics.fps).toBe('number');
      expect(typeof metrics.memory).toBe('number');
      expect(typeof metrics.loadTime).toBe('number');
      expect(typeof metrics.interactionTime).toBe('number');
    });
  });

  describe('resetMetrics', () => {
    it('should reset all metrics to zero', () => {
      monitor.measureLoadTime(performance.now() - 1000);
      monitor.measureInteractionTime(() => 'test');

      monitor.resetMetrics();
      const metrics = monitor.getMetrics();

      expect(metrics.fps).toBe(0);
      expect(metrics.memory).toBe(0);
      expect(metrics.loadTime).toBe(0);
      expect(metrics.interactionTime).toBe(0);
    });

    it('should not affect monitoring state', () => {
      monitor.startMonitoring();
      monitor.resetMetrics();
      const metrics = monitor.getMetrics();

      expect(typeof metrics.fps).toBe('number');
    });
  });

  describe('FPS measurement', () => {
    it('should measure FPS after starting monitoring', async () => {
      monitor.startMonitoring();

      // Wait for at least one FPS measurement
      await new Promise(resolve => setTimeout(resolve, 1100));

      const metrics = monitor.getMetrics();
      // FPS should be measured (may be 0 if no frames rendered)
      expect(typeof metrics.fps).toBe('number');
    }, 2000);

    it('should calculate reasonable FPS values', async () => {
      monitor.startMonitoring();

      await new Promise(resolve => setTimeout(resolve, 1100));

      const metrics = monitor.getMetrics();
      // FPS should be a reasonable value (0-120 for typical screens)
      expect(metrics.fps).toBeGreaterThanOrEqual(0);
      expect(metrics.fps).toBeLessThanOrEqual(120);
    }, 2000);
  });

  describe('memory measurement', () => {
    it('should measure memory if performance.memory is available', async () => {
      monitor.startMonitoring();

      await new Promise(resolve => setTimeout(resolve, 100));

      const metrics = monitor.getMetrics();

      if (performance.memory) {
        expect(metrics.memory).toBeGreaterThanOrEqual(0);
      } else {
        expect(metrics.memory).toBe(0);
      }
    }, 2000);
  });

  describe('real-world scenarios', () => {
    it('should monitor complete canvas session', () => {
      // Simulate canvas load
      const loadStart = performance.now();
      monitor.measureLoadTime(loadStart);

      // Simulate user interactions
      monitor.measureInteractionTime(() => {
        // Simulate node creation
        return { id: 1, type: 'node' };
      });

      monitor.measureInteractionTime(() => {
        // Simulate connection creation
        return { id: 2, type: 'connection' };
      });

      const metrics = monitor.getMetrics();

      expect(metrics.loadTime).toBeGreaterThan(0);
      expect(metrics.interactionTime).toBeGreaterThan(0);
      expect(metrics.interactionTime).toBeLessThan(1000); // Should be fast
    });

    it('should handle rapid interactions', () => {
      const times: number[] = [];

      for (let i = 0; i < 10; i++) {
        const { time } = monitor.measureInteractionTime(() => i);
        times.push(time);
      }

      // All interactions should be measured
      times.forEach(time => {
        expect(time).toBeGreaterThanOrEqual(0);
        expect(time).toBeLessThan(1000);
      });
    });

    it('should track performance over time', () => {
      const metricsOverTime: PerformanceMetrics[] = [];

      monitor.startMonitoring();

      for (let i = 0; i < 5; i++) {
        monitor.measureInteractionTime(() => {
          return Math.random();
        });
        metricsOverTime.push(monitor.getMetrics());
      }

      // Should have tracked metrics over time
      expect(metricsOverTime.length).toBe(5);
      metricsOverTime.forEach(metrics => {
        expect(typeof metrics.fps).toBe('number');
        expect(typeof metrics.interactionTime).toBe('number');
      });

      monitor.stopMonitoring();
    });
  });

  describe('edge cases', () => {
    it('should handle stop when not monitoring', () => {
      const metrics = monitor.stopMonitoring();
      expect(metrics).toBeDefined();
      expect(typeof metrics.fps).toBe('number');
    });

    it('should handle multiple start/stop cycles', () => {
      for (let i = 0; i < 5; i++) {
        monitor.startMonitoring();
        monitor.measureInteractionTime(() => i);
        monitor.stopMonitoring();
      }

      const metrics = monitor.getMetrics();
      expect(typeof metrics.interactionTime).toBe('number');
    });

    it('should handle reset without monitoring', () => {
      monitor.resetMetrics();
      const metrics = monitor.getMetrics();

      expect(metrics.fps).toBe(0);
      expect(metrics.memory).toBe(0);
      expect(metrics.loadTime).toBe(0);
      expect(metrics.interactionTime).toBe(0);
    });

    it('should handle very fast interactions', () => {
      const { time } = monitor.measureInteractionTime(() => 1);
      expect(time).toBeGreaterThanOrEqual(0);
      expect(time).toBeLessThan(100);
    });

    it('should measure load time with negative delta (future time)', () => {
      const futureTime = performance.now() + 1000;
      const loadTime = monitor.measureLoadTime(futureTime);

      // Should return a time (may be negative due to clock adjustments)
      expect(typeof loadTime).toBe('number');
    });
  });

  describe('metric types', () => {
    it('should maintain correct metric types', () => {
      monitor.measureLoadTime(performance.now() - 100);
      monitor.measureInteractionTime(() => 'test');

      const metrics = monitor.getMetrics();

      expect(metrics.fps).toBeGreaterThanOrEqual(0);
      expect(metrics.memory).toBeGreaterThanOrEqual(0);
      expect(metrics.loadTime).toBeGreaterThanOrEqual(0);
      expect(metrics.interactionTime).toBeGreaterThanOrEqual(0);
    });
  });
});
