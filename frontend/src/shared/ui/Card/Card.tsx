/**
 * Card Component - Glassmorphism Style
 *
 * A frosted glass effect card with subtle glow border and shadow.
 * Optimized for OLED displays with pure black backgrounds.
 *
 * Optimized with React.memo to prevent unnecessary re-renders.
 *
 * @example
 * // Stats card
 * <Card className="card-stats">
 *   <Card.Header>
 *     <Card.Title>Games</Card.Title>
 *   </Card.Header>
 *   <Card.Body>
 *     <StatsValue value={11} />
 *   </Card.Body>
 * </Card>
 *
 * @example
 * // Interactive card
 * <Card hoverable>
 *   <Card.Content>...</Card.Content>
 * </Card>
 *
 * @example
 * // Clickable card (as Link)
 * <Card as={Link} to="/games" hoverable>
 *   <Card.Content>Manage Games</Card.Content>
 * </Card>
 */

import React, {
  forwardRef,
  ForwardRefRenderFunction,
  memo,
  type HTMLAttributes,
  type ReactNode,
} from 'react';

import './Card.css';

/**
 * Card variant types
 */
export type CardVariant = 'default' | 'glass' | 'solid' | 'bordered';

/**
 * Card padding sizes
 */
export type CardPadding = 'none' | 'sm' | 'md' | 'lg' | 'reset';

/**
 * Props for Card component
 */
export interface CardProps extends Omit<HTMLAttributes<HTMLElement>, 'as'> {
  /** CSS class name */
  className?: string;
  /** Card variant style */
  variant?: CardVariant;
  /** Enable hover effect (alias for hover) */
  hoverable?: boolean;
  /** Enable glowing effect */
  glowing?: boolean;
  /** Enable hover effect (alias for hoverable) */
  hover?: boolean;
  /** Padding size */
  padding?: CardPadding;
  /** Render as different element type */
  as?: React.ElementType;
  /** Card content */
  children: ReactNode;
}

/**
 * Props for Card sub-components
 */
export interface CardSubComponentProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  className?: string;
}

// Memoized sub-components (defined first for proper hoisting)
const CardHeader = memo<CardSubComponentProps>(function CardHeader({ children, className = '', ...props }) {
  return (
    <div className={[`cyber-card__header`, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
});

const CardBody = memo<CardSubComponentProps>(function CardBody({ children, className = '', ...props }) {
  return (
    <div className={[`cyber-card__body`, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
});

const CardFooter = memo<CardSubComponentProps>(function CardFooter({ children, className = '', ...props }) {
  return (
    <div className={[`cyber-card__footer`, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
});

const CardTitle = memo<CardSubComponentProps>(function CardTitle({ children, className = '', ...props }) {
  return (
    <h3 className={[`cyber-card__title`, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </h3>
  );
});

// CardContent is an alias for CardBody
const CardContent = CardBody;

const Card: ForwardRefRenderFunction<HTMLElement, CardProps> = ({
  children,
  className = '',
  variant = 'default',
  hoverable = false,
  glowing = false,
  hover = false, // Alias for hoverable
  padding = 'md',
  as: Component = 'div',
  ...props
}, ref) => {
  // Support both 'hover' and 'hoverable' props
  const isHoverable = hover || hoverable;

  const cardClass = [
    'cyber-card',
    `cyber-card--${variant}`,
    isHoverable && 'cyber-card--hoverable',
    glowing && 'cyber-card--glowing',
    `cyber-card--padding-${padding}`,
    className
  ].filter(Boolean).join(' ');

  // Filter out boolean props and 'as' prop before spreading to DOM
  const { hoverable: _, glowing: __, hover: ___, as: ____, ...domProps } = props as any;

  return (
    <Component ref={ref as any} className={cardClass} {...domProps}>
      {children}
    </Component>
  );
};

Card.displayName = 'Card';

const ForwardedCard = forwardRef<HTMLElement, CardProps>(Card);

// Memoize Card component
const MemoizedCard = memo(ForwardedCard, (prevProps, nextProps) => {
  return (
    prevProps.variant === nextProps.variant &&
    (prevProps.hover || prevProps.hoverable) === (nextProps.hover || nextProps.hoverable) &&
    prevProps.glowing === nextProps.glowing &&
    prevProps.padding === nextProps.padding &&
    prevProps.className === nextProps.className &&
    prevProps.as === nextProps.as &&
    prevProps.children === nextProps.children
  );
});

MemoizedCard.displayName = 'Card';

// Define CardWithSubComponents interface with all sub-components
interface CardWithSubComponents 
  extends React.MemoExoticComponent<React.ForwardRefExoticComponent<CardProps & React.RefAttributes<HTMLElement>>> {
  /** Card header section */
  Header: typeof CardHeader;
  /** Card body section */
  Body: typeof CardBody;
  /** Card footer section */
  Footer: typeof CardFooter;
  /** Card title */
  Title: typeof CardTitle;
  /** Card content (alias for Body) */
  Content: typeof CardBody;
}

// Attach sub-components to the memoized Card
const CardComponent = MemoizedCard as CardWithSubComponents;
CardComponent.Header = CardHeader;
CardComponent.Body = CardBody;
CardComponent.Footer = CardFooter;
CardComponent.Title = CardTitle;
CardComponent.Content = CardContent;

// Export sub-components as named exports for direct import
export { CardHeader, CardBody, CardFooter, CardTitle, CardContent };

// Export the main Card component with sub-components attached
export { CardComponent as Card };

// Default export for convenience
export default CardComponent;