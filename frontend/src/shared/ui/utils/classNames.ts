/**
 * CSS类名构建工具函数
 * 
 * 消除组件中重复的类名构建逻辑
 */

/**
 * 构建条件类名字符串
 * @param baseClass 基础类名
 * @param modifiers 修饰符对象，键为修饰符名，值为是否应用
 * @param additionalClasses 额外的类名数组
 * @returns 拼接后的类名字符串
 * 
 * @example
 * const className = buildConditionalClasses(
 *   'cyber-input',
 *   { invalid: hasError, disabled: isDisabled },
 *   ['custom-class']
 * );
 * // 结果: 'cyber-input cyber-input--invalid custom-class'
 */
export function buildConditionalClasses(
  baseClass: string,
  modifiers: Record<string, boolean>,
  additionalClasses: string[] = []
): string {
  const modifierClasses = Object.entries(modifiers)
    .filter(([_, shouldApply]) => shouldApply)
    .map(([modifier]) => `${baseClass}--${modifier}`);

  return [...additionalClasses, ...modifierClasses]
    .filter(Boolean)
    .join(' ');
}

/**
 * 构建包装器类名
 * @param wrapperBaseClass 包装器基础类名
 * @param modifiers 修饰符对象
 * @returns 拼接后的包装器类名字符串
 * 
 * @example
 * const wrapperClass = buildWrapperClasses(
 *   'cyber-checkbox-wrapper',
 *   { invalid: hasError, disabled: isDisabled }
 * );
 * // 结果: 'cyber-checkbox-wrapper cyber-checkbox-wrapper--invalid'
 */
export function buildWrapperClasses(
  wrapperBaseClass: string,
  modifiers: Record<string, boolean>
): string {
  return buildConditionalClasses(wrapperBaseClass, modifiers);
}

/**
 * 构建输入控件类名
 * @param inputBaseClass 输入控件基础类名
 * @param modifiers 修饰符对象
 * @returns 拼接后的输入控件类名字符串
 * 
 * @example
 * const inputClass = buildInputClasses(
 *   'cyber-checkbox',
 *   { checked: isChecked, disabled: isDisabled }
 * );
 * // 结果: 'cyber-checkbox cyber-checkbox--checked'
 */
export function buildInputClasses(
  inputBaseClass: string,
  modifiers: Record<string, boolean>
): string {
  return buildConditionalClasses(inputBaseClass, modifiers);
}

/**
 * 构建标签类名
 * @param labelBaseClass 标签基础类名
 * @param modifiers 修饰符对象
 * @returns 拼接后的标签类名字符串
 * 
 * @example
 * const labelClass = buildLabelClasses(
 *   'cyber-input__label',
 *   { required: isRequired }
 * );
 * // 结果: 'cyber-input__label cyber-input__label--required'
 */
export function buildLabelClasses(
  labelBaseClass: string,
  modifiers: Record<string, boolean>
): string {
  return buildConditionalClasses(labelBaseClass, modifiers);
}

/**
 * 构建复合类名（基础类 + 修饰符 + 自定义类名）
 * @param baseClass 基础类名
 * @param variant 变体名
 * @param size 尺寸名
 * @param modifiers 修饰符对象
 * @param customClassName 自定义类名
 * @returns 拼接后的类名字符串
 * 
 * @example
 * const buttonClass = buildCompoundClasses(
 *   'cyber-button',
 *   'primary',
 *   'medium',
 *   { disabled: isDisabled, loading: isLoading },
 *   'my-button'
 * );
 * // 结果: 'cyber-button cyber-button--primary cyber-button--medium cyber-button--disabled my-button'
 */
export function buildCompoundClasses(
  baseClass: string,
  variant?: string,
  size?: string,
  modifiers: Record<string, boolean> = {},
  customClassName: string = ''
): string {
  const classes: string[] = [baseClass];

  if (variant) {
    classes.push(`${baseClass}--${variant}`);
  }

  if (size) {
    classes.push(`${baseClass}--${size}`);
  }

  const modifierClasses = Object.entries(modifiers)
    .filter(([_, shouldApply]) => shouldApply)
    .map(([modifier]) => `${baseClass}--${modifier}`);

  classes.push(...modifierClasses);

  if (customClassName) {
    classes.push(customClassName);
  }

  return classes.filter(Boolean).join(' ');
}
