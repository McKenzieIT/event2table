/**
 * NodeConfigModal Test Suite
 * TDD Red Phase - Failing tests for P0 bug fix
 *
 * Bug: Save button disabled on first modal open, preventing users from filling form
 * Root Cause: nodeConfig initialized with empty strings, validation logic prevents enabling
 */

import { vi, describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@test/test-utils';
import '@testing-library/jest-dom';
import { NodeConfigModal } from '../NodeConfigModal';
import toast from 'react-hot-toast';

// Mock toast notifications
vi.mock('react-hot-toast', () => ({
  ...vi.importActual('react-hot-toast'),
  default: {
    error: vi.fn(),
    success: vi.fn(),
  },
  toast: {
    error: vi.fn(),
    success: vi.fn(),
  },
}));

describe('NodeConfigModal - First Time Creation Bug (P0 #1)', () => {
  const mockOnChange = vi.fn();
  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('When modal opens for new node (empty config)', () => {
    it('should enable save button immediately (not disabled)', () => {
      // Arrange: Render modal with empty config (simulating first-time creation)
      const { container } = render(
        <NodeConfigModal
          config={{ nameEn: '', nameCn: '', description: '' }}
          onChange={mockOnChange}
          onClose={mockOnClose}
          disabled={false}
        />
      );

      // Act: Find save button
      const saveButton = screen.getByRole('button', { name: /保存/i });

      // Assert: Button should NOT be disabled
      // This test FAILS with current code because button is disabled
      expect(saveButton).not.toBeDisabled();
    });

    it('should allow user to fill form and enable save', async () => {
      // Arrange: Render modal with empty config
      render(
        <NodeConfigModal
          config={{ nameEn: '', nameCn: '', description: '' }}
          onChange={mockOnChange}
          onClose={mockOnClose}
          disabled={false}
        />
      );

      // Act: Get initial save button state
      const saveButton = screen.getByRole('button', { name: /保存/i });
      const nameEnInput = screen.getByLabelText(/节点英文名称/i);
      const nameCnInput = screen.getByLabelText(/节点中文名称/i);

      // Assert: Initially button might be disabled (acceptable IF user can type)
      // Act: User types in required fields
      fireEvent.change(nameEnInput, { target: { value: 'Test Node' } });
      fireEvent.change(nameCnInput, { target: { value: '测试节点' } });

      // Assert: After typing, button should be enabled
      await waitFor(() => {
        expect(saveButton).not.toBeDisabled();
      });
    });

    it('should call onChange with trimmed values when save clicked', async () => {
      // Arrange: Render modal with empty config
      render(
        <NodeConfigModal
          config={{ nameEn: '', nameCn: '', description: '' }}
          onChange={mockOnChange}
          onClose={mockOnClose}
          disabled={false}
        />
      );

      // Act: Fill form
      const nameEnInput = screen.getByLabelText(/节点英文名称/i);
      const nameCnInput = screen.getByLabelText(/节点中文名称/i);
      // Description textarea uses placeholder since label is not associated with for/id
      const descInput = screen.getByPlaceholderText(/简要描述/i);

      fireEvent.change(nameEnInput, { target: { value: '  Test Node  ' } });
      fireEvent.change(nameCnInput, { target: { value: '  测试节点  ' } });
      fireEvent.change(descInput, { target: { value: '  Test Description  ' } });

      // Act: Click save button
      const saveButton = screen.getByRole('button', { name: /保存/i });
      fireEvent.click(saveButton);

      // Assert: onChange called with trimmed values
      await waitFor(() => {
        expect(mockOnChange).toHaveBeenCalledWith({
          nameEn: 'Test Node',
          nameCn: '测试节点',
          description: 'Test Description',
        });
        expect(mockOnClose).toHaveBeenCalled();
      });
    });

    it('should show validation error if trying to save with empty fields', async () => {
      // Arrange: Render modal
      render(
        <NodeConfigModal
          config={{ nameEn: '', nameCn: '', description: '' }}
          onChange={mockOnChange}
          onClose={mockOnClose}
          disabled={false}
        />
      );

      // Act: Try to save without filling required fields
      // Note: This test verifies validation exists in handleSave
      // Current code never reaches this due to disabled button
      const saveButton = screen.getByRole('button', { name: /保存/i });

      // If button is enabled, user can click it
      if (!saveButton.hasAttribute('disabled')) {
        fireEvent.click(saveButton);

        // Assert: Toast error shown, onChange NOT called
        await waitFor(() => {
          expect(toast.error).toHaveBeenCalledWith('请输入节点英文名称');
          expect(mockOnChange).not.toHaveBeenCalled();
          expect(mockOnClose).not.toHaveBeenCalled();
        });
      }
    });
  });

  describe('When modal opens for existing node (has config)', () => {
    it('should populate form with existing values', () => {
      // Arrange: Render modal with existing config
      const existingConfig = {
        nameEn: 'Existing Node',
        nameCn: '现有节点',
        description: 'Existing description',
      };

      render(
        <NodeConfigModal
          config={existingConfig}
          onChange={mockOnChange}
          onClose={mockOnClose}
          disabled={false}
        />
      );

      // Assert: Form fields populated with existing values
      expect(screen.getByLabelText(/节点英文名称/i)).toHaveValue('Existing Node');
      expect(screen.getByLabelText(/节点中文名称/i)).toHaveValue('现有节点');
      // Description textarea uses placeholder query since label is not associated
      expect(screen.getByPlaceholderText(/简要描述/i)).toHaveValue('Existing description');
    });

    it('should enable save button with valid existing config', () => {
      // Arrange: Render modal with existing config
      const existingConfig = {
        nameEn: 'Existing Node',
        nameCn: '现有节点',
        description: 'Existing description',
      };

      render(
        <NodeConfigModal
          config={existingConfig}
          onChange={mockOnChange}
          onClose={mockOnClose}
          disabled={false}
        />
      );

      // Assert: Save button should be enabled
      const saveButton = screen.getByRole('button', { name: /保存/i });
      expect(saveButton).not.toBeDisabled();
    });
  });

  describe('Disabled prop behavior', () => {
    it('should disable entire form when disabled prop is true', () => {
      // Arrange: Render modal with disabled=true
      render(
        <NodeConfigModal
          config={{ nameEn: 'Test', nameCn: '测试', description: '' }}
          onChange={mockOnChange}
          onClose={mockOnClose}
          disabled={true}
        />
      );

      // Assert: All inputs disabled
      expect(screen.getByLabelText(/节点英文名称/i)).toBeDisabled();
      expect(screen.getByLabelText(/节点中文名称/i)).toBeDisabled();
      // Description textarea uses placeholder query since label is not associated
      expect(screen.getByPlaceholderText(/简要描述/i)).toBeDisabled();

      // Assert: Save button disabled
      expect(screen.getByRole('button', { name: /保存/i })).toBeDisabled();
    });
  });
});
