import { render, screen } from '@test/test-utils';

import { Modal } from '../Modal';

import { BaseModal } from '@/shared/ui';

describe('Modal Migration', () => {
  it('BaseModal should be an alias for Modal', () => {
    expect(BaseModal).toBe(Modal);
  });

  it('Modal should render with all BaseModal props', () => {
    render(
      <Modal
        isOpen={true}
        onClose={() => {}}
        title="Test Modal"
        size="medium"
        animation="slideUp"
      >
        Content
      </Modal>
    );
    
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });
});
