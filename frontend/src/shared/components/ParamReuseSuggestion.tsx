// ⚠️ REACT PERF: Missing React.memo/useMemo/useCallback
// TODO: Add appropriate React optimization:
//   - Large components (>500 chars): Add React.memo()
//   - Expensive computations: Add useMemo()
//   - useEffect dependencies: Add useCallback()
// See: docs/reports/2026-03-05/PERFORMANCE-OPTIMIZATION-DETAILED-REPORT.md

/**
 * ParamReuseSuggestion 组件 - 参数复用建议提示
 *
 * 当用户输入的参数名存在于参数库中时，显示此提示组件
 * 允许用户选择"关联到库"或"创建独立参数"
 *
 * @example
 * <ParamReuseSuggestion
 *   libraryParam={{
 *     param_name: 'accountId',
 *     param_name_cn: '灵犀账号id',
 *     template_name: 'int',
 *     usage_count: 1507
 *   }}
 *   onLinkToLibrary={() => }
 *   onCreateIndependent={() => }
 * />
 */

import React from 'react';
import { Button } from '@shared/ui';

export interface LibraryParamInfo {
  param_name: string;
  param_name_cn: string;
  template_name: string;
  usage_count: number;
}

export interface ParamReuseSuggestionProps {
  libraryParam: LibraryParamInfo;
  onLinkToLibrary: () => void;
  onCreateIndependent: () => void;
}

export function ParamReuseSuggestion({
  libraryParam,
  onLinkToLibrary,
  onCreateIndependent
}: ParamReuseSuggestionProps) {
  return (
    <div className="param-reuse-suggestion glass-card p-3 mb-3">
      <div className="d-flex align-items-center gap-2 mb-2">
        <span className="suggestion-icon">💡</span>
        <span className="suggestion-text">
          参数 '<strong>{libraryParam.param_name}</strong>' 已存在于库中
        </span>
      </div>
      <div className="suggestion-details text-muted small mb-3">
        <div>类型: {libraryParam.template_name}</div>
        <div>中文名: {libraryParam.param_name_cn}</div>
        <div>使用次数: {libraryParam.usage_count}</div>
      </div>
      <div className="suggestion-actions d-flex gap-2">
        <Button variant="primary" size="sm" onClick={onLinkToLibrary}>
          关联到库
        </Button>
        <Button variant="secondary" size="sm" onClick={onCreateIndependent}>
          创建独立参数
        </Button>
      </div>
    </div>
  );
}
