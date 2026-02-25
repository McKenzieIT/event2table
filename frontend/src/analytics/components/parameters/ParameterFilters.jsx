/**
 * ParameterFilters - Filter Component for Parameters
 *
 * Provides filtering controls for parameter list:
 * - Mode selection (all/common/non-common)
 * - Event filtering dropdown
 * - View common parameters button
 *
 * @example
 * <ParameterFilters
 *   gameGid={10000147}
 *   mode="all"
 *   selectedEvent={null}
 *   onModeChange={(mode) => setMode(mode)}
 *   onEventChange={(event) => setSelectedEvent(event)}
 *   onViewCommonParams={() => setShowCommonModal(true)}
 * />
 *
 * Props:
 * @param {number} gameGid - Game GID for filtering
 * @param {string} mode - Filter mode: 'all' | 'common' | 'non-common'
 * @param {string|null} selectedEvent - Selected event for filtering
 * @param {Function} onModeChange - Mode change handler
 * @param {Function} onEventChange - Event change handler
 * @param {Function} onViewCommonParams - View common params handler
 */

import React from 'react';
import { useQuery } from '@apollo/client/react';
import { Select } from '@shared/ui';
import { GET_EVENTS } from '@/graphql/queries';

const ParameterFilters = ({
  gameGid,
  mode,
  selectedEvent,
  onModeChange,
  onEventChange,
  onViewCommonParams,
}) => {
  // Fetch events for dropdown
  const { data: eventsData, loading: eventsLoading } = useQuery(GET_EVENTS, {
    variables: { gameGid },
    skip: !gameGid,
    fetchPolicy: 'cache-and-network',
  });

  const events = eventsData?.events || [];

  // Mode options for segmented control
  const modeOptions = [
    { value: 'all', label: '全部参数' },
    { value: 'common', label: '公共参数' },
    { value: 'non-common', label: '非公共参数' },
  ];

  // Prepare event options for Select
  const eventOptions = [
    { value: '', label: '所有事件' },
    ...events.map((event) => ({
      value: event.id,
      label: `${event.eventName} (${event.eventNameCn || event.eventName})`,
    })),
  ];

  return (
    <div className="flex flex-col gap-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
      {/* Mode Selection - Segmented Control */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium text-slate-300 mr-2">参数类型:</span>
        <div className="flex bg-slate-900/50 rounded-lg p-1 border border-slate-700">
          {modeOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => onModeChange(option.value)}
              className={`
                px-4 py-2 rounded-md text-sm font-medium transition-all
                ${
                  mode === option.value
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shadow-lg shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
                }
              `}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Event Filter Dropdown + View Common Button */}
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <Select
            label="事件筛选"
            options={eventOptions}
            value={selectedEvent || ''}
            onChange={(value) => onEventChange(value || null)}
            placeholder="选择事件筛选参数"
            disabled={!gameGid || eventsLoading}
            searchable
            helperText={gameGid ? `共 ${events.length} 个事件` : '请先选择游戏'}
          />
        </div>

        <div className="flex items-end">
          <button
            onClick={onViewCommonParams}
            className="px-4 py-2 bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded-lg hover:bg-purple-500/30 transition-all flex items-center gap-2"
            disabled={!gameGid}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            查看公共参数
          </button>
        </div>
      </div>
    </div>
  );
};

export default ParameterFilters;
