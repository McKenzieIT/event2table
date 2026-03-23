// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * ParameterHistory 功能测试
 *
 * 测试参数变更历史页面功能
 */
import { render, screen, createMockGameContext } from '@test/test-utils';
import { describe, it, expect, vi, beforeEach } from 'vitest';

import ParameterHistory from '../ParameterHistory';

// 创建可变的mock函数，允许在测试中动态修改返回值
const mockOutletContext = vi.fn();

// Mock useOutletContext using the new unified mock approach
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useOutletContext: () => mockOutletContext(),
  };
});

// Mock SelectGamePrompt component
vi.mock('@shared/ui/SelectGamePrompt', () => ({
  SelectGamePrompt: ({ message }: { message: string }) => (
    <div data-testid="select-game-prompt">{message}</div>
  ),
}));

describe('ParameterHistory', () => {
  // 默认返回有游戏上下文
  beforeEach(() => {
    mockOutletContext.mockReturnValue(createMockGameContext());
  });

  it('should render select game prompt when no game is selected', () => {
    mockOutletContext.mockReturnValue(createMockGameContext({ currentGame: null }));
    
    render(<ParameterHistory />);
    
    expect(screen.getByTestId('select-game-prompt')).toBeInTheDocument();
    expect(screen.getByText('查看参数变更历史需要先选择游戏')).toBeInTheDocument();
  });

  it('should render parameter history page when game is selected', () => {
    render(<ParameterHistory />);
    
    expect(screen.getByText('参数变更历史')).toBeInTheDocument();
    expect(screen.getByText('查看参数历史变更记录')).toBeInTheDocument();
  });

  it('should render page header with glass card styling', () => {
    const { container } = render(<ParameterHistory />);
    
    const pageHeader = container.querySelector('.page-header');
    expect(pageHeader).toBeInTheDocument();
    expect(pageHeader).toHaveClass('glass-card');
  });

  it('should render history card with glass card styling', () => {
    const { container } = render(<ParameterHistory />);
    
    const historyCard = container.querySelector('.history-card');
    expect(historyCard).toBeInTheDocument();
    expect(historyCard).toHaveClass('glass-card');
  });

  it('should render main container', () => {
    const { container } = render(<ParameterHistory />);
    
    const mainContainer = container.querySelector('.param-history-container');
    expect(mainContainer).toBeInTheDocument();
  });
});
