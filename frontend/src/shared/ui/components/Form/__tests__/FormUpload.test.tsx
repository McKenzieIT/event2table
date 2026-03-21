/**
 * FormUpload Component Unit Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useForm } from 'react-hook-form';
import FormUpload from '../FormUpload';
import Form from '../Form';

// Test wrapper component
const TestFormWrapper = ({ children, defaultValues = {} }: { children: React.ReactNode; defaultValues?: Record<string, any> }) => {
  const form = useForm({ defaultValues });
  return (
    <Form form={form} onSubmit={vi.fn()}>{children}</Form>
  );
};

// Mock File
const createFile = (name: string, size: number = 1024, type: string = 'image/png'): File => {
  const file = new File(['x'.repeat(size)], name, { type });
  return file;
};

describe('FormUpload', () => {
  it('should render with label', () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" />
      </TestFormWrapper>
    );
    
    expect(screen.getByText('Upload Files')).toBeInTheDocument();
  });

  it('should render required indicator when required', () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" required />
      </TestFormWrapper>
    );
    
    expect(screen.getByText('*')).toBeInTheDocument();
  });

  it('should render helper text', () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" helperText="Max 5 files" />
      </TestFormWrapper>
    );
    
    expect(screen.getByText('Max 5 files')).toBeInTheDocument();
  });

  it('should render dropzone', () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" />
      </TestFormWrapper>
    );
    
    const dropzone = document.querySelector('.form-upload-dropzone');
    expect(dropzone).toBeInTheDocument();
  });

  it('should render upload button', () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" buttonText="Select Files" />
      </TestFormWrapper>
    );
    
    expect(screen.getByText('Select Files')).toBeInTheDocument();
  });

  it('should show max file size hint', () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" maxSize={1048576} />
      </TestFormWrapper>
    );
    
    expect(screen.getByText(/Max file size:/)).toBeInTheDocument();
  });

  it('should show max files hint when multiple', () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" multiple maxFiles={5} />
      </TestFormWrapper>
    );
    
    expect(screen.getByText(/Max files: 5/)).toBeInTheDocument();
  });

  it('should be disabled when disabled prop is true', () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" disabled />
      </TestFormWrapper>
    );
    
    const dropzone = document.querySelector('.form-upload-dropzone');
    expect(dropzone).toHaveAttribute('aria-disabled', 'true');
  });

  it('should handle file selection', async () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = createFile('test.png', 1024, 'image/png');
    
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: true
    });
    
    fireEvent.change(input);
    
    await waitFor(() => {
      expect(screen.getByText('test.png')).toBeInTheDocument();
    });
  });

  it('should show file preview for images', async () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" showPreview />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = createFile('test.png', 1024, 'image/png');
    
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: true
    });
    
    fireEvent.change(input);
    
    await waitFor(() => {
      const preview = document.querySelector('.form-upload-preview');
      expect(preview).toBeInTheDocument();
    });
  });

  it('should show file size', async () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = createFile('test.png', 2048, 'image/png');
    
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: true
    });
    
    fireEvent.change(input);
    
    await waitFor(() => {
      expect(screen.getByText('2 KB')).toBeInTheDocument();
    });
  });

  it('should allow file removal', async () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = createFile('test.png', 1024, 'image/png');
    
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: true
    });
    
    fireEvent.change(input);
    
    await waitFor(() => {
      expect(screen.getByText('test.png')).toBeInTheDocument();
    });
    
    const removeButton = document.querySelector('.form-upload-remove');
    fireEvent.click(removeButton!);
    
    await waitFor(() => {
      expect(screen.queryByText('test.png')).not.toBeInTheDocument();
    });
  });

  it('should validate file size', async () => {
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
    
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" maxSize={100} />
      </TestFormWrapper>
    );
    
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = createFile('large.png', 1000, 'image/png');
    
    Object.defineProperty(input, 'files', {
      value: [file],
      writable: true
    });
    
    fireEvent.change(input);
    
    await waitFor(() => {
      expect(alertSpy).toHaveBeenCalled();
    });
    
    alertSpy.mockRestore();
  });

  it('should handle drag and drop', async () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" enableDragDrop />
      </TestFormWrapper>
    );
    
    const dropzone = document.querySelector('.form-upload-dropzone');
    
    fireEvent.dragEnter(dropzone!);
    expect(dropzone).toHaveClass('form-upload-dropzone--dragging');
    
    fireEvent.dragLeave(dropzone!);
    expect(dropzone).not.toHaveClass('form-upload-dropzone--dragging');
  });

  it('should have correct ARIA attributes', () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" required />
      </TestFormWrapper>
    );
    
    const dropzone = document.querySelector('.form-upload-dropzone');
    expect(dropzone).toHaveAttribute('aria-required', 'true');
    expect(dropzone).toHaveAttribute('aria-invalid', 'false');
  });

  it('should apply custom className', () => {
    render(
      <TestFormWrapper>
        <FormUpload name="files" label="Upload Files" className="custom-class" />
      </TestFormWrapper>
    );
    
    const wrapper = document.querySelector('.custom-class');
    expect(wrapper).toBeInTheDocument();
  });
});
