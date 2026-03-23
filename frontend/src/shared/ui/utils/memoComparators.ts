/**
 * React.memo 比较函数集合
 * 
 * 消除组件中重复的 memo 比较逻辑
 */

/**
 * 基础 props 比较函数
 * 比较常见的 props：className, disabled, error
 */
export function compareBaseProps(prevProps: any, nextProps: any): boolean {
  return (
    prevProps.className === nextProps.className &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.error === nextProps.error
  );
}

/**
 * 值和事件处理器比较函数
 * 比较值和事件处理器
 */
export function compareValueAndHandlers(prevProps: any, nextProps: any): boolean {
  return (
    prevProps.value === nextProps.value &&
    prevProps.onChange === nextProps.onChange &&
    prevProps.onBlur === nextProps.onBlur &&
    prevProps.onFocus === nextProps.onFocus
  );
}

/**
 * Checkbox/Radio/Switch 比较函数
 * 比较选中状态、禁用状态、错误状态和变更处理器
 */
export function compareToggleProps(prevProps: any, nextProps: any): boolean {
  return (
    prevProps.checked === nextProps.checked &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.error === nextProps.error &&
    prevProps.onChange === nextProps.onChange
  );
}

/**
 * Checkbox 特有比较函数（包含 indeterminate）
 */
export function compareCheckboxProps(prevProps: any, nextProps: any): boolean {
  return (
    prevProps.checked === nextProps.checked &&
    prevProps.indeterminate === nextProps.indeterminate &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.error === nextProps.error &&
    prevProps.onChange === nextProps.onChange
  );
}

/**
 * Input 比较函数
 * 比较输入框相关 props
 */
export function compareInputProps(prevProps: any, nextProps: any): boolean {
  return (
    prevProps.type === nextProps.type &&
    prevProps.label === nextProps.label &&
    prevProps.placeholder === nextProps.placeholder &&
    prevProps.error === nextProps.error &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.required === nextProps.required &&
    prevProps.helperText === nextProps.helperText &&
    prevProps.className === nextProps.className &&
    prevProps.value === nextProps.value &&
    prevProps.onChange === nextProps.onChange &&
    prevProps.onBlur === nextProps.onBlur &&
    prevProps.onFocus === nextProps.onFocus &&
    prevProps.readOnly === nextProps.readOnly &&
    prevProps.autoFocus === nextProps.autoFocus &&
    prevProps.name === nextProps.name &&
    prevProps.maxLength === nextProps.maxLength &&
    prevProps.minLength === nextProps.minLength
  );
}

/**
 * TextArea 比较函数
 */
export function compareTextAreaProps(prevProps: any, nextProps: any): boolean {
  return (
    prevProps.value === nextProps.value &&
    prevProps.error === nextProps.error &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.onChange === nextProps.onChange
  );
}

/**
 * Button 比较函数
 */
export function compareButtonProps(prevProps: any, nextProps: any): boolean {
  return (
    prevProps.variant === nextProps.variant &&
    prevProps.size === nextProps.size &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.loading === nextProps.loading &&
    prevProps.className === nextProps.className &&
    prevProps.children === nextProps.children &&
    prevProps.onClick === nextProps.onClick
  );
}

/**
 * Badge 比较函数
 */
export function compareBadgeProps(prevProps: any, nextProps: any): boolean {
  return (
    prevProps.variant === nextProps.variant &&
    prevProps.size === nextProps.size &&
    prevProps.dot === nextProps.dot &&
    prevProps.pill === nextProps.pill &&
    prevProps.className === nextProps.className &&
    prevProps.children === nextProps.children
  );
}

/**
 * Spinner 比较函数
 */
export function compareSpinnerProps(prevProps: any, nextProps: any): boolean {
  return (
    prevProps.size === nextProps.size &&
    prevProps.label === nextProps.label
  );
}

/**
 * SearchInput 比较函数
 */
export function compareSearchInputProps(prevProps: any, nextProps: any): boolean {
  return (
    prevProps.value === nextProps.value &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.onChange === nextProps.onChange &&
    prevProps.onClear === nextProps.onClear &&
    prevProps.placeholder === nextProps.placeholder &&
    prevProps.debounceMs === nextProps.debounceMs &&
    prevProps.className === nextProps.className
  );
}
