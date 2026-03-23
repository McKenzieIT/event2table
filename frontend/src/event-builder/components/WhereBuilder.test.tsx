import { render, screen, fireEvent, waitFor } from '@test/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import WhereBuilder, { WhereCondition } from './WhereBuilder';

describe('WhereBuilder Component', () => {
  const mockOnChange = vi.fn();
  const mockOnOpenModal = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  // Helper function to expand the component
  const expandComponent = () => {
    const header = screen.getByText(/WHERE条件/).closest('.section-header');
    if (header) {
      fireEvent.click(header);
    }
  };

  describe('渲染测试', () => {
    it('应该正确渲染 WHERE 条件构建器', async () => {
      render(
        <WhereBuilder
          conditions={[]}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      // 验证标题存在
      expect(screen.getByText(/WHERE条件/)).toBeInTheDocument();

      // 展开组件以查看内容
      expandComponent();

      // 验证空状态提示
      await waitFor(() => {
        expect(screen.getByText(/暂无WHERE条件/)).toBeInTheDocument();
      });
    });

    it('应该显示配置按钮', () => {
      render(
        <WhereBuilder
          conditions={[]}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      expect(screen.getByText(/配置/)).toBeInTheDocument();
    });
  });

  describe('条件显示测试', () => {
    it('应该正确显示单个条件', async () => {
      const conditions: WhereCondition[] = [
        {
          id: '1',
          field: 'role_id',
          operator: '=',
          value: '12345'
        }
      ];

      render(
        <WhereBuilder
          conditions={conditions}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      // 展开组件以查看条件
      expandComponent();

      await waitFor(() => {
        expect(screen.getByText(/role_id = '12345'/)).toBeInTheDocument();
      });
    });

    it('应该正确显示多个条件', async () => {
      const conditions: WhereCondition[] = [
        {
          id: '1',
          field: 'role_id',
          operator: '=',
          value: '12345',
          logicalOperator: 'AND'
        },
        {
          id: '2',
          field: 'account_id',
          operator: '=',
          value: '67890'
        }
      ];

      render(
        <WhereBuilder
          conditions={conditions}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      // 展开组件以查看条件
      expandComponent();

      await waitFor(() => {
        expect(screen.getByText(/AND role_id = '12345'/)).toBeInTheDocument();
        expect(screen.getByText(/account_id = '67890'/)).toBeInTheDocument();
      });
    });

    it('应该正确显示条件组', async () => {
      const conditions: WhereCondition[] = [
        {
          id: '1',
          type: 'group',
          field: '',  // Required by type
          operator: '', // Required by type
          value: '', // Required by type
          conditions: [
            { id: '1-1', field: 'role_id', operator: '=', value: '12345' }
          ]
        }
      ];

      render(
        <WhereBuilder
          conditions={conditions}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      // 展开组件以查看条件组
      expandComponent();

      await waitFor(() => {
        expect(screen.getByText(/\(1 个条件\)/)).toBeInTheDocument();
      });
    });
  });

  describe('交互测试', () => {
    it('点击配置按钮应该调用 onOpenModal', () => {
      render(
        <WhereBuilder
          conditions={[]}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      const configButton = screen.getByText(/配置/);
      fireEvent.click(configButton);

      expect(mockOnOpenModal).toHaveBeenCalledTimes(1);
    });

    it('点击标题栏应该切换折叠状态', async () => {
      render(
        <WhereBuilder
          conditions={[]}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      const header = screen.getByText(/WHERE条件/).closest('.section-header');

      // 初始状态是折叠的，内容不可见
      expect(screen.queryByText(/点击"配置"按钮编辑WHERE条件/)).not.toBeInTheDocument();

      // 点击展开
      if (header) {
        fireEvent.click(header);
      }

      await waitFor(() => {
        expect(screen.getByText(/点击"配置"按钮编辑WHERE条件/)).toBeInTheDocument();
      });
    });
  });

  describe('边界情况测试', () => {
    it('应该处理 undefined 或 null 的 conditions', async () => {
      render(
        <WhereBuilder
          conditions={undefined as any}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      // 展开组件以查看内容
      expandComponent();

      await waitFor(() => {
        expect(screen.getByText(/暂无WHERE条件/)).toBeInTheDocument();
      });
    });

    it('应该处理空字段或值的条件', async () => {
      const conditions: WhereCondition[] = [
        {
          id: '1',
          field: '',
          operator: '=',
          value: ''
        }
      ];

      render(
        <WhereBuilder
          conditions={conditions}
          onChange={mockOnChange}
          onOpenModal={mockOnOpenModal}
        />
      );

      // 展开组件以查看条件
      expandComponent();

      await waitFor(() => {
        expect(screen.getByText(/\? = ''/)).toBeInTheDocument();
      });
    });
  });
});
