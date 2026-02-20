import { ButtonHTMLAttributes, ReactNode, ForwardRefRenderFunction } from 'react';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children?: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'outline-primary' | 'outline-danger' | 'success' | 'warning' | 'info';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ComponentType;
  className?: string;
}

declare const Button: ForwardRefRenderFunction<HTMLButtonElement, ButtonProps>;

export default Button;
