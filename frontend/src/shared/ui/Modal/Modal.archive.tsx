/**
 * Cyberpunk Lab Theme - Modal Component
 *
 * Glassmorphism modal with backdrop blur and slide-up animation
 * Optimized with React.memo, useCallback, and advanced-event-handler-refs pattern
 */

import React, { useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import './Modal.css';

type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';
type ModalVariant = 'default' | 'danger' | 'warning';

interface ModalProps {
  children: React.ReactNode;
  isOpen?: boolean;
  onClose?: () => void;
  title?: string;
  size?: ModalSize;
  variant?: ModalVariant;
  closable?: boolean;
  closeOnBackdrop?: boolean;
  closeOnEscape?: boolean;
  showFooter?: boolean;
  footerActions?: React.ReactNode;
  className?: string;
}

interface ModalSubComponentProps {
  children: React.ReactNode;
  className?: string;
}

const Modal = React.forwardRef<HTMLDivElement, ModalProps & React.HTMLAttributes<HTMLDivElement>>(({
  children,
  isOpen = false,
  onClose,
  title,
  size = 'md',
  variant = 'default',
  closable = true,
  closeOnBackdrop = true,
  closeOnEscape = true,
  showFooter = false,
  footerActions,
  className = '',
  ...props
}, ref) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousActiveElement = useRef<HTMLElement | null>(null);
  const onCloseRef = useRef(onClose);

  // advanced-event-handler-refs: Store onClose in ref to stabilize dependencies
  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  // Focus trap and body scroll lock
  useEffect(() => {
    if (isOpen) {
      previousActiveElement.current = document.activeElement as HTMLElement;
      modalRef.current?.focus();

      // Prevent body scroll
      document.body.style.overflow = 'hidden';
    } else {
      // Restore body scroll
      document.body.style.overflow = '';

      // Restore focus
      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // ESC key handler - optimized with useCallback
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && onCloseRef.current) {
        onCloseRef.current();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape]);

  // Backdrop click handler - stabilized with useCallback
  const handleBackdropClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (closeOnBackdrop && e.target === e.currentTarget && onCloseRef.current) {
      onCloseRef.current();
    }
  }, [closeOnBackdrop]);

  // Close button handler - stabilized
  const handleClose = useCallback(() => {
    if (onCloseRef.current) {
      onCloseRef.current();
    }
  }, []);

  if (!isOpen) return null;

  const modalContent = (
    <>
      {/* Backdrop */}
      <div
        className="cyber-modal-backdrop"
        onClick={handleBackdropClick}
        aria-hidden="true"
      />

      {/* Modal */}
      <div
        className="cyber-modal-overlay"
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
        ref={modalRef}
        tabIndex={-1}
      >
        <div
          className={[
            'cyber-modal',
            `cyber-modal--${size}`,
            `cyber-modal--${variant}`,
            className
          ].filter(Boolean).join(' ')}
          {...props}
        >
          {/* Header */}
          {(title || closable) && (
            <div className="cyber-modal__header">
              {title && (
                <h2 id="modal-title" className="cyber-modal__title">
                  {title}
                </h2>
              )}
              {closable && (
                <button
                  type="button"
                  className="cyber-modal__close"
                  onClick={handleClose}
                  aria-label="Close modal"
                >
                  <span aria-hidden="true">×</span>
                </button>
              )}
            </div>
          )}

          {/* Body */}
          <div className="cyber-modal__body">
            {children}
          </div>

          {/* Footer */}
          {showFooter && (
            <div className="cyber-modal__footer">
              {footerActions || (
                <>
                  <button
                    type="button"
                    className="cyber-button cyber-button--secondary"
                    onClick={handleClose}
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    className="cyber-button cyber-button--primary"
                  >
                    Confirm
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );

  return createPortal(modalContent, document.body);
});

Modal.displayName = 'Modal';

// Don't memoize Modal - isOpen changes frequently and Portal always re-renders
// Instead, optimize the sub-components
Modal.Header = React.memo(function ModalHeader({ children, className = '', ...props }: ModalSubComponentProps) {
  return <div className={['cyber-modal__header', className].filter(Boolean).join(' ')} {...props}>{children}</div>;
});

Modal.Body = React.memo(function ModalBody({ children, className = '', ...props }: ModalSubComponentProps) {
  return <div className={['cyber-modal__body', className].filter(Boolean).join(' ')} {...props}>{children}</div>;
});

Modal.Footer = React.memo(function ModalFooter({ children, className = '', ...props }: ModalSubComponentProps) {
  return <div className={['cyber-modal__footer', className].filter(Boolean).join(' ')} {...props}>{children}</div>;
});

Modal.Title = React.memo(function ModalTitle({ children, className = '', ...props }: ModalSubComponentProps) {
  return <h2 className={['cyber-modal__title', className].filter(Boolean).join(' ')} {...props}>{children}</h2>;
});

export type { ModalProps, ModalSubComponentProps, ModalSize, ModalVariant };
export default Modal;
