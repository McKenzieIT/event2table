// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * FlowBuilder.test.tsx
 *
 * Unit tests for FlowBuilder component
 */
import { render, screen } from '@test/test-utils';
import { describe, it, expect, vi } from 'vitest';

import FlowBuilder from '../FlowBuilder';
// Mock useGameContext
vi.mock('@shared/hooks/useGameContext', () => ({
  useGameContext: () => ({
    currentGameGid: '10000147',
  }),
}));
// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
global.localStorage = localStorageMock;
describe('FlowBuilder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  it('should render FlowBuilder component', () => {
    render(
        <FlowBuilder />
    );
    expect(screen.getByText('流程构建器')).toBeInTheDocument();
  });
  it('should display game GID from context', () => {
    render(
        <FlowBuilder />
    );
    expect(screen.getByText('游戏 GID: 10000147')).toBeInTheDocument();
  });
  it('should display flow builder description', () => {
    render(
        <FlowBuilder />
    );
    expect(screen.getByText('可视化流程构建功能')).toBeInTheDocument();
    expect(screen.getByText('当前游戏上下文: GID 10000147')).toBeInTheDocument();
  });
  it('should use game GID from URL parameter when provided', () => {
    // Mock URL search params with game_gid
    const mockSearchParams = new URLSearchParams('game_gid=99999999');
    vi.spyOn(require('react-router-dom'), 'useSearchParams').mockReturnValue([mockSearchParams]);
    render(
        <FlowBuilder />
    );
    // The component should display the URL parameter game_gid
    expect(screen.getByText('当前游戏上下文: GID 99999999')).toBeInTheDocument();
  });
  it('should have correct container classes', () => {
    const { container } = render(
        <FlowBuilder />
    );
    const flowBuilderContainer = container.querySelector('.flow-builder-container');
    expect(flowBuilderContainer).toBeInTheDocument();
  });
  it('should render page header card', () => {
    const { container } = render(
        <FlowBuilder />
    );
    const pageHeader = container.querySelector('.page-header');
    expect(pageHeader).toBeInTheDocument();
  });
  it('should render builder card', () => {
    const { container } = render(
        <FlowBuilder />
    );
    const builderCard = container.querySelector('.builder-card');
    expect(builderCard).toBeInTheDocument();
  });
});
