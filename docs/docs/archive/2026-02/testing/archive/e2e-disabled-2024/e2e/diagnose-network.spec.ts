import { test, expect } from '@playwright/test';

test('Diagnose network requests', async ({ page }) => {
  // Track all requests
  const requests: { url: string; status: number | null }[] = [];
  page.on('request', request => {
    requests.push({ url: request.url(), status: null });
  });

  page.on('response', response => {
    const req = requests.find(r => r.url === response.url());
    if (req) req.status = response.status();
  });

  await page.goto('/#/games');
  await page.waitForTimeout(5000);

  // Check React script request
  const reactScriptReq = requests.find(r => r.url.includes('index-Dg5LwOXS.js'));
  console.log('React script request:', reactScriptReq ? 'FOUND' : 'NOT FOUND');
  if (reactScriptReq) {
    console.log('  URL:', reactScriptReq.url);
    console.log('  Status:', reactScriptReq.status);
  }

  // Check all failed requests
  const failed = requests.filter(r => r.status && r.status >= 400);
  console.log('Failed requests:', failed.length);
  failed.forEach(f => console.log('  -', f.url, 'Status:', f.status));

  // Check CSS request
  const cssReq = requests.find(r => r.url.includes('index-CV9Co3rJ.css'));
  console.log('CSS request:', cssReq ? 'FOUND' : 'NOT FOUND');
  if (cssReq) {
    console.log('  Status:', cssReq.status);
  }
});
