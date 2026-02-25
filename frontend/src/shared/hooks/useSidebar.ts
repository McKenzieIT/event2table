import { useState, useEffect, useCallback } from 'react';

export interface UseSidebarReturn {
  collapsed: boolean;
  groupStates: Record<string, boolean>;
  toggleCollapsed: () => void;
  toggleGroup: (groupId: string) => void;
  expandAllGroups: (allGroupIds: string[]) => void;
  collapseAllGroups: (allGroupIds: string[]) => void;
}

export const useSidebar = (): UseSidebarReturn => {
  const [collapsed, setCollapsed] = useState(false);
  const [groupStates, setGroupStates] = useState<Record<string, boolean>>({});

  useEffect(() => {
    try {
      const savedCollapsed = localStorage.getItem('sidebarCollapsed');
      const savedGroups = localStorage.getItem('sidebarGroupStates');

      if (savedCollapsed !== null) {
        setCollapsed(JSON.parse(savedCollapsed));
      }

      if (savedGroups) {
        setGroupStates(JSON.parse(savedGroups));
      }
    } catch (error) {
      console.error('[useSidebar] Failed to load sidebar state:', error);
    }
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem('sidebarGroupStates', JSON.stringify(groupStates));
    } catch (error) {
      console.error('[useSidebar] Failed to save group state:', error);
    }
  }, [groupStates]);

  const toggleCollapsed = useCallback(() => {
    setCollapsed(prev => {
      const newState = !prev;
      try {
        localStorage.setItem('sidebarCollapsed', JSON.stringify(newState));
        window.dispatchEvent(new CustomEvent('sidebarToggled', { detail: newState }));
      } catch (error) {
        console.error('[useSidebar] Failed to save collapsed state:', error);
      }
      return newState;
    });
  }, []);

  const toggleGroup = useCallback((groupId: string) => {
    setGroupStates(prev => ({
      ...prev,
      [groupId]: !prev[groupId]
    }));
  }, []);

  const expandAllGroups = useCallback((allGroupIds: string[]) => {
    const allExpanded = Object.fromEntries(
      allGroupIds.map(id => [id, true])
    );
    setGroupStates(allExpanded);
    try {
      localStorage.setItem('sidebarGroupStates', JSON.stringify(allExpanded));
    } catch (error) {
      console.error('[useSidebar] Failed to save group state:', error);
    }
  }, []);

  const collapseAllGroups = useCallback((allGroupIds: string[]) => {
    const allCollapsed = Object.fromEntries(
      allGroupIds.map(id => [id, false])
    );
    setGroupStates(allCollapsed);
    try {
      localStorage.setItem('sidebarGroupStates', JSON.stringify(allCollapsed));
    } catch (error) {
      console.error('[useSidebar] Failed to save group state:', error);
    }
  }, []);

  return {
    collapsed,
    groupStates,
    toggleCollapsed,
    toggleGroup,
    expandAllGroups,
    collapseAllGroups
  };
};
