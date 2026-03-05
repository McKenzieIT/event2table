// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React from "react";
import ReactDOM from "react-dom/client";
import { HashRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { ApolloProvider } from "@apollo/client/react";
import { Toaster } from "react-hot-toast";
import { ToastProvider } from "@shared/ui";
import ErrorBoundary from "@shared/components/ErrorBoundary";
import { client } from "@shared/apollo/client";
import App from "./App";

// CSS imports - Order is critical for Vite
// 1. Design tokens (must load first for CSS variables)
import "./styles/design-tokens.css";
// 2. Component styles (depends on design tokens)
import "./styles/components.css";
// 3. Base styles (depends on both above)
import "./index.css";

import { queryClient } from "@analytics/components/lib/queryClient";

// ✅ E2E Testing: Add diagnostic logging
console.log('[main.tsx] 🔵 Starting React app mount...');

const rootElement = document.getElementById("app-root");
console.log('[main.tsx] 🔵 Root element found:', !!rootElement);

if (!rootElement) {
  console.error('[main.tsx] ❌ Root element not found!');
  throw new Error('Failed to find the root element with id "app-root"');
}

console.log('[main.tsx] 🔵 Creating React root...');
const root = ReactDOM.createRoot(rootElement);

console.log('[main.tsx] 🔵 Rendering app with providers...');
root.render(
  <ErrorBoundary>
    <HashRouter>
      <ApolloProvider client={client}>
        <QueryClientProvider client={queryClient}>
          <ToastProvider>
            <App />
          </ToastProvider>
        </QueryClientProvider>
      </ApolloProvider>
      <Toaster position="top-right" />
    </HashRouter>
  </ErrorBoundary>
);

console.log('[main.tsx] ✅ React app render initiated');

// ✅ E2E Testing: Manually hide initial loader after React mounts
// This fixes the CSS selector issue where `+` sibling selector doesn't work
requestAnimationFrame(() => {
  console.log('[main.tsx] 🔵 Hiding initial loader...');
  const loader = document.getElementById('initial-loader');
  if (loader) {
    loader.style.display = 'none';
    console.log('[main.tsx] ✅ Initial loader hidden successfully');
  } else {
    console.warn('[main.tsx] ⚠️ Loader element not found');
  }

  // Verify React mounted
  const appRoot = document.getElementById('app-root');
  const hasChildren = appRoot && appRoot.children.length > 0;
  console.log('[main.tsx] 🔵 React mount verification:', {
    hasChildren,
    childrenCount: appRoot?.children.length || 0,
    innerHTMLLength: appRoot?.innerHTML?.length || 0
  });

  if (!hasChildren) {
    console.error('[main.tsx] ❌ WARNING: React may not have mounted correctly!');
  }
});
