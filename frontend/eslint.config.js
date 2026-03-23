import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import importPlugin from 'eslint-plugin-import';
import { plugin as noHardcodedColorsPlugin } from './eslint-plugin-no-hardcoded-colors.js';
import basemodalMigration from './eslint-plugin-basemodal-migration.js';

export default tseslint.config(
  { ignores: [
    'dist',
    'node_modules',
    'tests/performance/**',
    'tests/debug/**',
    'tests/e2e/**',
    'test/**',
    'vite.config.ts',
    'vite.config.enhanced.ts',
    'vitest.config.ts',
    'playwright.config.ts',
    'test/test-utils.tsx',
    // 自动生成的文件
    'src/types/api.generated.ts',
    'src/types/global.d.ts',
    // 不在 tsconfig.json 范围内的文件
    'src/features/games/__tests__/AddGameModalGraphQL.type.test.tsx',
    'src/migration/GAMES_MIGRATION_EXAMPLE.ts',
    'src/shared/components/VirtualList/index.tsx',
    'src/shared/ui/Button/Button.d.ts',
  ] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      parserOptions: {
        project: './tsconfig.json',
        tsconfigRootDir: import.meta.dirname,
      },
      globals: {
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        FormData: 'readonly',
        Blob: 'readonly',
        File: 'readonly',
        URL: 'readonly',
        Request: 'readonly',
        Response: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        setInterval: 'readonly',
        clearTimeout: 'readonly',
        clearInterval: 'readonly',
        Promise: 'readonly',
        Array: 'readonly',
        Object: 'readonly',
        String: 'readonly',
        Number: 'readonly',
        Boolean: 'readonly',
        Math: 'readonly',
        Date: 'readonly',
        JSON: 'readonly',
        RegExp: 'readonly',
        Error: 'readonly',
        TypeError: 'readonly',
        SyntaxError: 'readonly',
        RangeError: 'readonly',
        ReferenceError: 'readonly',
        XMLHttpRequest: 'readonly',
        Worker: 'readonly',
        navigator: 'readonly',
        location: 'readonly',
        history: 'readonly',
        performance: 'readonly',
        MutationObserver: 'readonly',
        IntersectionObserver: 'readonly',
        Element: 'readonly',
        HTMLElement: 'readonly',
        HTMLDivElement: 'readonly',
        HTMLInputElement: 'readonly',
        HTMLButtonElement: 'readonly',
        Event: 'readonly',
        MouseEvent: 'readonly',
        KeyboardEvent: 'readonly',
        CustomEvent: 'readonly',
      },
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      'no-hardcoded-colors': noHardcodedColorsPlugin,
      'basemodal-migration': basemodalMigration,
      import: importPlugin,
    },
    rules: {
      ...react.configs.recommended.rules,
      // React Hooks 规则 - 开发阶段放宽限制
      // 注意：这些规则在编译器 (React Compiler / Babel) 中已有保障
      'react-hooks/rules-of-hooks': 'warn',      // Hooks 调用规则
      'react-hooks/exhaustive-deps': 'warn',     // useEffect 依赖
      'react-hooks/set-state-in-effect': 'warn', // effect 中的 setState
      'react-hooks/refs': 'warn',                // refs 使用规则
      'react-hooks/purity': 'warn',              // 组件纯度
      'react-hooks/globals': 'warn',             // 全局变量使用
      'react-hooks/preserve-manual-memoization': 'warn', // 手动 memoization
      'react-hooks/incompatible-library': 'warn', // 不兼容库检测
      // React 17+ 不再需要显式导入 React
      'react/react-in-jsx-scope': 'off',
      'react/jsx-uses-react': 'off',
      // React 组件规则 - 开发阶段放宽限制
      'react/prop-types': 'off',
      'react/display-name': 'warn',              // 组件显示名称
      'react/no-unescaped-entities': 'warn',     // 未转义字符
      '@typescript-eslint/ban-ts-comment': ['off'],
      // 未使用变量 - 开发阶段放宽限制
      '@typescript-eslint/no-unused-vars': 'off',
      // 类型相关规则 - 开发阶段放宽限制
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-non-null-assertion': 'off',
      '@typescript-eslint/strict-boolean-expressions': 'off',
      '@typescript-eslint/no-floating-promises': 'off',
      // 开发环境允许 console，CI 中可通过其他方式检查
      'no-console': 'off',
      'no-unused-vars': 'off',
      'no-hardcoded-colors/no-hardcoded-colors': 'warn',
      'basemodal-migration/use-content-class-name': 'error',
      // 测试文件必须使用 test-utils 而非直接导入 @testing-library/react
      // 开发阶段放宽限制 - 改为警告
      'no-restricted-imports': ['warn', {
        patterns: [{
          group: ['@testing-library/react'],
          message: 'Use @/test/test-utils instead for component tests. This provides automatic Provider wrapping and better test isolation.'
        }]
      }],
      // 关闭 require 导入检查 - 开发阶段
      '@typescript-eslint/no-require-imports': 'off',
      // ============================================================================
      // Import/Export 规范 - 开发阶段放宽限制
      // ============================================================================
      'import/export': 'warn',           // 检查重复导出
      'import/named': 'warn',            // 检查 named import 是否存在
      'import/default': 'warn',          // 检查 default import 是否存在
      'import/namespace': 'warn',        // 检查 namespace import 是否存在
      'import/no-duplicates': 'warn',    // 禁止重复导入
      // 导入顺序规范 - 仅作为格式建议，不强制
      'import/order': 'off',
      // ============================================================================
      // 其他规则 - 开发阶段放宽限制
      // ============================================================================
      '@typescript-eslint/no-empty-object-type': 'warn',  // 空对象类型
      'no-empty': 'warn',                                  // 空块语句
      'no-prototype-builtins': 'warn',                    // Object.prototype 方法
      'no-useless-escape': 'warn',                        // 无用转义
      'no-case-declarations': 'warn',                     // case 中声明
      'react/no-deprecated': 'warn',                      // 废弃 API
      'react/no-children-prop': 'warn',                   // children prop
      'react/jsx-no-undef': 'warn',                       // 未定义 JSX
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
  {
    extends: [js.configs.recommended],
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: 'module',
      globals: {
        window: 'readonly',
        document: 'readonly',
        localStorage: 'readonly',
        sessionStorage: 'readonly',
        FormData: 'readonly',
        Blob: 'readonly',
        File: 'readonly',
        URL: 'readonly',
        Request: 'readonly',
        Response: 'readonly',
        fetch: 'readonly',
        setTimeout: 'readonly',
        setInterval: 'readonly',
        clearTimeout: 'readonly',
        clearInterval: 'readonly',
        Promise: 'readonly',
        Array: 'readonly',
        Object: 'readonly',
        String: 'readonly',
        Number: 'readonly',
        Boolean: 'readonly',
        Math: 'readonly',
        Date: 'readonly',
        JSON: 'readonly',
        RegExp: 'readonly',
        Error: 'readonly',
        TypeError: 'readonly',
        SyntaxError: 'readonly',
        RangeError: 'readonly',
        ReferenceError: 'readonly',
        XMLHttpRequest: 'readonly',
        Worker: 'readonly',
        navigator: 'readonly',
        location: 'readonly',
        history: 'readonly',
        performance: 'readonly',
        MutationObserver: 'readonly',
        IntersectionObserver: 'readonly',
        Element: 'readonly',
        HTMLElement: 'readonly',
        HTMLDivElement: 'readonly',
        HTMLInputElement: 'readonly',
        HTMLButtonElement: 'readonly',
        Event: 'readonly',
        MouseEvent: 'readonly',
        KeyboardEvent: 'readonly',
        CustomEvent: 'readonly',
        console: 'readonly',
        process: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        module: 'readonly',
        require: 'readonly',
        exports: 'readonly',
      },
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
      'no-hardcoded-colors': noHardcodedColorsPlugin,
      'basemodal-migration': basemodalMigration,
    },
    rules: {
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/prop-types': 'off',
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
      'no-console': 'off',
      'no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        caughtErrorsIgnorePattern: '^_',
      }],
      'no-undef': 'error',
      'no-hardcoded-colors/no-hardcoded-colors': 'warn',
      'basemodal-migration/use-content-class-name': 'error',
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },
  {
    extends: [js.configs.recommended],
    files: ['eslint.config.js', 'eslint-plugin-*.js', 'playwright.config.js', 'scripts/**/*.js', 'public/**/*.js'],
    languageOptions: {
      ecmaVersion: 2020,
      sourceType: 'module',
      globals: {
        console: 'readonly',
        process: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        module: 'readonly',
        require: 'readonly',
        exports: 'readonly',
      },
    },
    rules: {
      'no-console': 'off',
      'no-unused-vars': ['error', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        caughtErrorsIgnorePattern: '^_',
      }],
      'no-undef': 'off',
    },
  },
);