// @ts-nocheck - TypeScript检查暂禁用
/**
 * @shared/ui Component Library
 *
 * Cyberpunk Lab Theme - Production-Ready Components
 *
 * Components:
 * - Button: Primary, Secondary, Ghost, Danger variants
 * - Card: Glassmorphism cards with hover glow
 * - Input: Text, password, number inputs with focus glow
 * - TextArea: Multi-line text input
 * - Table: Data tables with striped rows and subtle hover
 * - Modal: Glassmorphism modals with backdrop blur
 * - Badge: Status badges with glowing accents
 * - Toast: Notification toasts with auto-dismiss
 * - Select: Dropdown selector with search
 * - Checkbox: Custom checkbox with three states
 * - Radio: Radio button for single-select groups
 * - Switch: Toggle switch for binary states
 * - Spinner: CSS-only loading indicator
 *
 * @example
 * import { Button, Card, Input, TextArea, useToast } from '@shared/ui';
 *
 * function MyPage() {
 *   const { success } = useToast();
 *
 *   return (
 *     <Card>
 *       <Card.Header>
 *         <Card.Title>Data Generator</Card.Title>
 *       </Card.Header>
 *       <Card.Body>
 *         <Input type="text" label="Game Name" placeholder="Enter name..." />
 *         <TextArea label="Description" rows={4} />
 *         <Button variant="primary" onClick={() => success('Generated successfully!')}>
 *           Generate
 *         </Button>
 *       </Card.Body>
 *     </Card>
 *   );
 * }
 */

// Export all components
export { default as Button } from './Button/Button';
export { default as Card } from './Card/Card';
export { default as Input } from './Input/Input';
export { default as TextArea } from './TextArea/TextArea';
export { default as Table } from './Table/Table';
export { default as Modal, BaseModal } from './BaseModal/BaseModal';
export { default as Badge } from './Badge/Badge';
export { ToastProvider, useToast } from './Toast/Toast';
export type { ToastType } from './Toast/Toast';
export { default as Select } from './Select/Select';
export { default as Checkbox } from './Checkbox/Checkbox';
export { default as Radio } from './Radio/Radio';
export { default as Switch } from './Switch/Switch';
export { default as Spinner } from './Spinner/Spinner';
export { default as PageLoader } from './PageLoader/PageLoader';
export { default as ErrorState } from './ErrorState/ErrorState';
export { default as EmptyState } from './EmptyState/EmptyState';

// Special components
export { SelectGamePrompt } from './SelectGamePrompt';
export { ConfirmDialog } from './BaseModal/ConfirmDialog';
export { SearchInput } from './SearchInput/SearchInput';
