// @ts-nocheck - TypeScript检查暂禁用
/**
 * SearchInput Component Tests
 * 测试搜索输入组件的所有功能
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SearchInput from './SearchInput';

describe('SearchInput Component', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Rendering', () => {
    it('should render input element', () => {
      render(<SearchInput />);
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('should render with placeholder', () => {
      render(<SearchInput placeholder="Search..." />);
      expect(screen.getByPlaceholderText('Search...')).toBeInTheDocument();
    });

    it('should render with custom icon', () => {
      const TestIcon = () => <svg data-testid="search-icon" />;
      render(<SearchInput icon={TestIcon} />);
      expect(screen.getByTestId('search-icon')).toBeInTheDocument();
    });
  });

  describe('Value Handling', () => {
    it('should display value', () => {
      render(<SearchInput value="search term" />);
      expect(screen.getByDisplayValue('search term')).toBeInTheDocument();
    });

    it('should update internal value on input', async () => {
      render(<SearchInput />);
      
      const input = screen.getByRole('textbox');
      await userEvent.type(input, 'test');
      
      expect(input).toHaveValue('test');
    });

    it('should sync with external value', () => {
      const { rerender } = render(<SearchInput value="initial" />);
      expect(screen.getByDisplayValue('initial')).toBeInTheDocument();
      
      rerender(<SearchInput value="updated" />);
      expect(screen.getByDisplayValue('updated')).toBeInTheDocument();
    });
  });

  describe('Debounce', () => {
    it('should debounce onChange callback', async () => {
      const handleChange = vi.fn();
      render(<SearchInput onChange={handleChange} debounceMs={300} />);
      
      const input = screen.getByRole('textbox');
      await userEvent.type(input, 'test');
      
      // Should not have been called immediately
      expect(handleChange).not.toHaveBeenCalled();
      
      // Fast-forward time by 300ms
      vi.advanceTimersByTime(300);
      
      await waitFor(() => {
        expect(handleChange).toHaveBeenCalledWith('test');
      });
    });

    it('should use default debounce of 300ms', async () => {
      const handleChange = vi.fn();
      render(<SearchInput onChange={handleChange} />);
      
      const input = screen.getByRole('textbox');
      await userEvent.type(input, 'test');
      
      vi.advanceTimersByTime(299);
      expect(handleChange).not.toHaveBeenCalled();
      
      vi.advanceTimersByTime(1);
      await waitFor(() => {
        expect(handleChange).toHaveBeenCalledWith('test');
      });
    });

    it('should cancel previous debounce on new input', async () => {
      const handleChange = vi.fn();
      render(<SearchInput onChange={handleChange} debounceMs={300} />);
      
      const input = screen.getByRole('textbox');
      await userEvent.type(input, 'te');
      vi.advanceTimersByTime(200);
      
      await userEvent.type(input, 'st');
      vi.advanceTimersByTime(300);
      
      await waitFor(() => {
        expect(handleChange).toHaveBeenCalledTimes(1);
        expect(handleChange).toHaveBeenCalledWith('test');
      });
    });
  });

  describe('Clear Button', () => {
    it('should show clear button when value is not empty', () => {
      render(<SearchInput value="test" />);
      expect(screen.getByLabelText('清除搜索')).toBeInTheDocument();
    });

    it('should not show clear button when value is empty', () => {
      render(<SearchInput />);
      expect(screen.queryByLabelText('清除搜索')).not.toBeInTheDocument();
    });

    it('should clear value when clear button is clicked', async () => {
      const handleClear = vi.fn();
      const handleChange = vi.fn();
      render(<SearchInput value="test" onClear={handleClear} onChange={handleChange} />);
      
      await userEvent.click(screen.getByLabelText('清除搜索'));
      
      expect(screen.getByRole('textbox')).toHaveValue('');
      expect(handleClear).toHaveBeenCalled();
      expect(handleChange).toHaveBeenCalledWith('');
    });

    it('should focus input after clearing', async () => {
      render(<SearchInput value="test" />);
      
      await userEvent.click(screen.getByLabelText('清除搜索'));
      
      expect(screen.getByRole('textbox')).toHaveFocus();
    });

    it('should not show clear button when disabled', () => {
      render(<SearchInput value="test" disabled />);
      expect(screen.queryByLabelText('清除搜索')).not.toBeInTheDocument();
    });
  });

  describe('Focus State', () => {
    it('should have focused class when focused', async () => {
      const { container } = render(<SearchInput />);
      
      const input = screen.getByRole('textbox');
      await userEvent.click(input);
      
      expect(container.querySelector('.search-input--focused')).toBeInTheDocument();
    });

    it('should remove focused class when blurred', async () => {
      const { container } = render(<SearchInput />);
      
      const input = screen.getByRole('textbox');
      await userEvent.click(input);
      await userEvent.tab();
      
      expect(container.querySelector('.search-input--focused')).not.toBeInTheDocument();
    });
  });

  describe('Disabled State', () => {
    it('should be disabled when disabled prop is true', () => {
      render(<SearchInput disabled />);
      expect(screen.getByRole('textbox')).toBeDisabled();
    });

    it('should have disabled class when disabled', () => {
      const { container } = render(<SearchInput disabled />);
      expect(container.querySelector('.search-input-wrapper--disabled')).toBeInTheDocument();
    });

    it('should not allow input when disabled', async () => {
      render(<SearchInput disabled />);
      const input = screen.getByRole('textbox');
      
      await userEvent.type(input, 'test');
      expect(input).toHaveValue('');
    });
  });

  describe('Keyboard Shortcut', () => {
    it('should focus input on Ctrl+K', async () => {
      render(<SearchInput />);
      
      await userEvent.keyboard('{Control>}k{/Control}');
      expect(screen.getByRole('textbox')).toHaveFocus();
    });

    it('should focus input on Cmd+K (Mac)', async () => {
      render(<SearchInput />);
      
      await userEvent.keyboard('{Meta>}k{/Meta}');
      expect(screen.getByRole('textbox')).toHaveFocus();
    });

    it('should show shortcut hint when not focused', () => {
      render(<SearchInput />);
      expect(screen.getByText('⌘K')).toBeInTheDocument();
    });

    it('should hide shortcut hint when focused', async () => {
      const { container } = render(<SearchInput />);
      
      await userEvent.click(screen.getByRole('textbox'));
      expect(container.querySelector('.shortcut-hint')).not.toBeInTheDocument();
    });

    it('should not show shortcut hint when disabled', () => {
      render(<SearchInput disabled />);
      expect(screen.queryByText('⌘K')).not.toBeInTheDocument();
    });
  });

  describe('Custom ClassName', () => {
    it('should apply custom className', () => {
      const { container } = render(<SearchInput className="custom-search" />);
      expect(container.querySelector('.custom-search')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('should have proper autocomplete attribute', () => {
      render(<SearchInput />);
      expect(screen.getByRole('textbox')).toHaveAttribute('autoComplete', 'off');
    });

    it('should support aria-label', () => {
      render(<SearchInput aria-label="Search items" />);
      expect(screen.getByLabelText('Search items')).toBeInTheDocument();
    });

    it('should have proper role for clear button', () => {
      render(<SearchInput value="test" />);
      expect(screen.getByRole('button', { name: /清除搜索/ })).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty onChange gracefully', async () => {
      render(<SearchInput />);
      
      const input = screen.getByRole('textbox');
      await userEvent.type(input, 'test');
      vi.advanceTimersByTime(300);
      
      // Should not throw error
      expect(input).toHaveValue('test');
    });

    it('should handle empty onClear gracefully', async () => {
      render(<SearchInput value="test" />);
      
      await userEvent.click(screen.getByLabelText('清除搜索'));
      
      expect(screen.getByRole('textbox')).toHaveValue('');
    });

    it('should handle rapid input changes', async () => {
      const handleChange = vi.fn();
      render(<SearchInput onChange={handleChange} debounceMs={100} />);
      
      const input = screen.getByRole('textbox');
      await userEvent.type(input, 'rapid');
      vi.advanceTimersByTime(50);
      await userEvent.type(input, ' changes');
      vi.advanceTimersByTime(100);
      
      await waitFor(() => {
        expect(handleChange).toHaveBeenCalledTimes(1);
        expect(handleChange).toHaveBeenCalledWith('rapid changes');
      });
    });
  });
});
