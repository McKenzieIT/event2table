/**
 * Codemod: Replace @testing-library/react imports with @/test/test-utils
 * 
 * This codemod finds all test files that import from '@testing-library/react'
 * and replaces them with imports from '@/test/test-utils', which provides
 * the renderWithProviders wrapper.
 * 
 * Usage:
 *   npx jscodeshift -t codemods/replace-render-import.js src --extensions=tsx,ts
 */

export default function transformer(file, api) {
  const j = api.jscodeshift;
  
  // Only process test files
  if (!file.path.includes('.test.')) {
    return file.source;
  }
  
  const root = j(file.source);

  // Find all imports from @testing-library/react
  const testLibraryImports = root.find(j.ImportDeclaration, {
    source: { value: '@testing-library/react' }
  });

  if (testLibraryImports.length === 0) {
    return file.source;
  }

  // Replace the import source
  testLibraryImports.forEach(path => {
    path.node.source.value = '@/test/test-utils';
  });

  return root.toSource({ quote: 'single', trailingComma: true });
}
