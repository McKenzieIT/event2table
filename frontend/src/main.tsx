// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { ApolloProvider } from "@apollo/client/react";
import { Toaster } from "react-hot-toast";
import { ToastProvider } from "@shared/ui";
import { ErrorBoundary } from "@shared/ui/ErrorBoundary";
import { client } from "@shared/apollo/client";
import App from "./App";

// CSS imports - Order is critical for Vite
// 1. Design tokens (must load first for CSS variables)
import "./styles/design-tokens.css";
// 2. Component styles (depends on design tokens)
import "./styles/components.css";
// 3. Base styles (depends on both above)
import "./index.css";

import { queryClient } from "@/config/queryClient";

// ✅ E2E Testing: Add diagnostic logging
console.log('[main.tsx] 🔵 Starting React app mount...');
console.log('[main.tsx] 🔵 Document ready state:', document.readyState);
console.log('[main.tsx] 🔵 Looking for #app-root element...');

// Find or create root element with fallback
let rootElement = document.getElementById("app-root");

if (!rootElement) {
  console.error('[main.tsx] ❌ #app-root not found, creating fallback element');
  console.log('[main.tsx] 🔵 Creating fallback #app-root element...');

  const fallback = document.createElement('div');
  fallback.id = 'app-root';
  document.body.appendChild(fallback);

  rootElement = fallback;
  console.log('[main.tsx] ✅ Fallback #app-root created and appended to body');
}

console.log('[main.tsx] ✅ Root element found:', {
  exists: !!rootElement,
  tagName: rootElement.tagName,
  id: rootElement.id,
  hasChildren: rootElement.children.length > 0
});

console.log('[main.tsx] 🔵 Creating React root...');
const root = ReactDOM.createRoot(rootElement);
console.log('[main.tsx] ✅ React root created successfully');

console.log('[main.tsx] 🔵 Rendering app with providers...');
console.log('[main.tsx] 🔵 Providers: ErrorBoundary > BrowserRouter > ApolloProvider > QueryClientProvider > ToastProvider');

root.render(
  <ErrorBoundary>
    <BrowserRouter future={{
      v7_startTransition: true,
      v7_relativeSplatPath: true,
    }}>
      <ApolloProvider client={client}>
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <App />
          </ToastProvider>
        </QueryClientProvider>
      </ApolloProvider>
      <Toaster position="top-right" />
    </BrowserRouter>
  </ErrorBoundary>
);

console.log('[main.tsx] ✅ React app render initiated successfully');

// ✅ E2E Testing: Properly verify React mounting and clean up initial loader
// Using requestAnimationFrame + setTimeout to ensure React has completed rendering
requestAnimationFrame(() => {
  // Schedule verification after current paint + React render cycle
  setTimeout(() => {
    console.log('[main.tsx] 🔵 Verifying React mount...');

    const appRoot = document.getElementById('app-root');
    const loader = document.getElementById('initial-loader');

    // Proper verification: Check if root has any children (React renders at least one div)
    const hasChildren = appRoot && appRoot.children.length > 0;

    // Additional check: root is not empty
    const hasContent = appRoot && appRoot.innerHTML.trim().length > 0;

    console.log('[main.tsx] 🔵 React mount verification:', {
      rootExists: !!appRoot,
      hasChildren,
      childrenCount: appRoot?.children.length || 0,
      hasContent,
      innerHTMLLength: appRoot?.innerHTML.length || 0,
      readyState: document.readyState
    });

    if (hasChildren && hasContent) {
      console.log('[main.tsx] ✅ React mounted successfully!');

      // Only remove loader if React has mounted successfully
      if (loader) {
        console.log('[main.tsx] 🔵 Removing initial loader...');
        loader.remove();
        console.log('[main.tsx] ✅ Initial loader removed successfully');
      }
    } else {
      // If mounting failed, wait a bit longer and check once more
      console.warn('[main.tsx] ⚠️ React not yet mounted, scheduling delayed verification...');

      setTimeout(() => {
        const finalCheck = document.getElementById('app-root');
        const finalHasChildren = finalCheck && finalCheck.children.length > 0;

        if (finalHasChildren) {
          console.log('[main.tsx] ✅ React mounted successfully (delayed check)!');

          if (loader) {
            loader.remove();
            console.log('[main.tsx] ✅ Initial loader removed successfully');
          }
        } else {
          console.error('[main.tsx] ❌ WARNING: React may not have mounted correctly!');
          console.error('[main.tsx] ❌ This may indicate a JavaScript error during rendering');
          console.error('[main.tsx] ❌ Check browser console for React errors');
        }
      }, 1000);
    }
  }, 0);
});
