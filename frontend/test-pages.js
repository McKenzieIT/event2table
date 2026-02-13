/**
 * Manual page test script
 * Tests if pages load without errors
 */

const pages = [
  '/',
  '/#/games',
  '/#/events',
  '/#/parameters',
  '/#/categories',
  '/#/canvas',
  '/#/field-builder',
  '/#/flows',
  '/#/event-nodes',
  '/#/event-node-builder',
  '/#/hql-manage',
  '/#/generate',
];

console.log('Pages to test:', pages.length);
console.log('Base URL: http://localhost:5173');
console.log('\nTest these pages manually by opening in browser:');
pages.forEach(page => {
  console.log(`  - http://localhost:5173${page}`);
});
