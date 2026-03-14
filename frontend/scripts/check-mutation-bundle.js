// ============================================
// GraphQL Mutation Bundle 诊断脚本
// ============================================
//
// 用法：在浏览器Console中执行此脚本
// 目的：检查实际加载的mutation定义是否是新的
// ============================================

console.log('🔍 开始诊断GraphQL mutation bundle...');

// 方法1: 检查所有script标签中的GraphQL mutation字符串
console.log('\n=== 方法1: 检查script标签 ===');
const scripts = document.querySelectorAll('script[type="module"]');
let foundInScripts = false;

scripts.forEach(script => {
  if (script.src && script.src.includes('chunk-')) {
    console.log(`📦 发现chunk: ${script.src}`);

    // 尝试fetch这个chunk的内容
    fetch(script.src)
      .then(response => response.text())
      .then(code => {
        // 检查是否包含旧的mutation字段
        if (code.includes('batchAddFieldsToCanvas')) {
          console.log(`✅ ${script.src} 包含 batchAddFieldsToCanvas mutation`);

          // 检查字段
          const hasOk = code.includes('"ok"') || code.includes("'ok'");
          const hasSuccess = code.includes('"success"') || code.includes("'success'");
          const hasFields = code.includes('"fields"') || code.includes("'fields'");
          const hasResult = code.includes('"result"') || code.includes("'result'");

          console.log(`   字段检查:`);
          console.log(`   - ok: ${hasOk ? '✅' : '❌'}`);
          console.log(`   - success: ${hasSuccess ? '✅' : '❌'}`);
          console.log(`   - fields: ${hasFields ? '✅' : '❌'}`);
          console.log(`   - result: ${hasResult ? '✅' : '❌'}`);

          if (hasOk && hasFields && !hasResult) {
            console.log(`🎉 ${script.src} 使用的是新的mutation定义！`);
          } else if (hasSuccess && hasResult) {
            console.log(`⚠️  ${script.src} 使用的是旧的mutation定义！`);
            console.log(`   这是导致400错误的原因！`);
          } else {
            console.log(`❓ ${script.src} mutation定义不明确`);
          }
        }
      })
      .catch(err => {
        console.log(`❌ 无法fetch ${script.src}:`, err.message);
      });

    foundInScripts = true;
  }
});

if (!foundInScripts) {
  console.log('❓ 未找到chunk文件');
}

// 方法2: 检查Apollo Client缓存
console.log('\n=== 方法2: 检查Apollo Client缓存 ===');
if (window.__APOLLO_CLIENT__) {
  const cache = window.__APOLLO_CLIENT__.cache;
  console.log('✅ Apollo Client已找到');

  // 尝试提取缓存的mutation定义
  const data = cache.extract();
  console.log('📦 缓存数据:', data);

  // 检查是否有旧的mutation缓存
  const hasOldMutation = JSON.stringify(data).includes('batchAddFieldsToCanvas');
  if (hasOldMutation) {
    console.log('⚠️  Apollo缓存中包含batchAddFieldsToCanvas mutation');
    console.log('   这可能导致使用旧的mutation定义');
  } else {
    console.log('✅ Apollo缓存中无batchAddFieldsToCanvas mutation');
  }
} else {
  console.log('❓ 未找到Apollo Client');
}

// 方法3: 拦截GraphQL请求
console.log('\n=== 方法3: GraphQL请求拦截器 ===');
const originalFetch = window.fetch;
window.fetch = function(...args) {
  const url = args[0];

  if (typeof url === 'string' && url.includes('/api/graphql')) {
    console.log('🔍 检测到GraphQL请求');

    // 检查请求body
    if (args[1] && args[1].body) {
      try {
        const body = JSON.parse(args[1].body);
        const query = body.query;

        if (query.includes('batchAddFieldsToCanvas')) {
          console.log('✅ batchAddFieldsToCanvas mutation被调用');

          // 检查字段
          const hasOk = query.includes('ok');
          const hasSuccess = query.includes('success');
          const hasFields = query.includes('fields');
          const hasResult = query.includes('result');

          console.log(`   查询字段检查:`);
          console.log(`   - ok: ${hasOk ? '✅' : '❌'}`);
          console.log(`   - success: ${hasSuccess ? '✅' : '❌'}`);
          console.log(`   - fields: ${hasFields ? '✅' : '❌'}`);
          console.log(`   - result: ${hasResult ? '✅' : '❌'}`);

          if (hasOk && hasFields && !hasResult) {
            console.log(`🎉 使用的是新的mutation定义！`);
          } else if (hasSuccess && hasResult) {
            console.log(`⚠️  使用的是旧的mutation定义！`);
            console.log(`   这是导致400错误的原因！`);
            console.log(`   实际查询:`, query);
          } else {
            console.log(`❓ mutation定义不明确`);
            console.log(`   实际查询:`, query);
          }
        }
      } catch (e) {
        console.log('❌ 无法解析请求body:', e.message);
      }
    }
  }

  return originalFetch.apply(this, args);
};

console.log('\n✅ GraphQL请求拦截器已启用');
console.log('📌 现在请操作FieldSelectionModal，触发mutation调用');
console.log('📌 Console会显示实际发送的GraphQL查询内容');

// 方法4: 清除所有缓存
console.log('\n=== 方法4: 强制清除所有缓存 ===');
console.log('执行以下命令清除所有缓存:');
console.log('  1. localStorage.clear();');
console.log('  2. sessionStorage.clear();');
console.log('  3. location.reload(true);');
console.log('或者点击:');
console.log('  清除Application → Storage → Clear site data');
console.log('  然后硬刷新: Cmd+Shift+R (Mac) 或 Ctrl+Shift+R (Windows)');

// 提供一键清除函数
window.forceClearAllCaches = function() {
  console.log('🧹 清除所有缓存...');

  // 清除localStorage
  localStorage.clear();
  console.log('✅ localStorage已清除');

  // 清除sessionStorage
  sessionStorage.clear();
  console.log('✅ sessionStorage已清除');

  // 清除Apollo Client缓存
  if (window.__APOLLO_CLIENT__) {
    window.__APOLLO_CLIENT__.clearStore()
      .then(() => console.log('✅ Apollo缓存已清除'))
      .catch(err => console.log('❌ 清除Apollo缓存失败:', err));
  }

  // 强制重新加载
  console.log('🔄 3秒后重新加载页面...');
  setTimeout(() => {
    location.reload(true);
  }, 3000);
};

console.log('\n💡 提示: 执行 forceClearAllCaches() 函数可一键清除所有缓存');
console.log('🔍 诊断完成！');
