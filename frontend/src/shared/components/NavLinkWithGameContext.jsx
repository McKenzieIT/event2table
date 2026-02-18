import React from 'react';
import { Link } from 'react-router-dom';
import { useGameStore } from '@/stores/gameStore';

/**
 * Smart navigation link component - automatically attaches game_gid parameter
 *
 * This component reads the current game context from the Zustand store and
 * automatically appends the game_gid parameter to the navigation URL.
 *
 * @param {string} to - Target path
 * @param {string} className - CSS class name
 * @param {ReactNode} children - Child elements
 * @param {object} props - Additional Link props
 *
 * @example
 * <NavLinkWithGameContext to="/parameter-usage" className="btn">
 *   Usage Analysis
 * </NavLinkWithGameContext>
 *
 * If current game has gid=10000147, this will navigate to:
 * /parameter-usage?game_gid=10000147
 */
export function NavLinkWithGameContext({ to, className, children, ...props }) {
  const { currentGame } = useGameStore();

  // Automatically append game_gid if a game is selected
  const finalTo = currentGame?.gid
    ? `${to}?game_gid=${currentGame.gid}`
    : to;

  return (
    <Link to={finalTo} className={className} {...props}>
      {children}
    </Link>
  );
}

export default NavLinkWithGameContext;
