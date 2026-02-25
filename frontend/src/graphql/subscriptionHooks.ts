/**
 * GraphQL Subscription Hooks
 * 
 * React hooks for GraphQL subscriptions
 */

import { useSubscription } from '@apollo/client/react';
import {
  ON_EVENT_UPDATED,
  ON_PARAMETER_UPDATED,
  ON_GAME_UPDATED,
  ON_CATEGORY_UPDATED,
  ON_HQL_GENERATED,
  ON_GAME_EVENTS_CHANGED,
} from './subscriptions';

/**
 * Hook to subscribe to event updates
 */
export function useEventUpdatedSubscription(gameGid: number) {
  return useSubscription(ON_EVENT_UPDATED, {
    variables: { gameGid },
  });
}

/**
 * Hook to subscribe to parameter updates
 */
export function useParameterUpdatedSubscription(eventId: number) {
  return useSubscription(ON_PARAMETER_UPDATED, {
    variables: { eventId },
    skip: !eventId,
  });
}

/**
 * Hook to subscribe to game updates
 */
export function useGameUpdatedSubscription(gid: number) {
  return useSubscription(ON_GAME_UPDATED, {
    variables: { gid },
    skip: !gid,
  });
}

/**
 * Hook to subscribe to category updates
 */
export function useCategoryUpdatedSubscription(gameGid: number) {
  return useSubscription(ON_CATEGORY_UPDATED, {
    variables: { gameGid },
    skip: !gameGid,
  });
}

/**
 * Hook to subscribe to HQL generation updates
 */
export function useHQLGeneratedSubscription(gameGid: number) {
  return useSubscription(ON_HQL_GENERATED, {
    variables: { gameGid },
    skip: !gameGid,
  });
}

/**
 * Hook to subscribe to all game events changes
 */
export function useGameEventsChangedSubscription(gameGid: number) {
  return useSubscription(ON_GAME_EVENTS_CHANGED, {
    variables: { gameGid },
    skip: !gameGid,
  });
}
