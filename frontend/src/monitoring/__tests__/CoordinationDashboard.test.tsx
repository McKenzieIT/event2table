/**
 * CoordinationDashboard 组件测试
 * 遵循TDD开发模式：先写测试，看测试失败，再编写实现
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CoordinationDashboard } from '../CoordinationDashboard';

describe('CoordinationDashboard', () => {
  beforeEach(() => {
    // Clear mocks to avoid side effects
    vi.clearAllMocks();
  });

  describe('初始渲染', () => {
    it('应该渲染标题', () => {
      render(<CoordinationDashboard />);
      expect(screen.getByText('Performance Coordination Dashboard')).toBeInTheDocument();
    });

    it('应该显示所有Subagent状态', () => {
      render(<CoordinationDashboard />);
      expect(screen.getByText(/Subagent 1/i)).toBeInTheDocument();
      expect(screen.getByText(/Subagent 2/i)).toBeInTheDocument();
      expect(screen.getByText(/Subagent 3/i)).toBeInTheDocument();
      expect(screen.getByText(/Subagent 4/i)).toBeInTheDocument();
    });

    it('应该显示当前Checkpoint', () => {
      render(<CoordinationDashboard />);
      expect(screen.getByText(/Checkpoint:/i)).toBeInTheDocument();
    });
  });

  describe('Subagent状态显示', () => {
    it('应该显示Subagent ID', () => {
      render(<CoordinationDashboard />);
      expect(screen.getByText('Monitoring Baseline')).toBeInTheDocument();
    });

    it('应该显示Subagent任务进度', () => {
      render(<CoordinationDashboard />);
      // 检查进度条或百分比显示
      const progressElement = screen.getAllByText(/Progress:/i);
      expect(progressElement.length).toBeGreaterThan(0);
    });
  });

  describe('冲突检测', () => {
    it('应该显示冲突检测部分', () => {
      render(<CoordinationDashboard />);
      expect(screen.getByText(/Conflict Detection/i)).toBeInTheDocument();
    });

    it('应该显示冲突数量（如果有）', () => {
      render(<CoordinationDashboard />);
      // 初始状态没有冲突，所以不显示Conflicts:
      const conflictElement = screen.queryByText(/Conflicts:/i);
      // 当没有冲突时，显示"No conflicts detected"
      expect(screen.getByText(/No conflicts detected/i)).toBeInTheDocument();
    });
  });

  describe('性能指标', () => {
    it('应该显示整体性能摘要', () => {
      render(<CoordinationDashboard />);
      expect(screen.getByText(/Performance Summary/i)).toBeInTheDocument();
    });

    it('应该显示API调用次数', () => {
      render(<CoordinationDashboard />);
      expect(screen.getByText(/API Calls/i)).toBeInTheDocument();
    });

    it('应该显示缓存命中率', () => {
      render(<CoordinationDashboard />);
      expect(screen.getByText(/Cache Hit Rate/i)).toBeInTheDocument();
    });
  });

  describe('交互功能', () => {
    it('应该支持刷新按钮', () => {
      render(<CoordinationDashboard />);
      const refreshButton = screen.getByRole('button', { name: /refresh/i });
      expect(refreshButton).toBeInTheDocument();
    });

    it('应该支持导出报告按钮', () => {
      render(<CoordinationDashboard />);
      const exportButton = screen.getByRole('button', { name: /export/i });
      expect(exportButton).toBeInTheDocument();
    });
  });
});
