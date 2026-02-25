import React, { useState, useEffect, createContext, useContext } from 'react';
import { ConfirmDialog } from '../ConfirmDialog/ConfirmDialog';

const ConfirmContext = createContext(null);

export function ConfirmProvider({ children }) {
  const [dialog, setDialog] = useState({
    open: false,
    title: '确认',
    message: '',
    variant: 'danger',
  });

  const [resolver, setResolver] = useState(null);

  const confirm = (message, options = {}) => {
    return new Promise((resolve) => {
      setDialog({
        open: true,
        title: options.title || '确认',
        message,
        variant: options.variant || 'danger',
      });
      setResolver(() => resolve);
    });
  };

  const handleConfirm = () => {
    if (resolver) resolver(true);
    setDialog(prev => ({ ...prev, open: false }));
    setResolver(null);
  };

  const handleCancel = () => {
    if (resolver) resolver(false);
    setDialog(prev => ({ ...prev, open: false }));
    setResolver(null);
  };

  return (
    <ConfirmContext.Provider value={{ confirm }}>
      {children}
      <ConfirmDialog
        open={dialog.open}
        title={dialog.title}
        message={dialog.message}
        variant={dialog.variant}
        confirmText="确认"
        cancelText="取消"
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    </ConfirmContext.Provider>
  );
}

export function useConfirm() {
  const context = useContext(ConfirmContext);
  if (!context) {
    throw new Error('useConfirm must be used within ConfirmProvider');
  }
  return context;
}

export function withConfirm(Component) {
  return function WrappedComponent(props) {
    const { confirm } = useConfirm();
    return <Component {...props} confirm={confirm} />;
  };
}
