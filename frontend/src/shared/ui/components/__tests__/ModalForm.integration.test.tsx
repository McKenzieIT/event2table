/**
 * Modal + Form Integration Tests
 * 
 * Comprehensive integration tests for Modal and Form components
 * Testing real-world user workflows and component interactions
 * 
 * Test Scenarios:
 * 1. Form inside Modal
 * 2. Form validation in Modal
 * 3. Form submission in Modal
 * 4. Modal close confirmation with unsaved form data
 * 5. Form reset on Modal close
 * 6. Multiple forms in Modal
 * 7. Form with Modal lifecycle hooks
 * 8. Edge cases and error handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Modal } from '../Modal/Modal';
import Form from '../Form/Form';
import FormInput from '../Form/FormInput';
import FormSelect from '../Form/FormSelect';
import FormCheckbox from '../Form/FormCheckbox';

// Mock constants
vi.mock('@shared/constants/timeouts', () => ({
  MODAL_ANIMATION_DELAY: 50,
}));

vi.mock('@shared/constants/zIndices', () => ({
  Z_INDICES: {
    MODAL: 1000,
  },
}));

describe('Modal + Form Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
  });

  // ========== Basic Integration ==========

  describe('Form inside Modal', () => {
    it('should render form inside modal', () => {
      const form = useForm();
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByRole('form')).toBeInTheDocument();
      expect(screen.getByLabelText('Name')).toBeInTheDocument();
    });

    it('should allow typing in form fields inside modal', async () => {
      const user = userEvent.setup();
      const form = useForm();
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      const input = screen.getByLabelText('Name');
      await user.type(input, 'John Doe');

      expect(input).toHaveValue('John Doe');
    });

    it('should submit form inside modal', async () => {
      const user = userEvent.setup();
      const form = useForm({ defaultValues: { name: 'John' } });
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      await user.click(screen.getByRole('button', { name: 'Submit' }));

      expect(onSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'John',
        })
      );
    });

    it('should not close modal when form is submitted', async () => {
      const user = userEvent.setup();
      const form = useForm({ defaultValues: { name: 'John' } });
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      await user.click(screen.getByRole('button', { name: 'Submit' }));

      expect(onSubmit).toHaveBeenCalled();
      expect(onClose).not.toHaveBeenCalled();
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });
  });

  // ========== Form Validation in Modal ==========

  describe('Form Validation in Modal', () => {
    const schema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
    });

    it('should show validation errors in modal', async () => {
      const user = userEvent.setup();
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
      });
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <FormInput name="email" label="Email" type="email" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Submit empty form
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
        expect(screen.getByText('Invalid email')).toBeInTheDocument();
      });
    });

    it('should clear errors when valid input is provided', async () => {
      const user = userEvent.setup();
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
      });
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <FormInput name="email" label="Email" type="email" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Submit empty form to show errors
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
      });

      // Provide valid input
      await user.type(screen.getByLabelText('Name'), 'John');

      await waitFor(() => {
        expect(screen.queryByText('Name is required')).not.toBeInTheDocument();
      });
    });

    it('should prevent form submission with invalid data', async () => {
      const user = userEvent.setup();
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
      });
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <FormInput name="email" label="Email" type="email" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Submit empty form
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      expect(onSubmit).not.toHaveBeenCalled();
    });
  });

  // ========== Modal Close Confirmation ==========

  describe('Modal Close Confirmation with Unsaved Data', () => {
    const schema = z.object({
      name: z.string().min(1),
    });

    it('should show confirmation dialog when closing modal with unsaved changes', async () => {
      const user = userEvent.setup();
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
      });
      const onSubmit = vi.fn();
      const onClose = vi.fn();
      const onBeforeClose = vi.fn().mockResolvedValue(false);

      render(
        <Modal
          isOpen={true}
          onClose={onClose}
          title="Test Form"
          onBeforeClose={onBeforeClose}
        >
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Type in form
      await user.type(screen.getByLabelText('Name'), 'John');

      // Try to close modal
      await user.click(screen.getByLabelText('关闭对话框'));

      expect(onBeforeClose).toHaveBeenCalled();
      expect(screen.getByText('确认关闭')).toBeInTheDocument();
      expect(onClose).not.toHaveBeenCalled();
    });

    it('should close modal when confirmed', async () => {
      const user = userEvent.setup();
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
      });
      const onSubmit = vi.fn();
      const onClose = vi.fn();
      const onBeforeClose = vi.fn().mockResolvedValue(false);

      render(
        <Modal
          isOpen={true}
          onClose={onClose}
          title="Test Form"
          onBeforeClose={onBeforeClose}
        >
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Type in form
      await user.type(screen.getByLabelText('Name'), 'John');

      // Try to close modal
      await user.click(screen.getByLabelText('关闭对话框'));

      // Confirm
      await user.click(screen.getByText('放弃修改'));

      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      });
    });

    it('should not close modal when cancelled', async () => {
      const user = userEvent.setup();
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
      });
      const onSubmit = vi.fn();
      const onClose = vi.fn();
      const onBeforeClose = vi.fn().mockResolvedValue(false);

      render(
        <Modal
          isOpen={true}
          onClose={onClose}
          title="Test Form"
          onBeforeClose={onBeforeClose}
        >
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Type in form
      await user.type(screen.getByLabelText('Name'), 'John');

      // Try to close modal
      await user.click(screen.getByLabelText('关闭对话框'));

      // Cancel
      await user.click(screen.getByText('继续编辑'));

      expect(onClose).not.toHaveBeenCalled();
      expect(screen.getByRole('dialog')).toBeInTheDocument();
    });

    it('should close modal immediately when no unsaved changes', async () => {
      const user = userEvent.setup();
      const form = useForm({
        resolver: zodResolver(schema),
        mode: 'onBlur',
      });
      const onSubmit = vi.fn();
      const onClose = vi.fn();
      const onBeforeClose = vi.fn().mockResolvedValue(true);

      render(
        <Modal
          isOpen={true}
          onClose={onClose}
          title="Test Form"
          onBeforeClose={onBeforeClose}
        >
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Close modal without typing
      await user.click(screen.getByLabelText('关闭对话框'));

      expect(onBeforeClose).toHaveBeenCalled();
      await waitFor(() => {
        expect(onClose).toHaveBeenCalled();
      });
    });
  });

  // ========== Form Reset on Modal Close ==========

  describe('Form Reset on Modal Close', () => {
    it('should reset form when modal closes and reopens', async () => {
      const user = userEvent.setup();
      const form = useForm();
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      const TestComponent = () => {
        const [isOpen, setIsOpen] = React.useState(true);
        const formInstance = useForm();

        return (
          <>
            <Modal isOpen={isOpen} onClose={() => setIsOpen(false)} title="Test Form">
              <Form form={formInstance} onSubmit={onSubmit}>
                <FormInput name="name" label="Name" />
                <button type="submit">Submit</button>
              </Form>
            </Modal>
            <button onClick={() => setIsOpen(true)}>Open Modal</button>
          </>
        );
      };

      render(<TestComponent />);

      // Type in form
      await user.type(screen.getByLabelText('Name'), 'John');

      // Close modal
      await user.click(screen.getByLabelText('关闭对话框'));

      await waitFor(() => {
        expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
      });

      // Reopen modal
      await user.click(screen.getByText('Open Modal'));

      expect(screen.getByLabelText('Name')).toHaveValue('');
    });

    it('should reset form after successful submission', async () => {
      const user = userEvent.setup();
      const form = useForm({ defaultValues: { name: '' } });
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit} resetAfterSubmit={true}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Type in form
      await user.type(screen.getByLabelText('Name'), 'John');

      // Submit form
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByLabelText('Name')).toHaveValue('');
      });
    });
  });

  // ========== Complex Form Scenarios ==========

  describe('Complex Form Scenarios', () => {
    const complexSchema = z.object({
      name: z.string().min(1, 'Name is required'),
      email: z.string().email('Invalid email'),
      role: z.string().min(1, 'Role is required'),
      agree: z.boolean().refine((val) => val === true, 'You must agree'),
    });

    it('should handle complex form with multiple field types', async () => {
      const user = userEvent.setup();
      const form = useForm({
        resolver: zodResolver(complexSchema),
        mode: 'onBlur',
      });
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="User Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <FormInput name="email" label="Email" type="email" />
            <FormSelect
              name="role"
              label="Role"
              options={[
                { value: 'admin', label: 'Admin' },
                { value: 'user', label: 'User' },
              ]}
            />
            <FormCheckbox name="agree" label="I agree to the terms" required />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Fill form
      await user.type(screen.getByLabelText('Name'), 'John Doe');
      await user.type(screen.getByLabelText('Email'), 'john@example.com');
      await user.selectOptions(screen.getByLabelText('Role'), 'admin');
      await user.click(screen.getByLabelText('I agree to the terms'));

      // Submit
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith(
          expect.objectContaining({
            name: 'John Doe',
            email: 'john@example.com',
            role: 'admin',
            agree: true,
          })
        );
      });
    });

    it('should show all validation errors for complex form', async () => {
      const user = userEvent.setup();
      const form = useForm({
        resolver: zodResolver(complexSchema),
        mode: 'onBlur',
      });
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="User Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <FormInput name="email" label="Email" type="email" />
            <FormSelect
              name="role"
              label="Role"
              options={[
                { value: 'admin', label: 'Admin' },
                { value: 'user', label: 'User' },
              ]}
            />
            <FormCheckbox name="agree" label="I agree to the terms" required />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Submit empty form
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
        expect(screen.getByText('Invalid email')).toBeInTheDocument();
        expect(screen.getByText('Role is required')).toBeInTheDocument();
        expect(screen.getByText('You must agree')).toBeInTheDocument();
      });
    });
  });

  // ========== Modal Lifecycle with Form ==========

  describe('Modal Lifecycle with Form', () => {
    it('should call onAfterOpen when modal with form opens', () => {
      const form = useForm();
      const onSubmit = vi.fn();
      const onClose = vi.fn();
      const onAfterOpen = vi.fn();

      render(
        <Modal
          isOpen={true}
          onClose={onClose}
          title="Test Form"
          onAfterOpen={onAfterOpen}
        >
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      expect(onAfterOpen).toHaveBeenCalled();
    });

    it('should call onAfterClose when modal with form closes', async () => {
      const user = userEvent.setup();
      const form = useForm();
      const onSubmit = vi.fn();
      const onClose = vi.fn();
      const onAfterClose = vi.fn();

      render(
        <Modal
          isOpen={true}
          onClose={onClose}
          title="Test Form"
          onAfterClose={onAfterClose}
        >
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      await user.click(screen.getByLabelText('关闭对话框'));

      await waitFor(() => {
        expect(onAfterClose).toHaveBeenCalled();
      });
    });
  });

  // ========== Edge Cases ==========

  describe('Edge Cases', () => {
    it('should handle form submission while modal is closing', async () => {
      const user = userEvent.setup();
      const form = useForm({ defaultValues: { name: 'John' } });
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      // Click submit and close button rapidly
      await user.click(screen.getByRole('button', { name: 'Submit' }));
      await user.click(screen.getByLabelText('关闭对话框'));

      expect(onSubmit).toHaveBeenCalled();
    });

    it('should handle form without schema in modal', async () => {
      const user = userEvent.setup();
      const form = useForm();
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );

      await user.type(screen.getByLabelText('Name'), 'John');
      await user.click(screen.getByRole('button', { name: 'Submit' }));

      expect(onSubmit).toHaveBeenCalled();
    });

    it('should handle disabled form in modal', () => {
      const form = useForm();
      const onSubmit = vi.fn();
      const onClose = vi.fn();

      render(
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" disabled />
            <button type="submit" disabled>Submit</button>
          </Form>
        </Modal>
      );

      expect(screen.getByLabelText('Name')).toBeDisabled();
      expect(screen.getByRole('button', { name: 'Submit' })).toBeDisabled();
    });
  });
});
