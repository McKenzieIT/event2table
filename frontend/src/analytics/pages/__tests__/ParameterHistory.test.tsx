// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * ParameterHistory 功能测试
 *
 * 测试参数变更历史页面功能
 */

import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import ParameterHistory from '../ParameterHistory';

// Mock useOutletContext
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useOutletContext: vi.fn(),
  };
});

// Mock SelectGamePrompt component
vi.mock('@shared/ui/SelectGamePrompt', () => ({
  SelectGamePrompt: ({ message }: { message: string }) => (
    <div data-testid="select-game-prompt">{message}</div>
  ),
}));

describe('ParameterHistory', () => {
  it('should render select game prompt when no game is selected', () => {
    const { useOutletContext } = require('react-router-dom');
    useOutletContext.mockReturnValue({ currentGame: null });

    render(
      <BrowserRouter>
        <ParameterHistory />
      </BrowserRouter>
    );

    expect(screen.getByTestId('select-game-prompt')).toBeInTheDocument();
    expect(screen.getByText('查看参数变更历史需要先选择游戏')).toBeInTheDocument();
  });

  it('should render parameter history page when game is selected', () => {
    const { useOutletContext } = require('react-router-dom');
    useOutletContext.mockReturnValue({
      currentGame: { gid: 1, name: 'Test Game' },
    });

    render(
      <BrowserRouter>
        <ParameterHistory />
      </BrowserRouter>
    );

    expect(screen.getByText('参数变更历史')).toBeInTheDocument();
    expect(screen.getByText('查看参数历史变更记录')).toBeInTheDocument();
  });

  it('should render page header with glass card styling', () => {
    const { useOutletContext } = require('react-router-dom');
    useOutletContext.mockReturnValue({
      currentGame: { gid: 1, name: 'Test Game' },
    });

    const { container } = render(
      <BrowserRouter>
        <ParameterHistory />
      </BrowserRouter>
    );

    const pageHeader = container.querySelector('.page-header');
    expect(pageHeader).toBeInTheDocument();
    expect(pageHeader).toHaveClass('glass-card');
  });

  it('should render history card with glass card styling', () => {
    const { useOutletContext } = require('react-router-dom');
    useOutletContext.mockReturnValue({
      currentGame: { gid: 1, name: 'Test Game' },
    });

    const { container } = render(
      <BrowserRouter>
        <ParameterHistory />
      </BrowserRouter>
    );

    const historyCard = container.querySelector('.history-card');
    expect(historyCard).toBeInTheDocument();
    expect(historyCard).toHaveClass('glass-card');
  });

  it('should render main container', () => {
    const { useOutletContext } = require('react-router-dom');
    useOutletContext.mockReturnValue({
      currentGame: { gid: 1, name: 'Test Game' },
    });

    const { container } = render(
      <BrowserRouter>
        <ParameterHistory />
      </BrowserRouter>
    );

    const mainContainer = container.querySelector('.param-history-container');
    expect(mainContainer).toBeInTheDocument();
  });
});
