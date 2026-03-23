/**
 * FormUpload Component - Test Suite
 * 
 * Comprehensive tests for FormUpload component including:
 * - Rendering behavior
 * - User interactions
 * - File validation
 * - Edge cases and accessibility
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { render, screen, waitFor, fireEvent } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { z } from 'zod';

import Form from './Form';
import FormUpload from './FormUpload';

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

// Mock file
const createMockFile = (name: string, size: number, type: string) => {
  const file = new File([''], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

describe('FormUpload Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock URL.createObjectURL and URL.revokeObjectURL
    global.URL.createObjectURL = vi.fn(() => 'mock-url');
    global.URL.revokeObjectURL = vi.fn();
  });

  describe('rendering', () => {
    it('should render upload dropzone', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" label="Upload Documents" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('button', { name: /drag and drop/i })).toBeInTheDocument();
    });

    it('should render label', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" label="Upload Documents" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Upload Documents')).toBeInTheDocument();
    });

    it('should render upload button', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" />
        </TestFormWrapper>
      );
      // The dropzone itself contains the button text
      expect(screen.getByText(/choose files/i)).toBeInTheDocument();
    });

    it('should render helper text when provided', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" helperText="Upload PDF or DOC files" />
        </TestFormWrapper>
      );
      expect(screen.getByText('Upload PDF or DOC files')).toBeInTheDocument();
    });

    it('should render required indicator when required is true', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" label="Upload Documents" required />
        </TestFormWrapper>
      );
      expect(screen.getByText('*')).toBeInTheDocument();
    });

    it('should apply custom className', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" className="custom-upload" />
        </TestFormWrapper>
      );
      const wrapper = screen.getByRole('button', { name: /drag and drop/i }).closest('.form-field-wrapper');
      expect(wrapper).toHaveClass('custom-upload');
    });
  });

  describe('interactions', () => {
    it('should handle file selection via click', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormUpload name="documents" />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      const fileInput = dropzone.querySelector('input[type="file"]') as HTMLInputElement;

      const file = createMockFile('test.pdf', 1024, 'application/pdf');
      await user.upload(fileInput, file);

      // Verify file is displayed in the list
      await waitFor(() => {
        expect(screen.getByText('test.pdf')).toBeInTheDocument();
      });
    });

    it('should handle drag enter event', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormUpload name="documents" />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      
      // Simulate drag enter
      await fireEvent.dragEnter(dropzone);

      expect(dropzone).toHaveClass('form-upload-dropzone--dragging');
    });

    it('should handle keyboard navigation', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormUpload name="documents" />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      dropzone.focus();
      expect(dropzone).toHaveFocus();

      await user.keyboard('{Enter}');
      const fileInput = dropzone.querySelector('input[type="file"]') as HTMLInputElement;
      expect(fileInput).toBeInTheDocument();
    });

    it('should display file list after upload', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormUpload name="documents" />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      const fileInput = dropzone.querySelector('input[type="file"]') as HTMLInputElement;

      const file = createMockFile('test.pdf', 1024, 'application/pdf');
      await user.upload(fileInput, file);

      await waitFor(() => {
        expect(screen.getByText('test.pdf')).toBeInTheDocument();
      });
    });

    it('should remove file when remove button is clicked', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormUpload name="documents" />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      const fileInput = dropzone.querySelector('input[type="file"]') as HTMLInputElement;

      const file = createMockFile('test.pdf', 1024, 'application/pdf');
      await user.upload(fileInput, file);

      await waitFor(() => {
        expect(screen.getByText('test.pdf')).toBeInTheDocument();
      });

      const removeButton = screen.getByRole('button', { name: /remove test.pdf/i });
      await user.click(removeButton);

      await waitFor(() => {
        expect(screen.queryByText('test.pdf')).not.toBeInTheDocument();
      });
    });
  });

  describe('edge cases', () => {
    it('should be disabled when disabled is true', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" disabled />
        </TestFormWrapper>
      );
      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      expect(dropzone).toHaveAttribute('aria-disabled', 'true');
    });

    it('should handle empty file list', () => {
      render(
        <TestFormWrapper defaultValues={{ documents: [] }}>
          <FormUpload name="documents" />
        </TestFormWrapper>
      );
      expect(screen.queryByRole('list')).not.toBeInTheDocument();
    });

    it('should handle multiple file upload', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormUpload name="documents" multiple />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      const fileInput = dropzone.querySelector('input[type="file"]') as HTMLInputElement;

      const file1 = createMockFile('test1.pdf', 1024, 'application/pdf');
      const file2 = createMockFile('test2.pdf', 2048, 'application/pdf');
      await user.upload(fileInput, [file1, file2]);

      await waitFor(() => {
        expect(screen.getByText('test1.pdf')).toBeInTheDocument();
        expect(screen.getByText('test2.pdf')).toBeInTheDocument();
      });
    });

    it('should validate file size', async () => {
      const user = userEvent.setup();
      const alertMock = vi.fn();
      global.alert = alertMock;

      render(
        <TestFormWrapper>
          <FormUpload name="documents" maxSize={1024} />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      const fileInput = dropzone.querySelector('input[type="file"]') as HTMLInputElement;

      const file = createMockFile('large.pdf', 2048, 'application/pdf');
      await user.upload(fileInput, file);

      expect(alertMock).toHaveBeenCalledWith(expect.stringContaining('exceeds maximum size'));
    });

    it('should validate file type', async () => {
      const user = userEvent.setup();
      const alertMock = vi.fn();
      global.alert = alertMock;

      render(
        <TestFormWrapper>
          <FormUpload name="documents" accept=".pdf,.doc" />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      
      // Create a file with .exe extension which is not in the accept list
      const file = createMockFile('test.exe', 1024, 'application/octet-stream');
      
      // Simulate drop event which bypasses the browser's accept filter
      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file],
        },
      });

      // The alert should be called synchronously
      expect(alertMock).toHaveBeenCalled();
      
      // Verify the file was not added to the list
      expect(screen.queryByText('test.exe')).not.toBeInTheDocument();
    });

    it('should not render label when not provided', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/upload/i)).not.toBeInTheDocument();
    });

    it('should not render helper text when not provided', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" label="Upload" />
        </TestFormWrapper>
      );
      expect(screen.queryByText(/helper/i)).not.toBeInTheDocument();
    });
  });

  describe('error handling', () => {
    it('should display validation error', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        documents: z.array(z.any()).min(1, 'Please upload at least one document'),
      });

      render(
        <TestFormWrapper schema={schema} mode="onSubmit">
          <FormUpload name="documents" label="Upload Documents" required />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText('Please upload at least one document')).toBeInTheDocument();
      });
    });

    it('should display error with custom className', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        documents: z.array(z.any()).min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema} mode="onSubmit">
          <FormUpload name="documents" className="custom-upload" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const dropzone = screen.getByRole('button', { name: /drag and drop/i });
        expect(dropzone).toHaveClass('form-upload-dropzone--error');
      });
    });

    it('should clear error when file is uploaded', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        documents: z.array(z.any()).min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema} mode="onSubmit">
          <FormUpload name="documents" label="Upload Documents" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.getByText('Required')).toBeInTheDocument();
      });

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      const fileInput = dropzone.querySelector('input[type="file"]') as HTMLInputElement;

      const file = createMockFile('test.pdf', 1024, 'application/pdf');
      await user.upload(fileInput, file);

      // Wait for file to be displayed
      await waitFor(() => {
        expect(screen.getByText('test.pdf')).toBeInTheDocument();
      });

      // Submit again to trigger validation
      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.queryByText('Required')).not.toBeInTheDocument();
      });
    });

    it('should hide helper text when error is present', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        documents: z.array(z.any()).min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema} mode="onSubmit">
          <FormUpload name="documents" helperText="Upload PDF files" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      expect(screen.getByText('Upload PDF files')).toBeInTheDocument();

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        expect(screen.queryByText('Upload PDF files')).not.toBeInTheDocument();
        expect(screen.getByText('Required')).toBeInTheDocument();
      });
    });
  });

  describe('accessibility', () => {
    it('should have correct ARIA attributes for required field', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" label="Upload Documents" required />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      expect(dropzone).toHaveAttribute('aria-required', 'true');
    });

    it('should have correct ARIA attributes for disabled field', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" label="Upload Documents" disabled />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      expect(dropzone).toHaveAttribute('aria-disabled', 'true');
    });

    it('should have correct ARIA attributes for invalid field', async () => {
      const user = userEvent.setup();
      const schema = z.object({
        documents: z.array(z.any()).min(1, 'Required'),
      });

      render(
        <TestFormWrapper schema={schema} mode="onSubmit">
          <FormUpload name="documents" label="Upload Documents" />
          <button type="submit">Submit</button>
        </TestFormWrapper>
      );

      await user.click(screen.getByRole('button', { name: /submit/i }));

      await waitFor(() => {
        const dropzone = screen.getByRole('button', { name: /drag and drop/i });
        expect(dropzone).toHaveAttribute('aria-invalid', 'true');
      });
    });

    it('should have button role for dropzone', () => {
      render(
        <TestFormWrapper>
          <FormUpload name="documents" />
        </TestFormWrapper>
      );
      expect(screen.getByRole('button', { name: /drag and drop/i })).toBeInTheDocument();
    });

    it('should have correct aria-label for remove button', async () => {
      const user = userEvent.setup();
      render(
        <TestFormWrapper>
          <FormUpload name="documents" />
        </TestFormWrapper>
      );

      const dropzone = screen.getByRole('button', { name: /drag and drop/i });
      const fileInput = dropzone.querySelector('input[type="file"]') as HTMLInputElement;

      const file = createMockFile('test.pdf', 1024, 'application/pdf');
      await user.upload(fileInput, file);

      await waitFor(() => {
        const removeButton = screen.getByRole('button', { name: /remove test.pdf/i });
        expect(removeButton).toBeInTheDocument();
      });
    });
  });
});
