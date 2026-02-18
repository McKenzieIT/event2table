/**
 * Canvas性能监控工具
 * 监控FPS、内存、响应时间等性能指标
 */

export class CanvasPerformanceMonitor {
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

    /**
     * 开始性能监控
     */
    startMonitoring() {
        if (this.isMonitoring) return;
        this.isMonitoring = true;
        this.frameCount = 0;
        this.lastTime = performance.now();
        this.measureFPS();
        this.measureMemory();
    }

    /**
     * 测量FPS
     */
    measureFPS() {
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

    /**
     * 测量内存使用
     */
    measureMemory() {
        if (!this.isMonitoring) return;

        if (performance.memory) {
            this.metrics.memory = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024);
        } else {
        }

        setTimeout(() => this.measureMemory(), 5000);
    }

    /**
     * 测量加载时间
     */
    measureLoadTime(startTime) {
        this.metrics.loadTime = Math.round(performance.now() - startTime);
        return this.metrics.loadTime;
    }

    /**
     * 测量交互时间
     */
    measureInteractionTime(callback) {
        const startTime = performance.now();
        callback();
        this.metrics.interactionTime = Math.round(performance.now() - startTime);
        return this.metrics.interactionTime;
    }

    /**
     * 获取当前指标
     */
    getMetrics() {
        return { ...this.metrics };
    }

    /**
     * 停止监控
     */
    stopMonitoring() {
        this.isMonitoring = false;
        return this.metrics;
    }

    /**
     * 重置指标
     */
    resetMetrics() {
        this.metrics = {
            fps: 0,
            memory: 0,
            loadTime: 0,
            interactionTime: 0
        };
    }
}

// 导出单例
export const canvasPerfMonitor = new CanvasPerformanceMonitor();

// 默认导出类
export default CanvasPerformanceMonitor;
