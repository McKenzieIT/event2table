/**
 * ApiLatencyChart Component
 *
 * Displays API latency data in a table format with metrics
 */

import { Spinner } from '@shared/ui';
import React from 'react';

import { useApiLatency } from '../hooks';
import type { ApiLatencyData, ApiLatencyDataPoint } from '../types';

/**
 * ApiLatencyChart component for displaying API latency metrics
 *
 * @returns ApiLatencyChart component
 *
 * @example
 * ```tsx
 * <ApiLatencyChart />
 * ```
 */
export function ApiLatencyChart(): React.JSX.Element {
  const { data: apiLatency, isLoading, error } = useApiLatency();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-700 font-medium">Failed to load API latency data</p>
        <p className="text-red-600 text-sm mt-1">{error.message}</p>
      </div>
    );
  }

  if (!apiLatency) {
    return null;
  }

  const getLatencyColor = (latency: number): string => {
    if (latency < 100) return 'text-green-600';
    if (latency < 500) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">API Latency</h3>
        <div className="text-sm text-gray-500">
          Last updated: {new Date(apiLatency.timestamp).toLocaleString()}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <p className="text-sm font-medium text-gray-600 mb-1">Average Latency</p>
          <p className={`text-2xl font-bold ${getLatencyColor(apiLatency.summary.overall_avg_latency_ms)}`}>
            {apiLatency.summary.overall_avg_latency_ms.toFixed(2)} ms
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <p className="text-sm font-medium text-gray-600 mb-1">Total Requests</p>
          <p className="text-2xl font-bold text-gray-900">
            {apiLatency.summary.total_requests.toLocaleString()}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <p className="text-sm font-medium text-gray-600 mb-1">Slowest Endpoint</p>
          <p className="text-lg font-semibold text-red-600 truncate">
            {apiLatency.summary.slowest_endpoint}
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Endpoint
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Method
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Avg (ms)
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                P50 (ms)
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                P95 (ms)
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                P99 (ms)
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Requests
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {apiLatency.endpoints.map((endpoint: ApiLatencyDataPoint, index: number) => (
              <tr key={`${endpoint.endpoint}-${endpoint.method}-${index}`}>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {endpoint.endpoint}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    endpoint.method === 'GET' ? 'bg-blue-100 text-blue-800' :
                    endpoint.method === 'POST' ? 'bg-green-100 text-green-800' :
                    endpoint.method === 'PUT' ? 'bg-yellow-100 text-yellow-800' :
                    endpoint.method === 'DELETE' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {endpoint.method}
                  </span>
                </td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getLatencyColor(endpoint.avg_latency_ms)}`}>
                  {endpoint.avg_latency_ms.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {endpoint.p50_latency_ms.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {endpoint.p95_latency_ms.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {endpoint.p99_latency_ms.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {endpoint.request_count.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
