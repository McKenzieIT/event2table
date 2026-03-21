/**
 * React Flow Test Wrapper
 * 
 * Provides ReactFlowProvider wrapper for tests that use React Flow components.
 * This resolves the error: "Seems like you have not used zustand provider as an ancestor"
 */

import React from 'react';
import { ReactFlowProvider } from 'reactflow';

interface ReactFlowWrapperProps {
  children: React.ReactNode;
}

/**
 * Wrapper component that provides React Flow context for tests
 */
export const ReactFlowWrapper: React.FC<ReactFlowWrapperProps> = ({ children }) => {
  return (
    <ReactFlowProvider>
      {children}
    </ReactFlowProvider>
  );
};

/**
 * Creates a wrapper function for renderHook tests
 */
export const createReactFlowWrapper = () => {
  return ({ children }: { children: React.ReactNode }) => (
    <ReactFlowWrapper>{children}</ReactFlowWrapper>
  );
};

export default ReactFlowWrapper;
