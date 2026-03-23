/**
 * Modal + Form Close Confirmation Tests
 * 
 * Tests for Modal close confirmation with unsaved form data.
 */

import { zodResolver } from '@hookform/resolvers/zod';
import { render, screen, waitFor } from '@test/test-utils';
import userEvent from '@testing-library/user-event';
import React from 'react';
import { useForm } from 'react-hook-form';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { z } from 'zod';

import Form from '../Form/Form';
import FormInput from '../Form/FormInput';
import { Modal } from '../Modal/Modal';

vi.mock('@shared/constants/timeouts', () => ({ MODAL_ANIMATION_DELAY: 50 }));
vi.mock('@shared/constants/zIndices', () => ({ Z_INDICES: { MODAL: 1000 } }));

describe('Modal + Form Close Confirmation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const schema = z.object({ name: z.string().min(1) });

  it('should show confirmation dialog when closing modal with unsaved changes', async () => {
    const user = userEvent.setup();
    const onBeforeClose = vi.fn().mockResolvedValue(false);

    const TestComponent = () => {
      const form = useForm({ resolver: zodResolver(schema) });
      return (
        <Modal isOpen={true} onClose={() => {}} title="Test Form" onBeforeClose={onBeforeClose}>
          <Form form={form} onSubmit={() => {}}>
            <FormInput name="name" label="Name" />
          </Form>
        </Modal>
      );
    };

    render(<TestComponent />);

    await user.type(screen.getByLabelText('Name'), 'John');
    await user.click(screen.getByLabelText('关闭对话框'));

    expect(onBeforeClose).toHaveBeenCalled();
    expect(screen.getByText('确认关闭')).toBeInTheDocument();
  });

  it('should close modal when confirmed', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const onBeforeClose = vi.fn().mockResolvedValue(false);

    const TestComponent = () => {
      const form = useForm({ resolver: zodResolver(schema) });
      return (
        <Modal isOpen={true} onClose={onClose} title="Test Form" onBeforeClose={onBeforeClose}>
          <Form form={form} onSubmit={() => {}}>
            <FormInput name="name" label="Name" />
          </Form>
        </Modal>
      );
    };

    render(<TestComponent />);

    await user.type(screen.getByLabelText('Name'), 'John');
    await user.click(screen.getByLabelText('关闭对话框'));
    await user.click(screen.getByText('放弃修改'));

    await waitFor(() => {
      expect(onClose).toHaveBeenCalled();
    });
  });
});
