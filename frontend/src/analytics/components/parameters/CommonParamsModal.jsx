/**
 * CommonParamsModal - Drawer Modal for Common Parameters
 *
 * Displays common parameters list with statistics.
 * Uses Apollo Client for GraphQL data fetching.
 *
 * @example
 * <CommonParamsModal
 *   isOpen={true}
 *   gameGid={10000147}
 *   onClose={() => setIsOpen(false)}
 * />
 *
 * Props:
 * @param {boolean} isOpen - Whether the modal is open
 * @param {number} gameGid - Game GID for filtering
 * @param {Function} onClose - Close handler
 */

import React, { useState } from 'react';
import { useQuery } from '@apollo/client/react';
import { BaseModal, Button, Badge, Spinner } from '@shared/ui';
import { GET_COMMON_PARAMETERS } from '@/graphql/queries';

const CommonParamsModal = ({ isOpen, onClose, gameGid }) => {
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch common parameters
  const { data, loading, error, refetch } = useQuery(GET_COMMON_PARAMETERS, {
    variables: { gameGid },
    skip: !isOpen || !gameGid,
    fetchPolicy: 'cache-and-network',
  });

  const commonParams = data?.commonParameters || [];

  // Filter parameters by search term
  const filteredParams = commonParams.filter(param =>
    param.paramName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (param.paramNameCn && param.paramNameCn.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleRefresh = () => {
    refetch();
  };

  const getTypeBadgeColor = (type) => {
    const colors = {
      base: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
      param: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
      custom: 'bg-green-500/20 text-green-300 border-green-500/30',
    };
    return colors[type] || 'bg-gray-500/20 text-gray-300 border-gray-500/30';
  };

  return (
    <BaseModal
      isOpen={isOpen}
      onClose={onClose}
      title="公共参数列表"
      size="lg"
      glassmorphism
    >
      <div className="flex flex-col h-[600px]">
        {/* Header with stats and refresh */}
        <div className="flex items-center justify-between mb-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
          <div className="flex items-center gap-6">
            <div>
              <div className="text-2xl font-bold text-cyan-400">{commonParams.length}</div>
              <div className="text-xs text-slate-400">公共参数总数</div>
            </div>
            <div className="w-px h-10 bg-slate-700" />
            <div>
              <div className="text-lg font-semibold text-green-400">
                {commonParams.length > 0 ? Math.round((commonParams.filter(p => p.occurrenceCount > 1).length / commonParams.length) * 100) : 0}%
              </div>
              <div className="text-xs text-slate-400">复用率</div>
            </div>
          </div>
          <Button
            variant="outline-primary"
            size="sm"
            onClick={handleRefresh}
            loading={loading}
            icon={() => (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            )}
          >
            刷新
          </Button>
        </div>

        {/* Search box */}
        <div className="mb-4">
          <input
            type="text"
            placeholder="搜索参数名称..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 bg-slate-900/50 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        {/* Parameters list */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Spinner size="lg" label="加载中..." />
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center h-64 text-red-400">
              <svg className="w-12 h-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p>加载失败: {error.message}</p>
            </div>
          ) : filteredParams.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 text-slate-400">
              <svg className="w-12 h-12 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
              <p>{searchTerm ? '未找到匹配的参数' : '暂无公共参数'}</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredParams.map((param) => (
                <div
                  key={param.paramName}
                  className="p-4 bg-slate-800/30 rounded-lg border border-slate-700 hover:border-cyan-500/50 transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <code className="text-cyan-400 font-semibold">{param.paramName}</code>
                        <Badge className={getTypeBadgeColor(param.type)} size="sm">
                          {param.type}
                        </Badge>
                      </div>
                      {param.paramNameCn && (
                        <div className="text-sm text-slate-400 mb-2">{param.paramNameCn}</div>
                      )}
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          出现 {param.occurrenceCount} 次
                        </span>
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                          </svg>
                          覆盖 {param.ratio.toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <svg
                      className="w-5 h-5 text-slate-500 group-hover:text-cyan-400 transition-colors"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-4 pt-4 border-t border-slate-700 flex justify-end">
          <Button variant="secondary" onClick={onClose}>
            关闭
          </Button>
        </div>
      </div>
    </BaseModal>
  );
};

export default CommonParamsModal;
