/**
 * FormRichText Component Unit Tests
 */

import { render, screen, fireEvent, waitFor } from '@test/test-utils';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi } from 'vitest';

import Form from '../Form';
import FormRichText from '../FormRichText';

// Test wrapper component
const TestFormWrapper = ({ children, defaultValues = {} }: { children: React.ReactNode; defaultValues?: Record<string, any> }) => {
  const form = useForm({ defaultValues });
  return (
    <Form form={form} onSubmit={vi.fn()}>{children}</Form>
  );
};

describe('FormRichText', () => {
  it('should render with label', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" />
      </TestFormWrapper>
    );
    
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('should render required indicator when required', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" required />
      </TestFormWrapper>
    );
    
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('should render helper text', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" helperText="Write your content" />
      </TestFormWrapper>
    );
    
    expect(screen.getByText('Write your content')).toBeInTheDocument();
  });

  it('should render editor', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" />
      </TestFormWrapper>
    );
    
    const editor = screen.getByRole('textbox');
    expect(editor).toBeInTheDocument();
  });

  it('should render default toolbar buttons', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" />
      </TestFormWrapper>
    );
    
    const toolbar = screen.getByRole('toolbar');
    expect(toolbar).toBeInTheDocument();
    
    // Default toolbar has 5 buttons: bold, italic, underline, link, list
    const buttons = toolbar.querySelectorAll('button');
    expect(buttons).toHaveLength(5);
  });

  it('should render custom toolbar', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" toolbar={['bold', 'italic']} />
      </TestFormWrapper>
    );
    
    const toolbar = screen.getByRole('toolbar');
    const buttons = toolbar.querySelectorAll('button');
    expect(buttons).toHaveLength(2);
  });

  it('should show character count by default', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" />
      </TestFormWrapper>
    );
    
    const charCount = document.querySelector('.form-richtext-charcount');
    expect(charCount).toBeInTheDocument();
    expect(charCount).toHaveTextContent('0');
  });

  it('should show character count with max length', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" maxLength={500} />
      </TestFormWrapper>
    );
    
    const charCount = document.querySelector('.form-richtext-charcount');
    expect(charCount).toHaveTextContent('0 / 500');
  });

  it('should update character count on input', async () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" />
      </TestFormWrapper>
    );
    
    const editor = screen.getByRole('textbox');
    
    fireEvent.input(editor, { 
      target: { innerHTML: '<p>Hello World</p>', innerText: 'Hello World' } 
    });
    
    await waitFor(() => {
      const charCount = document.querySelector('.form-richtext-charcount');
      expect(charCount).toHaveTextContent('11');
    });
  });

  it('should be disabled when disabled prop is true', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" disabled />
      </TestFormWrapper>
    );
    
    const editor = screen.getByRole('textbox');
    expect(editor).toHaveAttribute('contenteditable', 'false');
  });

  it('should have correct ARIA attributes', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" required />
      </TestFormWrapper>
    );
    
    const editor = screen.getByRole('textbox');
    expect(editor).toHaveAttribute('aria-required', 'true');
    expect(editor).toHaveAttribute('aria-invalid', 'false');
    expect(editor).toHaveAttribute('aria-multiline', 'true');
  });

  it('should apply custom className', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" className="custom-class" />
      </TestFormWrapper>
    );
    
    const wrapper = document.querySelector('.custom-class');
    expect(wrapper).toBeInTheDocument();
  });

  it('should apply min and max height styles', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" minHeight={200} maxHeight={500} />
      </TestFormWrapper>
    );
    
    const editor = screen.getByRole('textbox');
    expect(editor).toHaveStyle({ minHeight: '200px', maxHeight: '500px' });
  });

  it('should execute bold command on toolbar click', () => {
    // Mock execCommand for jsdom
    document.execCommand = vi.fn();
    
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" />
      </TestFormWrapper>
    );
    
    const boldButton = screen.getByTitle('Bold (Ctrl+B)');
    fireEvent.click(boldButton);
    
    expect(document.execCommand).toHaveBeenCalledWith('bold', false, undefined);
    
    vi.restoreAllMocks();
  });

  it('should execute italic command on toolbar click', () => {
    // Mock execCommand for jsdom
    document.execCommand = vi.fn();
    
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" />
      </TestFormWrapper>
    );
    
    const italicButton = screen.getByTitle('Italic (Ctrl+I)');
    fireEvent.click(italicButton);
    
    expect(document.execCommand).toHaveBeenCalledWith('italic', false, undefined);
    
    vi.restoreAllMocks();
  });

  it('should execute underline command on toolbar click', () => {
    // Mock execCommand for jsdom
    document.execCommand = vi.fn();
    
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" />
      </TestFormWrapper>
    );
    
    const underlineButton = screen.getByTitle('Underline (Ctrl+U)');
    fireEvent.click(underlineButton);
    
    expect(document.execCommand).toHaveBeenCalledWith('underline', false, undefined);
    
    vi.restoreAllMocks();
  });

  it('should hide character count when showCharCount is false', () => {
    render(
      <TestFormWrapper>
        <FormRichText name="content" label="Content" showCharCount={false} />
      </TestFormWrapper>
    );
    
    const charCount = document.querySelector('.form-richtext-charcount');
    expect(charCount).not.toBeInTheDocument();
  });

  it('should show error state', () => {
    // Use a wrapper component to properly use hooks
    const ErrorTestWrapper = () => {
      const form = useForm({
        defaultValues: { content: '' },
        mode: 'onSubmit'
      });
      
      // Use useEffect to set error only once after mount
      React.useEffect(() => {
        form.setError('content', { type: 'required', message: 'Content is required' });
      }, [form]);
      
      return (
        <Form form={form} onSubmit={vi.fn()}>
          <FormRichText name="content" label="Content" />
        </Form>
      );
    };
    
    render(<ErrorTestWrapper />);
    
    expect(screen.getByRole('alert')).toHaveTextContent('Content is required');
  });
});
