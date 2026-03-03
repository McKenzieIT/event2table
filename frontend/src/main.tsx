// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
import React from "react";
import ReactDOM from "react-dom/client";
import { HashRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { ApolloProvider } from "@apollo/client";
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

const rootElement = document.getElementById("app-root");

if (!rootElement) {
  throw new Error('Failed to find the root element with id "app-root"');
}

ReactDOM.createRoot(rootElement).render(
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
  </ErrorBoundary>,
);
