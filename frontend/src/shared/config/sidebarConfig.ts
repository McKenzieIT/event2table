export interface SidebarItem {
  id: string;
  label: string;
  shortLabel: string;
  icon: string;
  path: string;
  tooltip: string;
}

export interface SidebarGroup {
  id: string;
  title: string;
  defaultExpanded: boolean;
  items: SidebarItem[];
}

export interface GameChipConfig {
  icon: string;
  label: string;
  shortLabel: string;
  defaultText: string;
}

export const SIDEBAR_GROUPS: SidebarGroup[] = [
  {
    id: 'dashboard',
    title: '仪表板',
    defaultExpanded: true,
    items: [
      {
        id: 'overview',
        label: '概览',
        shortLabel: '概览',
        icon: 'bi-speedometer2',
        path: '/',
        tooltip: '仪表板'
      }
    ]
  },
  {
    id: 'event-nodes',
    title: '事件节点',
    defaultExpanded: true,
    items: [
      {
        id: 'event-node-builder',
        label: '事件节点构建器',
        shortLabel: '节点',
        icon: 'bi-diagram-3',
        path: '/event-node-builder',
        tooltip: '事件节点构建器'
      },
      {
        id: 'manage-nodes',
        label: '事件节点管理',
        shortLabel: '管理',
        icon: 'bi-diagram-3-fill',
        path: '/event-nodes',
        tooltip: '事件节点管理'
      }
    ]
  },
  {
    id: 'hql-generation',
    title: 'HQL生成',
    defaultExpanded: true,
    items: [
      {
        id: 'canvas',
        label: 'HQL构建画布',
        shortLabel: '画布',
        icon: 'bi-diagram-3',
        path: '/canvas',
        tooltip: 'HQL构建画布'
      },
      {
        id: 'flows',
        label: 'HQL流程管理',
        shortLabel: '流程',
        icon: 'bi-git',
        path: '/flows',
        tooltip: 'HQL流程管理'
      }
    ]
  },
  {
    id: 'data-management',
    title: '数据管理',
    defaultExpanded: false,
    items: [
      {
        id: 'categories',
        label: '分类管理',
        shortLabel: '分类',
        icon: 'bi-tags',
        path: '/categories',
        tooltip: '分类管理'
      },
      {
        id: 'events',
        label: '日志事件',
        shortLabel: '事件',
        icon: 'bi-journal-code',
        path: '/events',
        tooltip: '日志事件'
      },
      {
        id: 'parameters',
        label: '参数管理',
        shortLabel: '参数',
        icon: 'bi-sliders',
        path: '/parameters',
        tooltip: '参数管理'
      },
      {
        id: 'common-params',
        label: '公参管理',
        shortLabel: '公参',
        icon: 'bi-diagram-3',
        path: '/common-params',
        tooltip: '公参管理'
      }
    ]
  }
];

export const GAME_CHIP_CONFIG: GameChipConfig = {
  icon: 'bi-controller',
  label: '游戏选择',
  shortLabel: '游戏',
  defaultText: '选择游戏'
};
