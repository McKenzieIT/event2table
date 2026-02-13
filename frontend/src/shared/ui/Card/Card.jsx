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

import React from 'react';
import './Card.css';

const Card = React.forwardRef(({
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
  const { hoverable: _, glowing: __, hover: ___, as: ____, ...domProps } = props;

  return (
    <Component ref={ref} className={cardClass} {...domProps}>
      {children}
    </Component>
  );
});

Card.displayName = 'Card';

// Memoize Card component
const MemoizedCard = React.memo(Card, (prevProps, nextProps) => {
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

MemoizedCard.displayName = 'MemoizedCard';

// Memoized sub-components
Card.Header = React.memo(function CardHeader({ children, className = '', ...props }) {
  return (
    <div className={[`cyber-card__header`, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
});

Card.Body = React.memo(function CardBody({ children, className = '', ...props }) {
  return (
    <div className={[`cyber-card__body`, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
});

Card.Footer = React.memo(function CardFooter({ children, className = '', ...props }) {
  return (
    <div className={[`cyber-card__footer`, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
});

Card.Title = React.memo(function CardTitle({ children, className = '', ...props }) {
  return (
    <h3 className={[`cyber-card__title`, className].filter(Boolean).join(' ')} {...props}>
      {children}
    </h3>
  );
});

Card.Content = Card.Body; // Alias

export default MemoizedCard;
