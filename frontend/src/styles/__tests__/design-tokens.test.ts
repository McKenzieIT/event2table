/**
 * Design Tokens Integration Tests
 *
 * 验证 CSS 变量和设计令牌的正确性
 * 赛博朋克实验室风格设计系统
 * 
 * 通过读取 CSS 文件内容验证令牌定义
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

// 读取 CSS 文件内容
let cssContent: string;

beforeAll(() => {
  const cssPath = join(__dirname, '../design-tokens.css');
  cssContent = existsSync(cssPath) ? readFileSync(cssPath, 'utf-8') : '';
});

// 辅助函数：检查 CSS 变量是否定义
function hasToken(content: string, token: string): boolean {
  const regex = new RegExp(`--${token.replace(/^--/, '')}\\s*:`, 'g');
  return regex.test(content);
}

// 辅助函数：获取 CSS 变量的值
function getTokenValue(content: string, token: string): string | null {
  const normalizedToken = token.replace(/^--/, '');
  const regex = new RegExp(`--${normalizedToken}\\s*:\\s*([^;]+);`, 'g');
  const match = regex.exec(content);
  return match ? match[1].trim() : null;
}

// ============================================================================
// Color System Tests
// ============================================================================

describe('Color System', () => {
  it('should have primary cyan color tokens defined', () => {
    const cyanTokens = [
      'cyan-400', 'cyan-500', 'cyan-600', 'cyan-700',
    ];
    
    cyanTokens.forEach(token => {
      expect(hasToken(cssContent, token), `Missing color token: --${token}`).toBe(true);
    });
  });

  it('should have accent violet color tokens defined', () => {
    const violetTokens = [
      'violet-400', 'violet-500', 'violet-600', 'violet-700',
    ];
    
    violetTokens.forEach(token => {
      expect(hasToken(cssContent, token), `Missing color token: --${token}`).toBe(true);
    });
  });

  it('should have correct primary color value for cyan-500', () => {
    const value = getTokenValue(cssContent, 'cyan-500');
    expect(value).toBe('#06B6D4');
  });

  it('should have correct accent color value for violet-500', () => {
    const value = getTokenValue(cssContent, 'violet-500');
    expect(value).toBe('#8B5CF6');
  });

  it('should have semantic colors defined', () => {
    expect(hasToken(cssContent, 'success')).toBe(true);
    expect(hasToken(cssContent, 'warning')).toBe(true);
    expect(hasToken(cssContent, 'danger')).toBe(true);
    expect(hasToken(cssContent, 'info')).toBe(true);
  });

  it('should have semantic subtle colors defined', () => {
    expect(hasToken(cssContent, 'success-subtle')).toBe(true);
    expect(hasToken(cssContent, 'warning-subtle')).toBe(true);
    expect(hasToken(cssContent, 'danger-subtle')).toBe(true);
    expect(hasToken(cssContent, 'info-subtle')).toBe(true);
  });

  it('should have background colors defined', () => {
    expect(hasToken(cssContent, 'bg-deep')).toBe(true);
    expect(hasToken(cssContent, 'bg-base')).toBe(true);
    expect(hasToken(cssContent, 'bg-elevated')).toBe(true);
    expect(hasToken(cssContent, 'bg-glass')).toBe(true);
    expect(hasToken(cssContent, 'bg-glass-light')).toBe(true);
  });

  it('should have text colors defined', () => {
    expect(hasToken(cssContent, 'text-primary')).toBe(true);
    expect(hasToken(cssContent, 'text-secondary')).toBe(true);
    expect(hasToken(cssContent, 'text-muted')).toBe(true);
    expect(hasToken(cssContent, 'text-disabled')).toBe(true);
  });

  it('should have border colors defined', () => {
    expect(hasToken(cssContent, 'border-default')).toBe(true);
    expect(hasToken(cssContent, 'border-medium')).toBe(true);
    expect(hasToken(cssContent, 'border-strong')).toBe(true);
  });
});

// ============================================================================
// Spacing System Tests
// ============================================================================

describe('Spacing System', () => {
  it('should have spacing tokens defined', () => {
    const spacingTokens = ['space-1', 'space-2', 'space-3', 'space-4', 'space-5', 'space-6', 'space-8'];
    
    spacingTokens.forEach(token => {
      expect(hasToken(cssContent, token), `Missing spacing token: --${token}`).toBe(true);
    });
  });

  it('should use 4px base unit for spacing', () => {
    // space-1 should be 4px (0.25rem)
    expect(getTokenValue(cssContent, 'space-1')).toBe('0.25rem');
    
    // space-2 should be 8px (0.5rem)
    expect(getTokenValue(cssContent, 'space-2')).toBe('0.5rem');
    
    // space-4 should be 16px (1rem)
    expect(getTokenValue(cssContent, 'space-4')).toBe('1rem');
    
    // space-8 should be 32px (2rem)
    expect(getTokenValue(cssContent, 'space-8')).toBe('2rem');
  });
});

// ============================================================================
// Typography System Tests
// ============================================================================

describe('Typography System', () => {
  it('should have font family tokens defined', () => {
    expect(hasToken(cssContent, 'font-display')).toBe(true);
    expect(hasToken(cssContent, 'font-body')).toBe(true);
    expect(hasToken(cssContent, 'font-mono')).toBe(true);
  });

  it('should use Outfit for display font', () => {
    const value = getTokenValue(cssContent, 'font-display');
    expect(value).toContain('Outfit');
  });

  it('should use DM Sans for body font', () => {
    const value = getTokenValue(cssContent, 'font-body');
    expect(value).toContain('DM Sans');
  });

  it('should use JetBrains Mono for mono font', () => {
    const value = getTokenValue(cssContent, 'font-mono');
    expect(value).toContain('JetBrains Mono');
  });

  it('should have font size tokens defined', () => {
    const fontSizeTokens = [
      'text-xs', 'text-sm', 'text-base', 'text-lg',
      'text-xl', 'text-2xl', 'text-3xl', 'text-4xl',
    ];
    
    fontSizeTokens.forEach(token => {
      expect(hasToken(cssContent, token), `Missing font size token: --${token}`).toBe(true);
    });
  });

  it('should have font weight tokens defined', () => {
    expect(hasToken(cssContent, 'font-regular')).toBe(true);
    expect(hasToken(cssContent, 'font-medium')).toBe(true);
    expect(hasToken(cssContent, 'font-semibold')).toBe(true);
    expect(hasToken(cssContent, 'font-bold')).toBe(true);
  });

  it('should have correct font weight values', () => {
    expect(getTokenValue(cssContent, 'font-regular')).toBe('400');
    expect(getTokenValue(cssContent, 'font-medium')).toBe('500');
    expect(getTokenValue(cssContent, 'font-semibold')).toBe('600');
    expect(getTokenValue(cssContent, 'font-bold')).toBe('700');
  });
});

// ============================================================================
// Border Radius Tests
// ============================================================================

describe('Border Radius', () => {
  it('should have radius tokens defined', () => {
    const radiusTokens = [
      'radius-none', 'radius-sm', 'radius-md', 'radius-lg',
      'radius-xl', 'radius-2xl', 'radius-full',
    ];
    
    radiusTokens.forEach(token => {
      expect(hasToken(cssContent, token), `Missing radius token: --${token}`).toBe(true);
    });
  });

  it('should have correct radius values', () => {
    expect(getTokenValue(cssContent, 'radius-none')).toBe('0');
    expect(getTokenValue(cssContent, 'radius-sm')).toBe('0.25rem');
    expect(getTokenValue(cssContent, 'radius-md')).toBe('0.5rem');
    expect(getTokenValue(cssContent, 'radius-full')).toBe('9999px');
  });
});

// ============================================================================
// Shadow Tests
// ============================================================================

describe('Shadows', () => {
  it('should have shadow tokens defined', () => {
    const shadowTokens = [
      'shadow-sm', 'shadow-md', 'shadow-lg', 'shadow-xl',
    ];
    
    shadowTokens.forEach(token => {
      expect(hasToken(cssContent, token), `Missing shadow token: --${token}`).toBe(true);
    });
  });

  it('should have glow shadows for cyberpunk effect', () => {
    expect(hasToken(cssContent, 'glow-cyan')).toBe(true);
    expect(hasToken(cssContent, 'glow-violet')).toBe(true);
  });
});

// ============================================================================
// Transition Tests
// ============================================================================

describe('Transitions', () => {
  it('should have transition tokens defined', () => {
    const transitionTokens = [
      'transition-fast', 'transition-base', 'transition-slow', 'transition-slower',
    ];
    
    transitionTokens.forEach(token => {
      expect(hasToken(cssContent, token), `Missing transition token: --${token}`).toBe(true);
    });
  });

  it('should have transition durations in correct format', () => {
    const fast = getTokenValue(cssContent, 'transition-fast');
    const base = getTokenValue(cssContent, 'transition-base');
    const slow = getTokenValue(cssContent, 'transition-slow');
    
    // Should contain ms unit
    expect(fast).not.toBeNull();
    expect(fast).toMatch(/\d+ms/);
    expect(base).not.toBeNull();
    expect(base).toMatch(/\d+ms/);
    expect(slow).not.toBeNull();
    expect(slow).toMatch(/\d+ms/);
  });
});

// ============================================================================
// Z-Index Tests
// ============================================================================

describe('Z-Index', () => {
  it('should have z-index tokens defined', () => {
    const zIndexTokens = [
      'z-dropdown', 'z-sticky', 'z-fixed',
      'z-modal-backdrop', 'z-modal', 'z-popover',
      'z-tooltip', 'z-toast',
    ];
    
    zIndexTokens.forEach(token => {
      expect(hasToken(cssContent, token), `Missing z-index token: --${token}`).toBe(true);
    });
  });
});

// ============================================================================
// Cyberpunk Theme Tests
// ============================================================================

describe('Cyberpunk Theme', () => {
  it('should have glass card styles defined', () => {
    expect(cssContent).toContain('.glass-card');
  });

  it('should have neon border effect defined', () => {
    expect(cssContent).toContain('.neon-border');
  });

  it('should have text gradient effect defined', () => {
    expect(cssContent).toContain('.text-gradient');
  });

  it('should have text glow effect defined', () => {
    expect(cssContent).toContain('.text-glow');
  });

  it('should have animations defined', () => {
    expect(cssContent).toContain('@keyframes fadeIn');
    expect(cssContent).toContain('@keyframes fadeInUp');
    expect(cssContent).toContain('@keyframes slideInLeft');
    expect(cssContent).toContain('@keyframes slideInRight');
    expect(cssContent).toContain('@keyframes glow');
  });

  it('should have hover effects defined', () => {
    expect(cssContent).toContain('.hover-lift');
    expect(cssContent).toContain('.hover-scale');
    expect(cssContent).toContain('.hover-glow');
  });

  it('should have cyber button styles defined', () => {
    expect(cssContent).toContain('.btn-cyber');
  });

  it('should have cyber input styles defined', () => {
    expect(cssContent).toContain('.input-cyber');
  });

  it('should have cyber badge styles defined', () => {
    expect(cssContent).toContain('.badge-cyber');
  });
});

// ============================================================================
// Accessibility Tests
// ============================================================================

describe('Accessibility', () => {
  it('should have reduced motion media query', () => {
    expect(cssContent).toContain('@media (prefers-reduced-motion: reduce)');
  });

  it('should have focus visible styles', () => {
    expect(cssContent).toContain(':focus-visible');
  });
});
