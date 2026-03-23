/**
 * Modal + Form Basic Integration Tests
 * 
 * Tests for basic Modal and Form integration.
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

describe('Modal + Form Basic', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
  });

  it('should render form inside modal', () => {
    const onSubmit = vi.fn();
    const onClose = vi.fn();

    const TestComponent = () => {
      const form = useForm();
      return (
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );
    };

    render(<TestComponent />);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByLabelText('Name')).toBeInTheDocument();
  });

  it('should submit form inside modal', async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    const onClose = vi.fn();

    const TestComponent = () => {
      const form = useForm({ defaultValues: { name: 'John' } });
      return (
        <Modal isOpen={true} onClose={onClose} title="Test Form">
          <Form form={form} onSubmit={onSubmit}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );
    };

    render(<TestComponent />);

    await user.click(screen.getByRole('button', { name: 'Submit' }));

    expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ name: 'John' }));
  });

  it('should show validation errors in modal', async () => {
    const user = userEvent.setup();
    const schema = z.object({ name: z.string().min(1, 'Name is required') });

    const TestComponent = () => {
      const form = useForm({ resolver: zodResolver(schema) });
      return (
        <Modal isOpen={true} onClose={() => {}} title="Test Form">
          <Form form={form} onSubmit={() => {}}>
            <FormInput name="name" label="Name" />
            <button type="submit">Submit</button>
          </Form>
        </Modal>
      );
    };

    render(<TestComponent />);

    await user.click(screen.getByRole('button', { name: 'Submit' }));

    await waitFor(() => {
      expect(screen.getByText('Name is required')).toBeInTheDocument();
    });
  });
});
