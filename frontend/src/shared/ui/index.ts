// @ts-nocheck - TypeScript检查暂禁用
/**
 * @shared/ui Component Library
 *
 * Event2Table - Cyberpunk Lab Theme - Production-Ready Components
 *
 * ## 组件分类
 *
 * ### 基础组件
 * 通用 UI 组件，可在任何场景使用
 * - Button: 按钮组件，支持多种变体和尺寸
 * - Input: 输入框组件，支持文本、密码、数字等类型
 * - TextArea: 多行文本输入组件
 * - Select: 下拉选择器组件
 * - Checkbox: 复选框组件
 * - Radio: 单选按钮组件
 * - Switch: 开关切换组件
 * - Badge: 徽章标签组件
 * - Spinner: 加载指示器组件
 * - Table: 数据表格组件
 *
 * ### 业务组件
 * 与业务逻辑相关的组件
 * - SelectGamePrompt: 游戏选择提示组件
 * - ConfirmDialog: 确认对话框组件
 * - SearchInput: 搜索输入框组件
 * - BulkOperationsToolbar: 批量操作工具栏组件
 *
 * ### 布局组件
 * 用于页面布局的组件
 * - Card: 卡片容器组件
 * - Modal: 模态框组件
 * - PageLoader: 页面加载器组件
 * - Pagination: 分页组件
 * - Breadcrumb: 面包屑导航组件
 *
 * ### 状态组件
 * 显示各种状态的组件
 * - EmptyState: 空状态组件
 * - ErrorState: 错误状态组件
 * - Skeleton: 骨架屏组件
 * - Toast: 消息提示组件
 * - Loading: 加载状态组件
 *
 * ### 特殊组件
 * 特殊用途的组件
 * - ErrorBoundary: 错误边界组件
 * - CanvasErrorBoundary: 画布错误边界组件
 * - PerformanceMonitor: 性能监控组件
 * - CodeBlock: 代码块组件
 *
 * @example
 * // 基础用法
 * import { Button, Card, Input, TextArea } from '@shared/ui';
 *
 * function MyPage() {
 *   return (
 *     <Card>
 *       <Card.Header>
 *         <Card.Title>数据生成器</Card.Title>
 *       </Card.Header>
 *       <Card.Body>
 *         <Input label="游戏名称" placeholder="输入名称..." />
 *         <TextArea label="描述" rows={4} />
 *         <Button variant="primary">生成</Button>
 *       </Card.Body>
 *     </Card>
 *   );
 * }
 *
 * @example
 * // 使用 Toast
 * import { ToastProvider, useToast } from '@shared/ui';
 *
 * function App() {
 *   return (
 *     <ToastProvider>
 *       <MyComponent />
 *     </ToastProvider>
 *   );
 * }
 *
 * function MyComponent() {
 *   const { success, error, info } = useToast();
 *
 *   const handleClick = () => {
 *     success('操作成功！');
 *   };
 *
 *   return <Button onClick={handleClick}>点击</Button>;
 * }
 *
 * @example
 * // 使用 Modal
 * import { Modal } from '@shared/ui';
 *
 * function MyPage() {
 *   const [isOpen, setIsOpen] = useState(false);
 *
 *   return (
 *     <>
 *       <Button onClick={() => setIsOpen(true)}>打开对话框</Button>
 *       <Modal
 *         isOpen={isOpen}
 *         onClose={() => setIsOpen(false)}
 *         title="确认操作"
 *       >
 *         <p>确定要执行此操作吗？</p>
 *       </Modal>
 *     </>
 *   );
 * }
 */

// ============================================================================
// 基础组件
// ============================================================================

export { default as Button } from './Button/Button';
export { default as Input } from './Input/Input';
export { default as TextArea } from './TextArea/TextArea';
export { Table } from './components/Table/Table';
export { default as Badge } from './Badge/Badge';
export { default as Checkbox } from './Checkbox/Checkbox';
export { default as Radio } from './Radio/Radio';
export { default as Switch } from './Switch/Switch';
export { default as Spinner } from './Spinner/Spinner';

// Select exports
export { Select } from './components/Select/Select';
export type { SelectProps, SelectOption } from './components/Select/Select.types';

// 基础组件类型导出
export type { InputProps } from './Input/Input';
export type { TextAreaProps } from './TextArea/TextArea';
export type { TableProps, TableColumn } from './components/Table/Table.types';
export type { CheckboxProps } from './Checkbox/Checkbox';
export type { RadioProps } from './Radio/Radio';
export type { SwitchProps } from './Switch/Switch';
export type { SpinnerProps } from './Spinner/Spinner';

// ============================================================================
// 业务组件
// ============================================================================

export { default as SelectGamePrompt } from './SelectGamePrompt';
export { default as ConfirmDialog } from './ConfirmDialog/ConfirmDialog';
export { default as SearchInput } from './SearchInput/SearchInput';

// 业务组件类型导出
export type { SelectGamePromptProps } from './SelectGamePrompt';

// ============================================================================
// 布局组件
// ============================================================================

export { default as Card } from './Card/Card';
export { default as PageLoader } from './PageLoader/PageLoader';
export { default as Pagination } from './Pagination/Pagination';

// ============================================================================
// Modal组件 - 统一的模态框组件
// ============================================================================

// Modal exports
export { Modal } from './components/Modal/Modal';
export type { ModalProps, ModalSize, ModalAnimation, ModalVariant } from './components/Modal/Modal.types';


// 布局组件类型导出
export type { PaginationProps } from './Pagination/Pagination';

// ============================================================================
// 状态组件
// ============================================================================

export { default as EmptyState } from './EmptyState/EmptyState';
export { default as ErrorState } from './ErrorState/ErrorState';
export { default as Skeleton, SkeletonTable, SkeletonForm, SkeletonCard, SkeletonInline } from './Skeleton/Skeleton';
export { ToastProvider, useToast } from './Toast/Toast';
export { default as Loading } from './Loading';

// 状态组件类型导出
export type { SkeletonProps } from './Skeleton/Skeleton';
export type { ToastType } from './Toast/Toast';

// ============================================================================
// 特殊组件
// ============================================================================

export { default as ErrorBoundary } from './ErrorBoundary';
export { default as CanvasErrorBoundary } from './CanvasErrorBoundary';