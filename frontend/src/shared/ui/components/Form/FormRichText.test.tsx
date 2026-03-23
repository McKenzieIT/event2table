/**
 * FormRichText Component - Test Suite
 * 
 * Comprehensive tests for FormRichText component including:
 * - Rendering behavior
 * - User interactions
 * - Toolbar functionality
 * - Edge cases and accessibility
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { z } from 'zod';

import Form from './Form';
import FormRichText from './FormRichText';

// Test wrapper component
const TestFormWrapper = ({
  children,
  schema,
  mode = 'onTouched',
  defaultValues = {},
}: {
  children: React.ReactNode;
  schema?: any;
  mode?: any;
  defaultValues?: any;
}) => {
  const form = useForm({
    resolver: schema ? zodResolver(schema) : undefined,
    mode,
    defaultValues,
  });

  return (
    <Form form={form} onSubmit={vi.fn()}>
      {children}
    </Form>
  );
};

describe('FormRichText Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock document.execCommand
    document.execCommand = vi.fn(() => true);
    // Mock window.prompt
    window.prompt = vi.fn(() => 'https://example.com');
  });

  describe('rendering', () => {
    it('should render rich text editor', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('should render label', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Content')).toBeInTheDocument();
    });

    it('should render toolbar with default buttons', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('toolbar')).toBeInTheDocument();
    });

    it('should render toolbar with custom buttons', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" toolbar={['bold', 'italic']} />
        </TestFormWrapper>
      );
      expect(screen.getByRole('toolbar')).toBeInTheDocument();
    });

    it('should render helper text when provided', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" helperText="Write your content here" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Write your content here')).toBeInTheDocument();
    });

    it('should render required indicator when required is true', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" required />
        </TestFormWrapper>
      );
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" className="custom-richtext" />
        </TestFormWrapper>
      );
      const wrapper = screen.getByRole('textbox').closest('.form-field-wrapper');
      expect(wrapper).toHaveClass('custom-richtext');
    });
  });

  describe('interactions', () => {
    it('should handle text input', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );

      const editor = screen.getByRole('textbox');
      await user.type(editor, 'Hello World');
      expect(editor).toHaveTextContent('Hello World');
    });

    it('should handle bold toolbar button', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" toolbar={['bold']} />
        </TestFormWrapper>
      );

      const boldButton = screen.getByTitle(/bold/i);
      await user.click(boldButton);

      expect(document.execCommand).toHaveBeenCalledWith('bold', false, undefined);
    });

    it('should handle italic toolbar button', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" toolbar={['italic']} />
        </TestFormWrapper>
      );

      const italicButton = screen.getByTitle(/italic/i);
      await user.click(italicButton);

      expect(document.execCommand).toHaveBeenCalledWith('italic', false, undefined);
    });

    it('should handle underline toolbar button', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" toolbar={['underline']} />
        </TestFormWrapper>
      );

      const underlineButton = screen.getByTitle(/underline/i);
      await user.click(underlineButton);

      expect(document.execCommand).toHaveBeenCalledWith('underline', false, undefined);
    });

    it('should handle link toolbar button', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" toolbar={['link']} />
        </TestFormWrapper>
      );

      const linkButton = screen.getByTitle(/link/i);
      await user.click(linkButton);

      expect(window.prompt).toHaveBeenCalled();
    });

    it('should handle list toolbar button', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" toolbar={['list']} />
        </TestFormWrapper>
      );

      const listButton = screen.getByTitle(/list/i);
      await user.click(listButton);

      expect(document.execCommand).toHaveBeenCalledWith('insertUnorderedList', false, undefined);
    });

    it('should handle keyboard shortcuts', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );

      const editor = screen.getByRole('textbox');
      editor.focus();
      await user.keyboard('{Control>}b{/Control}');

      expect(document.execCommand).toHaveBeenCalledWith('bold', false, undefined);
    });

    it('should handle default value', () => {
      render(
        <TestFormWrapper defaultValues={{ content: '<p>Default content</p>' }}>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );
      const editor = screen.getByRole('textbox');
      expect(editor.innerHTML).toContain('Default content');
    });

    it('should handle null value', () => {
      render(
        <TestFormWrapper defaultValues={{ content: null }}>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );
      const editor = screen.getByRole('textbox');
      expect(editor.innerHTML).toBe('');
    });

    it('should handle undefined value', () => {
      render(
        <TestFormWrapper defaultValues={{}}>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );
      const editor = screen.getByRole('textbox');
      expect(editor.innerHTML).toBe('');
    });
  });

  describe('edge cases', () => {
    it('should be disabled when disabled is true', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" disabled />
        </TestFormWrapper>
      );
      const editor = screen.getByRole('textbox');
      expect(editor).toHaveAttribute('contentEditable', 'false');
    });

    it('should handle maxLength constraint', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" maxLength={10} />
        </TestFormWrapper>
      );

      const editor = screen.getByRole('textbox');
      await user.type(editor, 'This is a very long text that exceeds the limit');

      expect(screen.getByText(/10 \/ 10/i)).toBeInTheDocument();
    });

    it('should display character count when showCharCount is true', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" maxLength={100} showCharCount />
        </TestFormWrapper>
      );
      expect(screen.getByText('0 / 100')).toBeInTheDocument();
    });

    it('should hide character count when showCharCount is false', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" maxLength={100} showCharCount={false} />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/\/ 100/i)).not.toBeInTheDocument();
    });

    it('should handle empty toolbar', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" toolbar={[]} />
        </TestFormWrapper>
      );
      const toolbar = screen.getByRole('toolbar');
      expect(toolbar.children).toHaveLength(0);
    });

    it('should not render label when not provided', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/content/i)).not.toBeInTheDocument();
    });

    it('should not render helper text when not provided', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/helper/i)).not.toBeInTheDocument();
    });
  });

  describe('error handling', () => {
    it('should display validation error', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        content: z.string().min(1, 'Content is required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRichText name="content" label="Content" required />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText('Content is required')).toBeInTheDocument();
      });
    });

    it('should display error with custom className', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        content: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRichText name="content" className="custom-richtext" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const editor = screen.getByRole('textbox');
        expect(editor).toHaveClass('form-richtext-container--error');
      });
    });

    it('should clear error when content is added', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        content: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRichText name="content" label="Content" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText('Required')).toBeInTheDocument();
      });

      const editor = screen.getByRole('textbox');
      await user.type(editor, 'Some content');

      await waitFor(() => {
        expect(screen.queryByText('Required')).not.toBeInTheDocument();
      });
    });

    it('should hide helper text when error is present', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        content: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRichText name="content" helperText="Write your content" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      expect(screen.getByText('Write your content')).toBeInTheDocument();

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.queryByText('Write your content')).not.toBeInTheDocument();
        expect(screen.getByText('Required')).toBeInTheDocument();
      });
    });
  });

  describe('accessibility', () => {
    it('should have correct ARIA attributes for required field', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" required />
        </TestFormWrapper>
      );

      const editor = screen.getByRole('textbox');
      expect(editor).toHaveAttribute('aria-required', 'true');
    });

    it('should have correct ARIA attributes for disabled field', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" disabled />
        </TestFormWrapper>
      );

      const editor = screen.getByRole('textbox');
      expect(editor).toHaveAttribute('aria-disabled', 'true');
    });

    it('should have correct ARIA attributes for invalid field', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        content: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRichText name="content" label="Content" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const editor = screen.getByRole('textbox');
        expect(editor).toHaveAttribute('aria-invalid', 'true');
      });
    });

    it('should have toolbar role', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('toolbar')).toBeInTheDocument();
    });

    it('should have textbox role for editor', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('textbox')).toBeInTheDocument();
    });

    it('should have aria-multiline attribute', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" label="Content" />
        </TestFormWrapper>
      );
      const editor = screen.getByRole('textbox');
      expect(editor).toHaveAttribute('aria-multiline', 'true');
    });

    it('should associate error message with editor', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        content: z.string().min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema}>
          <FormRichText name="content" label="Content" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const editor = screen.getByRole('textbox');
        const errorId = editor.getAttribute('aria-describedby');
        expect(errorId).toContain('error');
      });
    });

    it('should associate helper text with editor', () => {
      render(
        <TestFormWrapper>
          <FormRichText name="content" helperText="Helper text" />
        </TestFormWrapper>
      );

      const editor = screen.getByRole('textbox');
      const helperId = editor.getAttribute('aria-describedby');
      expect(helperId).toContain('helper');
    });
  });
});
