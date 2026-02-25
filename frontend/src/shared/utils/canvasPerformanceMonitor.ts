export interface PerformanceMetrics {
  fps: number;
  memory: number;
  loadTime: number;
  interactionTime: number;
}

export class CanvasPerformanceMonitor {
  private metrics: PerformanceMetrics;
  private isMonitoring: boolean;
  private frameCount: number;
  private lastTime: number;

  constructor() {
    this.metrics = {
      fps: 0,
      memory: 0,
      loadTime: 0,
      interactionTime: 0
    };
    this.isMonitoring = false;
    this.frameCount = 0;
    this.lastTime = performance.now();
  }

  startMonitoring(): void {
    if (this.isMonitoring) return;
    this.isMonitoring = true;
    this.frameCount = 0;
    this.lastTime = performance.now();
    this.measureFPS();
    this.measureMemory();
  }

  private measureFPS(): void {
    if (!this.isMonitoring) return;

    this.frameCount++;
    const currentTime = performance.now();

    if (currentTime >= this.lastTime + 1000) {
      this.metrics.fps = Math.round((this.frameCount * 1000) / (currentTime - this.lastTime));
      this.frameCount = 0;
      this.lastTime = currentTime;
    }

    requestAnimationFrame(() => this.measureFPS());
  }

  private measureMemory(): void {
    if (!this.isMonitoring) return;

    if (performance.memory) {
      this.metrics.memory = Math.round((performance.memory as PerformanceMemory).usedJSHeapSize / 1024 / 1024);
    }

    setTimeout(() => this.measureMemory(), 5000);
  }

  measureLoadTime(startTime: number): number {
    this.metrics.loadTime = Math.round(performance.now() - startTime);
    return this.metrics.loadTime;
  }

  measureInteractionTime<T>(callback: () => T): { result: T; time: number } {
    const startTime = performance.now();
    const result = callback();
    this.metrics.interactionTime = Math.round(performance.now() - startTime);
    return { result, time: this.metrics.interactionTime };
  }

  getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  stopMonitoring(): PerformanceMetrics {
    this.isMonitoring = false;
    return this.metrics;
  }

  resetMetrics(): void {
    this.metrics = {
      fps: 0,
      memory: 0,
      loadTime: 0,
      interactionTime: 0
    };
  }
}

interface PerformanceMemory {
  usedJSHeapSize: number;
  jsHeapSizeLimit: number;
  totalJSHeapSize: number;
}

export const canvasPerfMonitor = new CanvasPerformanceMonitor();
export default CanvasPerformanceMonitor;
