// 🔍 渐进式Provider测试 - 使用动态import
// @ts-nocheck

import React from "react";
import ReactDOM from "react-dom/client";

console.log('[PROGRESSIVE TEST] Starting...');

const rootElement = document.getElementById("app-root");
if (!rootElement) {
  console.error('[PROGRESSIVE TEST] Root element not found');
  throw new Error('Root element not found');
}

const root = ReactDOM.createRoot(rootElement);

// 移除加载器
const loader = document.getElementById('initial-loader');
if (loader) loader.remove();

// 第1步: 测试基础React
console.log('[TEST 1] Testing basic React rendering...');
root.render(
  React.createElement('div', {
    style: {
      padding: '20px',
      background: '#e0f2fe',
      color: '#0d47a1',
      fontFamily: 'Arial, sans-serif',
      fontSize: '18px'
    }
  }, '🎯 Step 1: Basic React - Running...')
);

// 第2步: 测试HashRouter（3秒后）
setTimeout(() => {
  console.log('[TEST 2] Testing with HashRouter...');
  import('react-router-dom').then(({ HashRouter }) => {
    console.log('[TEST 2] HashRouter imported successfully');

    root.render(
      React.createElement(HashRouter, null,
        React.createElement('div', {
          style: {
            padding: '20px',
            background: '#e1bee7',
            color: '#4a148c',
            fontFamily: 'Arial, sans-serif',
            fontSize: '18px'
          }
        }, '🎯 Step 2: HashRouter - SUCCESS!')
      )
    );

    console.log('[PROGRESSIVE TEST] ✅ Test 2 passed: HashRouter works');

    // 第3步: 测试QueryClientProvider（3秒后）
    setTimeout(() => {
      console.log('[TEST 3] Testing with QueryClientProvider...');

      Promise.all([
        import('@tanstack/react-query'),
        import('@analytics/components/lib/queryClient')
      ]).then(([{ QueryClientProvider }, { queryClient }]) => {
        console.log('[TEST 3] QueryClient imported successfully');

        root.render(
          React.createElement(QueryClientProvider, { client: queryClient },
            React.createElement(HashRouter, null,
              React.createElement('div', {
                style: {
                  padding: '20px',
                  background: '#c8e6c9',
                  color: '#1b5e20',
                  fontFamily: 'Arial, sans-serif',
                  fontSize: '18px'
                }
              }, '🎯 Step 3: QueryClientProvider - SUCCESS!')
            )
          )
        );

        console.log('[PROGRESSIVE TEST] ✅ Test 3 passed: QueryClientProvider works');

        // 第4步: 测试ApolloProvider（3秒后）
        setTimeout(() => {
          console.log('[TEST 4] Testing with ApolloProvider...');

          Promise.all([
            import('@apollo/client/react'),
            import('@shared/apollo/client')
          ]).then(({ ApolloProvider }, { client }) => {
            console.log('[TEST 4] Apollo Client imported successfully');

            root.render(
              React.createElement(ApolloProvider, { client: client },
                React.createElement(QueryClientProvider, { client: queryClient },
                  React.createElement(HashRouter, null,
                    React.createElement('div', {
                      style: {
                        padding: '20px',
                        background: '#ffccbc',
                        color: '#bf360c',
                        fontFamily: 'Arial, sans-serif',
                        fontSize: '18px'
                      }
                    }, '🎯 Step 4: ApolloProvider - SUCCESS!')
                  )
                )
              )
            );

            console.log('[PROGRESSIVE TEST] ✅ Test 4 passed: ApolloProvider works');

            // 第5步: 测试所有Provider（3秒后）
            setTimeout(() => {
              console.log('[TEST 5] Testing with Toast and Popup...');

              Promise.all([
                import('@shared/ui'),
                import('@shared/popup/PopupProvider')
              ]).then(([{ ToastProvider }, { PopupProvider }) => {
                console.log('[TEST 5] Toast and Popup imported successfully');

                root.render(
                  React.createElement(ToastProvider, null,
                    React.createElement(PopupProvider, null,
                      React.createElement(ApolloProvider, { client: client },
                        React.createElement(QueryClientProvider, { client: queryClient },
                          React.createElement(HashRouter, null,
                            React.createElement('div', {
                              style: {
                                padding: '20px',
                                background: '#b2dfdb',
                                color: '#006064',
                                fontFamily: 'Arial, sans-serif',
                                fontSize: '18px'
                              }
                            }, '🎯 Step 5: All Providers - SUCCESS! 🎉')
                          )
                        )
                      )
                    )
                  )
                );

                console.log('[PROGRESSIVE TEST] ✅ Test 5 passed: All Providers work!');
                console.log('[PROGRESSIVE TEST] 🎉 ALL TESTS PASSED!');

                // 显示成功消息
                setTimeout(() => {
                  const successDiv = document.createElement('div');
                  successDiv.style.cssText = `
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: #4caf50;
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    font-family: Arial, sans-serif;
                    z-index: 999999;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                  `;
                  successDiv.innerHTML = `
                    <h3 style="margin:0 0 10px 0;">✅ 所有Provider测试通过!</h3>
                    <p style="margin:0;">React应用可以正常加载</p>
                  `;
                  document.body.appendChild(successDiv);
                }, 500);

              }).catch(err => {
                console.error('[TEST 5 FAILED] Toast/Popup error:', err);
                showStepError(5, 'Toast/Popup Providers', err);
              });

            }).catch(err => {
              console.error('[TEST 4 FAILED] ApolloProvider error:', err);
              showStepError(4, 'ApolloProvider', err);
            });

          }).catch(err => {
            console.error('[TEST 3 FAILED] QueryClientProvider error:', err);
            showStepError(3, 'QueryClientProvider', err);
          });

        }).catch(err => {
          console.error('[TEST 2 FAILED] HashRouter error:', err);
          showStepError(2, 'HashRouter', err);
        });

      }).catch(err => {
        console.error('[PROGRESSIVE TEST] Fatal error:', err);
        document.body.innerHTML = `
          <div style="background:red;color:white;padding:20px;font-family:monospace;font-size:14px;">
            <h2>❌ FATAL ERROR:</h2>
            <p>${err.message}</p>
            <pre>${err.stack}</pre>
          </div>
        `;
      });
    });
  });
});

// 显示错误的辅助函数
function showStepError(stepNumber, stepName, error) {
  const errorDiv = document.createElement('div');
  errorDiv.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #f44336;
    color: white;
    padding: 20px;
    z-index: 999999;
    font-family: 'JetBrains Mono', monospace;
    font-size: 14px;
    max-height: 60vh;
    overflow: auto;
  `;

  errorDiv.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:15px;">
      <span style="font-size:24px;">❌</span>
      <h2 style="margin:0;">TEST ${stepNumber} FAILED</h2>
    </div>
    <div style="background:rgba(0,0,0,0.2);padding:15px;border-radius:4px;">
      <p style="margin:0 0 10px 0;"><strong>Component:</strong> ${stepName}</p>
      <p style="margin:0 0 10px 0;"><strong>Error:</strong> ${error.message || error}</p>
      ${error.stack ? `<pre style="margin-top:10px;white-space:pre-wrap;background:rgba(0,0,0,0.3);padding:10px;border-radius:4px;overflow-x:auto;">${error.stack}</pre>` : ''}
    </div>
  `;

  document.body.appendChild(errorDiv);
}
