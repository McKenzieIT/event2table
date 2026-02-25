export interface BreadcrumbItem {
  label: string;
  icon?: string;
  parent?: string;
  to?: string;
  active?: boolean;
}

export interface BreadcrumbConfig {
  label: string;
  icon?: string;
  parent?: string;
}

export const breadcrumbConfig: Record<string, BreadcrumbConfig> = {
  '/': { label: '首页', icon: 'bi-house' },

  '/canvas': { label: 'HQL画布', parent: '/' },
  '/event-node-builder': { label: '事件节点构建器', parent: '/' },
  '/flows': { label: 'HQL流程管理', parent: '/' },

  '/categories': { label: '分类管理', parent: '/' },
  
  '/events': { label: '日志事件', parent: '/', icon: 'bi-list-check' },
  '/events/create': { label: '新建事件', parent: '/events' },
  '/events/:id': { label: '事件详情', parent: '/events' },
  '/events/:id/edit': { label: '编辑事件', parent: '/events' },
  
  '/common-params': { label: '公共参数', parent: '/' },
  
  '/parameters': { label: '参数管理', parent: '/', icon: 'bi-gear' },
  '/parameter-dashboard': { label: '参数分析', parent: '/parameters' },
  '/parameter-usage': { label: '参数使用分析', parent: '/parameters' },
  '/parameter-history': { label: '参数变更历史', parent: '/parameters' },
  '/parameter-network': { label: '参数关系网络', parent: '/parameters' },
  '/parameter-analysis': { label: '参数分析', parent: '/parameters' },
  '/parameters/compare': { label: '参数对比', parent: '/parameters' },
  '/parameters/enhanced': { label: '增强参数管理', parent: '/parameters' },
  
  '/hql-manage': { label: 'HQL管理', parent: '/' },
  '/hql-results': { label: 'HQL结果', parent: '/' },
  '/hql/:id/edit': { label: '编辑HQL', parent: '/hql-manage' },
  
  '/import-events': { label: '导入事件', parent: '/' },
  
  '/api-docs': { label: 'API文档', parent: '/' },
  '/batch-operations': { label: '批量操作', parent: '/' },
  '/validation-rules': { label: '验证规则', parent: '/' },
  '/log-detail': { label: '日志详情', parent: '/' },
  
  '/generate': { label: 'HQL生成', parent: '/' },
  '/generate/result': { label: '生成结果', parent: '/generate' },
  
  '/flow-builder': { label: '流程构建器', parent: '/' },
  '/field-builder': { label: '字段构建器', parent: '/' },
  '/event-nodes': { label: '事件节点管理', parent: '/' },
  
  '/alter-sql/:paramId': { label: '修改SQL', parent: '/parameters' },
  '/alter-sql-builder': { label: 'SQL构建器', parent: '/' },
  
  '/logs/create': { label: '新建日志', parent: '/log-detail' },
  '/logs/:id/edit': { label: '编辑日志', parent: '/log-detail' },
};

export function generateBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [{ label: '首页', to: '/' }];
  
  let currentPath = '';
  
  for (const segment of segments) {
    currentPath += `/${segment}`;
    
    let config = breadcrumbConfig[currentPath];
    
    if (!config) {
      const isNumericId = /^\d+$/.test(segment);
      if (isNumericId) {
        const parentPath = currentPath.replace(`/${segment}`, '');
        config = breadcrumbConfig[parentPath];
        if (config) {
          breadcrumbs.push({ label: `${config.label} #${segment}`, to: currentPath });
          continue;
        }
      }
    }
    
    if (config) {
      breadcrumbs.push({ label: config.label, to: currentPath });
    } else {
      breadcrumbs.push({ label: segment, to: currentPath });
    }
  }
  
  if (breadcrumbs.length > 0) {
    breadcrumbs[breadcrumbs.length - 1].active = true;
    delete breadcrumbs[breadcrumbs.length - 1].to;
  }
  
  return breadcrumbs;
}
