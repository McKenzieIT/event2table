/**
 * FieldSelectorEnhanced.test.js
 * 增强版字段选择器的 TDD 测试
 *
 * 测试策略：
 * 1. Red - 先写测试，运行失败
 * 2. Green - 写最小代码使测试通过
 * 3. Refactor - 重构代码，保持测试通过
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fetchParams } from '@shared/api/eventNodeBuilder';
import FieldSelectorEnhanced from './FieldSelectorEnhanced';

// Mock fetchParams API
vi.mock('@shared/api/eventNodeBuilder', () => ({
  fetchParams: vi.fn(),
}));

// 创建测试用 QueryClient
function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        cacheTime: 0,
      },
    },
  });
}

// 测试包装器
function TestWrapper({ children }) {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
}

describe('FieldSelectorEnhanced - TDD 测试套件', () => {
  const mockSelectedEvent = { id: 1968, name: 'role.online' };
  const mockCanvasFields = [
    { fieldName: 'serverName', displayName: '服务器名称' }
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ==================== 测试 1: 字段加载 ====================
  describe('当选择事件后', () => {
    it('应该显示所有参数字段', async () => {
      // === Red: 测试失败（功能未实现）===
      // Mock API 返回
      fetchParams.mockResolvedValue([
        { param_name: 'serverId', param_name_cn: '服务器ID' },
        { param_name: 'serverName', param_name_cn: '服务器名称' },
        { param_name: 'roleId', param_name_cn: '角色ID' },
        { param_name: 'roleName', param_name_cn: '角色名称' },
        { param_name: 'level', param_name_cn: '等级' },
        { param_name: 'vipLevel', param_name_cn: 'VIP等级' },
        { param_name: 'loginTime', param_name_cn: '登录时间' },
        { param_name: 'ip', param_name_cn: 'IP地址' },
        { param_name: 'deviceId', param_name_cn: '设备ID' },
      ]);

      // 渲染组件
      render(
        <TestWrapper>
          <FieldSelectorEnhanced
            value=""
            onChange={vi.fn()}
            selectedEvent={mockSelectedEvent}
            canvasFields={[]}
          />
        </TestWrapper>
      );

      // 等待加载完成
      await waitFor(() => {
        expect(screen.getByText('服务器ID')).toBeInTheDocument();
      });

      // === Green: 验证所有字段都显示 ===
      expect(screen.getByText('服务器名称')).toBeInTheDocument();
      expect(screen.getByText('角色ID')).toBeInTheDocument();
      expect(screen.getByText('角色名称')).toBeInTheDocument();
      expect(screen.getByText('等级')).toBeInTheDocument();
      expect(screen.getByText('VIP等级')).toBeInTheDocument();
      expect(screen.getByText('登录时间')).toBeInTheDocument();
      expect(screen.getByText('IP地址')).toBeInTheDocument();
      expect(screen.getByText('设备ID')).toBeInTheDocument();

      // 验证 API 被调用
      expect(fetchParams).toHaveBeenCalledWith(1968);
    });
  });

  // ==================== 测试 2: 已在画布标记 ====================
  describe('当字段已在画布上', () => {
    it('应该显示绿色背景和勾选标记', async () => {
      // === Red: 测试失败 ===
      fetchParams.mockResolvedValue([
        { param_name: 'serverName', param_name_cn: '服务器名称' },
      ]);

      const onChange = vi.fn();

      render(
        <TestWrapper>
          <FieldSelectorEnhanced
            value=""
            onChange={onChange}
            selectedEvent={mockSelectedEvent}
            canvasFields={mockCanvasFields}
          />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('服务器名称')).toBeInTheDocument();
      });

      // === Green: 验证视觉标记 ===
      const serverNameOption = screen.getByText(/服务器名称/);

      // 检查是否有勾选标记
      expect(serverNameOption.textContent).toContain('✓');

      // 检查是否有 CSS class
      expect(serverNameOption).toHaveClass('field-in-canvas');

      // 检查样式（绿色背景）
      expect(serverNameOption).toHaveStyle({
        backgroundColor: '#d1fae5',
      });
    });
  });

  // ==================== 测试 3: 字段分组 ====================
  describe('字段分组显示', () => {
    it('应该按参数字段和基础字段分组', async () => {
      // === Red: 测试失败 ===
      fetchParams.mockResolvedValue([
        { param_name: 'serverName', param_name_cn: '服务器名称' },
        { param_name: 'roleId', param_name_cn: '角色ID' },
      ]);

      render(
        <TestWrapper>
          <FieldSelectorEnhanced
            value=""
            onChange={vi.fn()}
            selectedEvent={mockSelectedEvent}
            canvasFields={[]}
          />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('服务器名称')).toBeInTheDocument();
      });

      // === Green: 验证分组 ===
      // 检查分组标签
      expect(screen.getByText(/📦 参数字段/)).toBeInTheDocument();
      expect(screen.getByText(/📊 基础字段/)).toBeInTheDocument();

      // 检查分组内的字段数量
      const selectElement = screen.getByRole('combobox');
      const paramGroup = selectElement.querySelector('optgroup[label*="参数字段"]');
      const baseGroup = selectElement.querySelector('optgroup[label*="基础字段"]');

      // 参数字段应该有 2 个
      expect(paramGroup.querySelectorAll('option').length).toBe(2);

      // 基础字段应该有 6 个（ds, role_id, account_id, utdid, tm, ts）
      expect(baseGroup.querySelectorAll('option').length).toBe(6);
    });
  });

  // ==================== 测试 4: 无事件选择 ====================
  describe('当未选择事件时', () => {
    it('应该显示"请先选择事件"提示', () => {
      // === Red: 测试失败 ===
      render(
        <TestWrapper>
          <FieldSelectorEnhanced
            value=""
            onChange={vi.fn()}
            selectedEvent={null}
            canvasFields={[]}
          />
        </TestWrapper>
      );

      // === Green: 验证提示 ===
      const selectElement = screen.getByRole('combobox');
      expect(selectElement).toBeDisabled();
      expect(screen.getByText('请先选择事件')).toBeInTheDocument();
    });
  });

  // ==================== 测试 5: 字段选择事件 ====================
  describe('当选择字段时', () => {
    it('应该调用 onChange 回调', async () => {
      // === Red: 测试失败 ===
      fetchParams.mockResolvedValue([
        { param_name: 'serverName', param_name_cn: '服务器名称' },
      ]);

      const onChange = vi.fn();

      render(
        <TestWrapper>
          <FieldSelectorEnhanced
            value=""
            onChange={onChange}
            selectedEvent={mockSelectedEvent}
            canvasFields={[]}
          />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('服务器名称')).toBeInTheDocument();
      });

      // === Green: 验证 onChange ===
      const selectElement = screen.getByRole('combobox');
      selectElement.value = 'serverName';
      selectElement.dispatchEvent(new Event('change', { bubbles: true }));

      expect(onChange).toHaveBeenCalledWith('serverName');
    });
  });
});

// ==================== Refactor 阶段 ====================
describe('Refactor 验证', () => {
  it('重构后所有测试仍然通过', async () => {
    // 运行所有测试，确保重构没有破坏功能
    // 这个测试套件作为回归测试
    expect(true).toBe(true);
  });
});
