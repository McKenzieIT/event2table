import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Capture console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('❌ Console Error:', msg.text());
    }
  });
  
  console.log('📍 Navigating to http://localhost:5173/#/');
  
  try {
    await page.goto('http://localhost:5173/#/', { timeout: 15000, waitUntil: 'networkidle' });
    
    console.log('✅ Page loaded successfully!');
    
    // Check if React app mounted
    const appRoot = await page.locator('#app-root').count();
    const appContent = await page.locator('#app-root').innerHTML();
    
    console.log(`📦 app-root exists: ${appRoot > 0}`);
    console.log(`📦 app-root content length: ${appContent.length}`);
    
    if (appContent.length > 0) {
      console.log('✅ React app mounted successfully!');
      
      // Check for Dashboard
      const dashboardExists = await page.locator('h1, h2').filter({ hasText: /Dashboard|Event2Table/i }).count();
      console.log(`📊 Dashboard found: ${dashboardExists > 0}`);
      
      if (dashboardExists > 0) {
        console.log('🎉 SUCCESS: Application is working!');
      } else {
        console.log('⚠️ Dashboard not found, but app mounted');
      }
    } else {
      console.log('❌ FAIL: app-root is empty (React not mounted)');
    }
    
    // Screenshot
    await page.screenshot({ path: '/Users/mckenzie/Documents/event2table/fix-verification.png', fullPage: true });
    console.log('📸 Screenshot saved: /Users/mckenzie/Documents/event2table/fix-verification.png');
    
  } catch (error) {
    console.log('❌ Error:', error.message);
  }
  
  await browser.close();
})();
