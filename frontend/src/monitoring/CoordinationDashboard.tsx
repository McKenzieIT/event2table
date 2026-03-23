/**
 * CoordinationDashboard - 性能协调仪表板
 * 用于显示并行优化期间所有Subagent的状态、冲突检测和性能指标
 */

import React, { useState, useEffect } from 'react';

import { PerformanceMonitor, MetricsSummary } from './PerformanceMonitor';

interface SubagentStatus {
  id: number;
  name: string;
  task: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  progress: number;
  startTime?: Date;
  endTime?: Date;
}

interface ConflictInfo {
  type: 'file' | 'resource' | 'dependency';
  description: string;
  severity: 'low' | 'medium' | 'high';
  subagents: number[];
}

export const CoordinationDashboard: React.FC = () => {
  const [subagents, setSubagents] = useState<SubagentStatus[]>([
    {
      id: 1,
      name: 'Subagent 1',
      task: 'Monitoring Baseline',
      status: 'idle',
      progress: 0
    },
    {
      id: 2,
      name: 'Subagent 2',
      task: 'Parallel Optimization',
      status: 'idle',
      progress: 0
    },
    {
      id: 3,
      name: 'Subagent 3',
      task: 'CI/CD Integration',
      status: 'idle',
      progress: 0
    },
    {
      id: 4,
      name: 'Subagent 4',
      task: 'Safety & Coordination',
      status: 'idle',
      progress: 0
    }
  ]);

  const [conflicts, setConflicts] = useState<ConflictInfo[]>([]);
  const [metrics, setMetrics] = useState<MetricsSummary>({
    totalAPICalls: 0,
    averageAPIDuration: 0,
    cacheHitRate: 0,
    totalPageLoads: 0
  });
  const [currentCheckpoint, setCurrentCheckpoint] = useState<string>('Not Started');

  useEffect(() => {
    // 定期更新性能指标
    const interval = setInterval(() => {
      const summary = PerformanceMonitor.getMetricsSummary();
      setMetrics(summary);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    const summary = PerformanceMonitor.getMetricsSummary();
    setMetrics(summary);
  };

  const handleExport = () => {
    const report = PerformanceMonitor.getDetailedReport();
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `performance-report-${new Date().toISOString()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getStatusColor = (status: SubagentStatus['status']): string => {
    switch (status) {
      case 'idle':
        return 'bg-gray-200 text-gray-700';
      case 'running':
        return 'bg-blue-100 text-blue-700';
      case 'completed':
        return 'bg-green-100 text-green-700';
      case 'failed':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-200 text-gray-700';
    }
  };

  const getSeverityColor = (severity: ConflictInfo['severity']): string => {
    switch (severity) {
      case 'low':
        return 'text-yellow-600';
      case 'medium':
        return 'text-orange-600';
      case 'high':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Performance Coordination Dashboard
              </h1>
              <p className="text-gray-600 mt-2">
                Monitoring parallel optimization progress and coordination
              </p>
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleRefresh}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Refresh
              </button>
              <button
                onClick={handleExport}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
              >
                Export Report
              </button>
            </div>
          </div>
        </div>

        {/* Checkpoint Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Current Checkpoint
          </h2>
          <p className="text-lg">
            <span className="font-medium">Checkpoint:</span> {currentCheckpoint}
          </p>
        </div>

        {/* Subagent Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Subagent Status
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {subagents.map((subagent) => (
              <div
                key={subagent.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {subagent.name}
                    </h3>
                    <p className="text-sm text-gray-600">{subagent.task}</p>
                  </div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                      subagent.status
                    )}`}
                  >
                    {subagent.status.toUpperCase()}
                  </span>
                </div>
                <div className="mt-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">Progress:</span>
                    <span className="text-sm font-medium">{subagent.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${subagent.progress}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Conflict Detection */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Conflict Detection
          </h2>
          {conflicts.length === 0 ? (
            <p className="text-gray-600">No conflicts detected</p>
          ) : (
            <div className="space-y-3">
              <p className="text-sm font-medium text-gray-700">
                Conflicts: {conflicts.length}
              </p>
              {conflicts.map((conflict, index) => (
                <div
                  key={index}
                  className="border-l-4 border-red-500 bg-red-50 p-4 rounded"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900">{conflict.description}</p>
                      <p className="text-sm text-gray-600 mt-1">
                        Type: {conflict.type} | Subagents: {conflict.subagents.join(', ')}
                      </p>
                    </div>
                    <span
                      className={`text-sm font-medium ${getSeverityColor(
                        conflict.severity
                      )}`}
                    >
                      {conflict.severity.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Performance Summary */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Performance Summary
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-sm text-blue-600 font-medium">API Calls</p>
              <p className="text-2xl font-bold text-blue-900">{metrics.totalAPICalls}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-sm text-green-600 font-medium">Avg Duration</p>
              <p className="text-2xl font-bold text-green-900">{metrics.averageAPIDuration}ms</p>
            </div>
            <div className="bg-purple-50 rounded-lg p-4">
              <p className="text-sm text-purple-600 font-medium">Cache Hit Rate</p>
              <p className="text-2xl font-bold text-purple-900">
                {(metrics.cacheHitRate * 100).toFixed(0)}%
              </p>
            </div>
            <div className="bg-orange-50 rounded-lg p-4">
              <p className="text-sm text-orange-600 font-medium">Page Loads</p>
              <p className="text-2xl font-bold text-orange-900">{metrics.totalPageLoads}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
