/**
 * Test Pages Configuration
 * 
 * Defines all pages that need visual regression testing
 * Based on UI optimization changes made to the application
 */

export interface TestPage {
  name: string;
  url: string;
  description: string;
  waitForSelector?: string;
}

export const testPages: TestPage[] = [
  // Main Pages
  {
    name: 'Dashboard',
    url: '/',
    description: 'Main dashboard page with cards and analytics',
    waitForSelector: '.dashboard-container, [data-testid="dashboard-container"]',
  },
  {
    name: 'GamesList',
    url: '/games',
    description: 'Games management list page',
    waitForSelector: '.games-list-page, [class*="games-list"]',
  },
  {
    name: 'EventsList',
    url: '/events',
    description: 'Events management list page',
    waitForSelector: '.events-list-page, [class*="events-list"]',
  },
  {
    name: 'ParametersList',
    url: '/parameters',
    description: 'Parameters management list page',
    waitForSelector: '.parameters-list-page, [class*="parameters-list"]',
  },
  {
    name: 'CategoriesList',
    url: '/categories',
    description: 'Categories management list page',
    waitForSelector: '.categories-list-page, [class*="categories-list"]',
  },
  {
    name: 'CommonParamsList',
    url: '/common-params',
    description: 'Common parameters list page',
    waitForSelector: '.common-params-list-page, [class*="common-params"]',
  },
  {
    name: 'FlowsList',
    url: '/flows',
    description: 'Flows list page',
    waitForSelector: '.flows-list-page, [class*="flows-list"]',
  },
  
  // Canvas & Builder Pages
  {
    name: 'Canvas',
    url: '/canvas',
    description: 'Canvas flow builder page',
    waitForSelector: '.canvas-page, [class*="canvas-page"]',
  },
  {
    name: 'EventNodeBuilder',
    url: '/event-node-builder',
    description: 'Event node builder page',
    waitForSelector: '.event-node-builder, [class*="event-node-builder"]',
  },
  {
    name: 'FieldBuilder',
    url: '/field-builder',
    description: 'Field builder page',
    waitForSelector: '.field-builder-page, [class*="field-builder"]',
  },
  {
    name: 'FlowBuilder',
    url: '/flow-builder',
    description: 'Flow builder page',
    waitForSelector: '.flow-builder-page, [class*="flow-builder"]',
  },
  {
    name: 'EventNodes',
    url: '/event-nodes',
    description: 'Event nodes management page',
    waitForSelector: '.event-nodes-container, [class*="event-nodes"]',
  },
  
  // Form Pages
  {
    name: 'GameForm',
    url: '/games/create',
    description: 'Game creation form',
    waitForSelector: '.game-form-container, [class*="game-form"]',
  },
  {
    name: 'EventForm',
    url: '/events/create',
    description: 'Event creation form',
    waitForSelector: '.event-form-container, [class*="event-form"]',
  },
  {
    name: 'CategoryForm',
    url: '/categories/create',
    description: 'Category creation form',
    waitForSelector: '.category-form-container, [class*="category-form"]',
  },
  {
    name: 'LogForm',
    url: '/logs/create',
    description: 'Log creation form',
    waitForSelector: '.log-form-container, [class*="log-form"]',
  },
  
  // Parameter Pages
  {
    name: 'ParametersEnhanced',
    url: '/parameters/enhanced',
    description: 'Enhanced parameters page',
    waitForSelector: '.parameters-enhanced-container, [class*="parameters-enhanced"]',
  },
  {
    name: 'ParameterCompare',
    url: '/parameters/compare',
    description: 'Parameter comparison page',
    waitForSelector: '.parameter-compare-container, [class*="parameter-compare"]',
  },
  {
    name: 'ParameterAnalysis',
    url: '/parameter-analysis',
    description: 'Parameter analysis page',
    waitForSelector: '.parameter-analysis-page, [class*="parameter-analysis"]',
  },
  {
    name: 'ParameterDashboard',
    url: '/parameter-dashboard',
    description: 'Parameter dashboard page',
    waitForSelector: '.parameter-dashboard-page, [class*="parameter-dashboard"]',
  },
  {
    name: 'ParameterUsage',
    url: '/parameter-usage',
    description: 'Parameter usage page',
    waitForSelector: '.parameter-usage-page, [class*="parameter-usage"]',
  },
  {
    name: 'ParameterHistory',
    url: '/parameter-history',
    description: 'Parameter history page',
    waitForSelector: '.parameter-history-page, [class*="parameter-history"]',
  },
  {
    name: 'ParameterNetwork',
    url: '/parameter-network',
    description: 'Parameter network visualization page',
    waitForSelector: '.parameter-network-container, [class*="parameter-network"]',
  },
  
  // HQL Pages
  {
    name: 'HqlManage',
    url: '/hql-manage',
    description: 'HQL management page',
    waitForSelector: '.hql-manage-page, [class*="hql-manage"]',
  },
  {
    name: 'HqlResults',
    url: '/hql-results',
    description: 'HQL results page',
    waitForSelector: '.hql-results-page, [class*="hql-results"]',
  },
  
  // Generation & Import Pages
  {
    name: 'Generate',
    url: '/generate',
    description: 'HQL generation page',
    waitForSelector: '.generate-page, [class*="generate-page"]',
  },
  {
    name: 'GenerateResult',
    url: '/generate/result',
    description: 'Generation result page',
    waitForSelector: '.generate-result-page, [class*="generate-result"]',
  },
  {
    name: 'ImportEvents',
    url: '/import-events',
    description: 'Events import page',
    waitForSelector: '.import-events-page, [class*="import-events"]',
  },
  {
    name: 'AlterSqlBuilder',
    url: '/alter-sql-builder',
    description: 'ALTER SQL builder page',
    waitForSelector: '.alter-sql-builder-page, [class*="alter-sql-builder"]',
  },
  
  // Other Pages
  {
    name: 'ValidationRules',
    url: '/validation-rules',
    description: 'Validation rules page',
    waitForSelector: '.validation-rules-page, [class*="validation-rules"]',
  },
  {
    name: 'ApiDocs',
    url: '/api-docs',
    description: 'API documentation page',
    waitForSelector: '.api-docs-container, [class*="api-docs"]',
  },
  {
    name: 'BatchOperations',
    url: '/batch-operations',
    description: 'Batch operations page',
    waitForSelector: '.batch-operations-page, [class*="batch-operations"]',
  },
  {
    name: 'LogDetail',
    url: '/log-detail',
    description: 'Log detail page',
    waitForSelector: '.log-detail-container, [class*="log-detail"]',
  },
];

export const getPageUrl = (page: TestPage): string => {
  const baseUrl = process.env.BASE_URL || 'http://localhost:5173';
  return `${baseUrl}${page.url}`;
};
