import React, { useState, useCallback } from 'react';
import { Button, Modal } from '@shared/ui';

const ModalShowcase: React.FC = () => {
  const [modalOpen, setModalOpen] = useState(false);

  const handleOpenModal = useCallback(() => {
    setModalOpen(true);
  }, []);

  const handleCloseModal = useCallback(() => {
    setModalOpen(false);
  }, []);

  return (
    <>
      <section className="showcase-section">
        <h2 className="section-title">Modal</h2>
        <div className="showcase-row">
          <Button variant="primary" onClick={handleOpenModal}>
            Open Modal
          </Button>
          <Button variant="danger" onClick={handleOpenModal}>
            Delete Confirmation
          </Button>
        </div>
      </section>

      <Modal
        isOpen={modalOpen}
        onClose={handleCloseModal}
        title="Confirm Action"
        animation="slideUp"
        glassmorphism
        size="md"
      >
        <p style={{ marginBottom: '16px' }}>
          This is a modal dialog with glassmorphism effect and backdrop blur.
        </p>
        <p>
          Modals support different sizes (sm, md, lg, xl, full) and variants (default, danger, warning).
        </p>
      </Modal>
    </>
  );
};

export default ModalShowcase;
