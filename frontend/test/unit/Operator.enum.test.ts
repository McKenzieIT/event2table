import { Operator } from '@/shared/types/hql-types';

describe('Operator Enum Consistency', () => {
  test('should use short form enum values matching backend', () => {
    /**
     * 后端期望的枚举值:
     * - EQ (而非 EQUAL)
     * - NE (而非 NOT_EQUAL)
     * - GT (而非 GREATER_THAN)
     * - LT (而非 LESS_THAN)
     * - GTE (而非 GREATER_EQUAL)
     * - LTE (而非 LESS_EQUAL)
     *
     * 这个测试会先失败，因为当前前端使用长形式
     */

    // 验证基本运算符使用简短形式
    expect(Operator.EQ).toBe('=');
    expect(Operator.NE).toBe('!=');
    expect(Operator.GT).toBe('>');
    expect(Operator.LT).toBe('<');
    expect(Operator.GTE).toBe('>=');
    expect(Operator.LTE).toBe('<=');

    // 验证复杂运算符保持不变
    expect(Operator.LIKE).toBe('LIKE');
    expect(Operator.IN).toBe('IN');
    expect(Operator.NOT_IN).toBe('NOT IN');
    expect(Operator.IS_NULL).toBe('IS NULL');
    expect(Operator.IS_NOT_NULL).toBe('IS NOT NULL');
  });

  test('should not have old long-form enum values', () => {
    /**
     * 确保不再使用旧的长形式枚举值
     */
    expect('EQUAL' in Operator).toBe(false);
    expect('NOT_EQUAL' in Operator).toBe(false);
    expect('GREATER_THAN' in Operator).toBe(false);
    expect('LESS_THAN' in Operator).toBe(false);
  });
});
