import React from "react";
import ReactDOM from "react-dom/client";
import { HashRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { ToastProvider } from "@shared/ui";
import App from "./App";

// CSS imports - Order is critical for Vite
// 1. Design tokens (must load first for CSS variables)
import "./styles/design-tokens.css";
// 2. Component styles (depends on design tokens)
import "./styles/components.css";
// 3. Base styles (depends on both above)
import "./index.css";

import { queryClient } from "@analytics/components/lib/queryClient";

ReactDOM.createRoot(document.getElementById("app-root")).render(
  <HashRouter>
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <App />
      </ToastProvider>
    </QueryClientProvider>
    <Toaster position="top-right" />
  </HashRouter>,
);
