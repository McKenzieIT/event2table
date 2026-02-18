/**
 * WhereBuilderModal Component Tests
 * 阶段2：模式融合 - 移除简单/高级模式切换
 */
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import WhereBuilderModal from './WhereBuilderModal';

describe('WhereBuilderModal - Phase 2: Mode Removal', () => {
  const mockProps = {
    isOpen: true,
    onClose: vi.fn(),
    conditions: [],
    onApply: vi.fn(),
    canvasFields: [],
    selectedEvent: { id: 1968, name: 'role.online' }
  };

  it('不应该显示模式切换按钮', () => {
    // When
    render(<WhereBuilderModal {...mockProps} />);

    // Then - 验证模式切换按钮不存在
    expect(screen.queryByText('简单模式')).not.toBeInTheDocument();
    expect(screen.queryByText('高级模式')).not.toBeInTheDocument();
  });

  it('应该同时显示"添加条件"和"添加分组"按钮', () => {
    // When
    render(<WhereBuilderModal {...mockProps} />);

    // Then - 验证两个按钮都存在
    expect(screen.getByText('添加条件')).toBeInTheDocument();
    expect(screen.getByText('添加分组')).toBeInTheDocument();
  });

  it('"添加分组"按钮应该始终可见（不受模式控制）', () => {
    // When
    render(<WhereBuilderModal {...mockProps} />);

    // Then - "添加分组"按钮应该直接可见
    const addGroupButton = screen.getByText('添加分组');
    expect(addGroupButton).toBeVisible();
    expect(addGroupButton.closest('button')).not.toBeDisabled();
  });

  it('不应该有mode状态', () => {
    // 当移除模式后，组件内部不应该使用mode状态
    // 这个测试验证组件在没有mode prop的情况下正常工作
    render(<WhereBuilderModal {...mockProps} />);

    // Then - 模态框应该正常显示，不报错
    expect(screen.getByText('WHERE条件构建器')).toBeInTheDocument();
  });
});
