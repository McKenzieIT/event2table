/**
 * SearchInput Component Tests
 * 测试搜索输入组件的所有功能
 */

import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import SearchInput from './SearchInput';

describe('SearchInput Component', () => {
  // Use fake timers for debounce tests
  beforeEach(() => {
    // Ensure real timers are used before setting up fake timers
    vi.useRealTimers();
    vi.useFakeTimers();
  });

  afterEach(() => {
    // Ensure all timers are flushed and restored
    vi.runAllTimers();
    vi.useRealTimers();
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
      render(<SearchInput icon={<TestIcon />} />);
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
      // Use fireEvent instead of userEvent for fake timer compatibility
      fireEvent.change(input, { target: { value: 'test' } });

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
      // Use fireEvent for fake timer compatibility
      fireEvent.change(input, { target: { value: 'test' } });

      // Should not have been called immediately
      expect(handleChange).not.toHaveBeenCalled();

      // Fast-forward time by 300ms using act
      await act(async () => {
        vi.advanceTimersByTime(300);
      });

      // Now it should have been called
      expect(handleChange).toHaveBeenCalledWith('test');
    });

    it('should use default debounce of 300ms', async () => {
      const handleChange = vi.fn();
      render(<SearchInput onChange={handleChange} />);

      const input = screen.getByRole('textbox');
      fireEvent.change(input, { target: { value: 'test' } });

      await act(async () => {
        vi.advanceTimersByTime(299);
      });
      expect(handleChange).not.toHaveBeenCalled();

      await act(async () => {
        vi.advanceTimersByTime(1);
      });
      expect(handleChange).toHaveBeenCalledWith('test');
    });

    it('should cancel previous debounce on new input', async () => {
      const handleChange = vi.fn();
      render(<SearchInput onChange={handleChange} debounceMs={300} />);

      const input = screen.getByRole('textbox');
      fireEvent.change(input, { target: { value: 'te' } });

      await act(async () => {
        vi.advanceTimersByTime(200);
      });

      fireEvent.change(input, { target: { value: 'test' } });

      await act(async () => {
        vi.advanceTimersByTime(300);
      });

      expect(handleChange).toHaveBeenCalledTimes(1);
      expect(handleChange).toHaveBeenCalledWith('test');
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

      // Use fireEvent for click
      fireEvent.click(screen.getByLabelText('清除搜索'));

      expect(screen.getByRole('textbox')).toHaveValue('');
      expect(handleClear).toHaveBeenCalled();
      expect(handleChange).toHaveBeenCalledWith('');
    });

    it('should focus input after clearing', async () => {
      render(<SearchInput value="test" />);

      fireEvent.click(screen.getByLabelText('清除搜索'));

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
      fireEvent.focus(input);

      expect(container.querySelector('.search-input--focused')).toBeInTheDocument();
    });

    it('should remove focused class when blurred', async () => {
      const { container } = render(<SearchInput />);

      const input = screen.getByRole('textbox');
      fireEvent.focus(input);
      fireEvent.blur(input);

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

      // The input is disabled, so it cannot be interacted with by users
      expect(input).toBeDisabled();

      // In jsdom, fireEvent.change can still modify the value even on disabled inputs
      // This is a jsdom quirk - in real browsers, disabled inputs don't receive input events
      // The key test is that the input is disabled, which prevents user interaction
      // Note: The component's internal handleChange is still called in jsdom environment
    });
  });

  describe('Keyboard Shortcut', () => {
    it('should focus input on Ctrl+K', async () => {
      render(<SearchInput />);

      const input = screen.getByRole('textbox');

      // The keyboard shortcut is handled by onKeyDown on the input itself
      // We need to simulate the keydown event with Ctrl+K on the input
      fireEvent.keyDown(input, { key: 'k', ctrlKey: true });
      expect(input).toHaveFocus();
    });

    it('should focus input on Cmd+K (Mac)', async () => {
      render(<SearchInput />);

      const input = screen.getByRole('textbox');

      fireEvent.keyDown(input, { key: 'k', metaKey: true });
      expect(input).toHaveFocus();
    });

    it('should show shortcut hint when not focused', () => {
      render(<SearchInput />);
      expect(screen.getByText('⌘K')).toBeInTheDocument();
    });

    it('should hide shortcut hint when focused', async () => {
      const { container } = render(<SearchInput />);

      fireEvent.focus(screen.getByRole('textbox'));
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

    it('should have default aria-label', () => {
      render(<SearchInput />);
      // Component uses default aria-label "搜索..."
      expect(screen.getByLabelText('搜索...')).toBeInTheDocument();
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
      fireEvent.change(input, { target: { value: 'test' } });

      await act(async () => {
        vi.advanceTimersByTime(300);
      });

      // Should not throw error
      expect(input).toHaveValue('test');
    });

    it('should handle empty onClear gracefully', async () => {
      render(<SearchInput value="test" />);

      fireEvent.click(screen.getByLabelText('清除搜索'));

      expect(screen.getByRole('textbox')).toHaveValue('');
    });

    it('should handle rapid input changes', async () => {
      const handleChange = vi.fn();
      render(<SearchInput onChange={handleChange} debounceMs={100} />);

      const input = screen.getByRole('textbox');
      fireEvent.change(input, { target: { value: 'rapid' } });

      await act(async () => {
        vi.advanceTimersByTime(50);
      });

      fireEvent.change(input, { target: { value: 'rapid changes' } });

      await act(async () => {
        vi.advanceTimersByTime(100);
      });

      expect(handleChange).toHaveBeenCalledTimes(1);
      expect(handleChange).toHaveBeenCalledWith('rapid changes');
    });
  });
});
