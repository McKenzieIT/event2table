/**
 * ParameterCard - Individual Parameter Card Component
 *
 * Displays parameter information with type badge and edit functionality.
 * Uses CHANGE_PARAMETER_TYPE mutation for type updates.
 *
 * @example
 * <ParameterCard
 *   parameter={{
 *     id: 1,
 *     paramName: 'accountId',
 *     paramNameCn: '账号ID',
 *     type: 'base',
 *     gameGid: 10000147
 *   }}
 *   onEdit={(param) => setSelectedParam(param)}
 * />
 *
 * Props:
 * @param {Object} parameter - Parameter object
 * @param {number} parameter.id - Parameter ID
 * @param {string} parameter.paramName - Parameter name
 * @param {string} parameter.paramNameCn - Parameter Chinese name
 * @param {string} parameter.type - Parameter type (base/param/custom)
 * @param {number} parameter.gameGid - Game GID
 * @param {Function} onEdit - Edit button handler
 */

import React from 'react';
import { Badge } from '@shared/ui';

const ParameterCard = ({ parameter, onEdit }) => {
  const getTypeBadgeColor = (type) => {
    const colors = {
      base: 'bg-blue-500/20 text-blue-300 border-blue-500/30 hover:bg-blue-500/30',
      param: 'bg-purple-500/20 text-purple-300 border-purple-500/30 hover:bg-purple-500/30',
      custom: 'bg-green-500/20 text-green-300 border-green-500/30 hover:bg-green-500/30',
    };
    return colors[type] || 'bg-gray-500/20 text-gray-300 border-gray-500/30';
  };

  const getTypeLabel = (type) => {
    const labels = {
      base: '基础字段',
      param: '事件参数',
      custom: '自定义',
    };
    return labels[type] || type;
  };

  return (
    <div className="group p-4 bg-slate-800/30 rounded-lg border border-slate-700 hover:border-cyan-500/50 transition-all">
      <div className="flex items-start justify-between">
        {/* Parameter Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <code className="text-cyan-400 font-semibold text-lg">{parameter.paramName}</code>
            <Badge className={getTypeBadgeColor(parameter.type)} size="sm">
              {getTypeLabel(parameter.type)}
            </Badge>
          </div>

          {parameter.paramNameCn && (
            <div className="text-sm text-slate-400 mb-2">{parameter.paramNameCn}</div>
          )}

          {/* Additional metadata could go here */}
          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14" />
              </svg>
              ID: {parameter.id}
            </span>
            {parameter.eventCount !== undefined && (
              <span className="flex items-center gap-1">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {parameter.eventCount} 个事件
              </span>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onEdit(parameter)}
            className="p-2 text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/10 rounded-lg transition-all"
            title="编辑参数类型"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ParameterCard;
