// 🔧 临时最小化测试 - 只测试React是否能工作
// @ts-nocheck

import React from "react";
import ReactDOM from "react-dom/client";

console.log('[MINIMAL TEST] Script loaded');

try {
  console.log('[MINIMAL TEST] Creating React root');
  const rootElement = document.getElementById("app-root");
  console.log('[MINIMAL TEST] Root element:', rootElement);

  if (!rootElement) {
    console.error('[MINIMAL TEST] Root element not found!');
    document.body.innerHTML = '<div style="color:red;">❌ Root element not found</div>';
  } else {
    console.log('[MINIMAL TEST] Creating ReactDOM root');
    const root = ReactDOM.createRoot(rootElement);
    console.log('[MINIMAL TEST] Rendering simple component');

    root.render(
      React.createElement('div', {
        style: {
          padding: '40px',
          background: 'lightblue',
          color: 'darkblue',
          fontFamily: 'Arial, sans-serif',
          fontSize: '24px',
          fontWeight: 'bold'
        }
      }, '✅ React Works! Loading...')
    );

    console.log('[MINIMAL TEST] Render complete');

    // 移除加载器
    const loader = document.getElementById('initial-loader');
    if (loader) {
      console.log('[MINIMAL TEST] Removing loader');
      loader.remove();
    }
  }
} catch (error) {
  console.error('[MINIMAL TEST] Error:', error);
  document.body.innerHTML = `
    <div style="background:red;color:white;padding:20px;font-family:monospace;">
      <h2>❌ MINIMAL TEST ERROR:</h2>
      <p>${error.message}</p>
      <pre>${error.stack}</pre>
    </div>
  `;
}

console.log('[MINIMAL TEST] Script execution complete');
