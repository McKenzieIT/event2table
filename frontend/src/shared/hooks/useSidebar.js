// dwd_generator/static/js/react-app-shell/src/hooks/useSidebar.js
import { useState, useEffect, useCallback } from 'react';

export const useSidebar = () => {
  // 侧边栏折叠状态
  const [collapsed, setCollapsed] = useState(false);

  // 分组展开状态
  const [groupStates, setGroupStates] = useState({});

  // 从 localStorage 加载用户偏好
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
      // 保持默认状态
    }
  }, []);

  // 持久化 groupStates 到 localStorage
  useEffect(() => {
    try {
      localStorage.setItem('sidebarGroupStates', JSON.stringify(groupStates));
    } catch (error) {
      console.error('[useSidebar] Failed to save group state:', error);
    }
  }, [groupStates]);

  // 切换侧边栏折叠
  const toggleCollapsed = useCallback(() => {
    setCollapsed(prev => {
      const newState = !prev;
      try {
        localStorage.setItem('sidebarCollapsed', JSON.stringify(newState));
        // 触发事件通知其他组件
        window.dispatchEvent(new CustomEvent('sidebarToggled', { detail: newState }));
      } catch (error) {
        console.error('[useSidebar] Failed to save collapsed state:', error);
      }
      return newState;
    });
  }, []); // Empty deps - stable reference

  // 切换分组展开状态
  const toggleGroup = useCallback((groupId) => {
    setGroupStates(prev => ({
      ...prev,
      [groupId]: !prev[groupId]
    }));
  }, []);

  // 展开所有分组
  const expandAllGroups = useCallback((allGroupIds) => {
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

  // 折叠所有分组
  const collapseAllGroups = useCallback((allGroupIds) => {
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
