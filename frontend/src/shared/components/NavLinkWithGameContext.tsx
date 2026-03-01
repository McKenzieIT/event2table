import React from 'react';
import { Link, LinkProps } from 'react-router-dom';
import { useGameStore } from '@/stores/gameStore';

/**
 * Smart navigation link component - automatically attaches game_gid parameter
 *
 * This component reads the current game context from the Zustand store and
 * automatically appends the game_gid parameter to the navigation URL.
 *
 * @example
 * <NavLinkWithGameContext to="/parameter-usage" className="btn">
 *   Usage Analysis
 * </NavLinkWithGameContext>
 *
 * If current game has gid=10000147, this will navigate to:
 * /parameter-usage?game_gid=10000147
 */

export interface NavLinkWithGameContextProps extends Omit<LinkProps, 'to'> {
  to: string;
}

export function NavLinkWithGameContext({ to, className, children, ...props }: NavLinkWithGameContextProps) {
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
