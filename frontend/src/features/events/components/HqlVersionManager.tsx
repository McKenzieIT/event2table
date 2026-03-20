/**
 * HqlVersionManager Component
 *
 * Main container for HQL version management features
 * Integrates history, timeline, actions, and compare components
 *
 * @example
 * ```tsx
 * <HqlVersionManager
 *   eventId={123}
 *   currentHql="SELECT * FROM table"
 *   onVersionChange={(hql) => setHql(hql)}
 * />
 * ```
 */

import React, { useState, useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { HqlVersionHistory } from './HqlVersionHistory';
import { HqlVersionTimeline } from './HqlVersionTimeline';
import { HqlVersionActions } from './HqlVersionActions';
import { HqlVersionCompare } from './HqlVersionCompare';
import { useHqlVersionCompare } from '../hooks';
import type { HqlVersion, VersionDiff } from '../api/hqlVersionApi';
import './HqlVersionManager.css';

interface HqlVersionManagerProps {
  eventId: number;
  currentHql: string;
  onVersionChange?: (hql: string) => void;
}

const HqlVersionManager: React.FC<HqlVersionManagerProps> = ({
  eventId,
  currentHql,
  onVersionChange
}) => {
  const queryClient = useQueryClient();
  const [selectedVersion, setSelectedVersion] = useState<HqlVersion | null>(null);
  const [compareVersion, setCompareVersion] = useState<HqlVersion | null>(null);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [viewMode, setViewMode] = useState<'list' | 'timeline'>('list');

  const compareMutation = useHqlVersionCompare({
    onSuccess: () => {
      setShowCompareModal(true);
    }
  });

  const handleSelectVersion = useCallback((version: HqlVersion) => {
    setSelectedVersion(version);
  }, []);

  const handleCompare = useCallback(async (version1: HqlVersion, version2: HqlVersion) => {
    setCompareVersion(version2);
    compareMutation.mutate({
      version_id_1: version1.id,
      version_id_2: version2.id
    });
  }, [compareMutation]);

  const handleSaveSuccess = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['hql-versions', 'history', eventId] });
  }, [queryClient, eventId]);

  const handleRollbackSuccess = useCallback((version: HqlVersion) => {
    if (onVersionChange) {
      onVersionChange(version.hql_content);
    }
    queryClient.invalidateQueries({ queryKey: ['hql-versions', 'history', eventId] });
  }, [onVersionChange, queryClient, eventId]);

  return (
    <div className="hql-version-manager">
      {/* View Mode Toggle */}
      <div className="view-mode-toggle">
        <div className="btn-group">
          <button
            className={`btn btn-sm ${viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setViewMode('list')}
            type="button"
          >
            <i className="bi bi-list-ul"></i>
            {' '}列表视图
          </button>
          <button
            className={`btn btn-sm ${viewMode === 'timeline' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setViewMode('timeline')}
            type="button"
          >
            <i className="bi bi-clock-history"></i>
            {' '}时间线视图
          </button>
        </div>
      </div>

      {/* Version History/Timeline */}
      {viewMode === 'list' ? (
        <HqlVersionHistory
          eventId={eventId}
          selectedVersionId={selectedVersion?.id}
          compareVersionId={compareVersion?.id}
          onSelectVersion={handleSelectVersion}
          onCompare={handleCompare}
        />
      ) : (
        <HqlVersionTimeline
          eventId={eventId}
          selectedVersionId={selectedVersion?.id}
          onSelectVersion={handleSelectVersion}
        />
      )}

      {/* Version Actions */}
      <HqlVersionActions
        eventId={eventId}
        currentHql={currentHql}
        selectedVersion={selectedVersion}
        compareVersion={compareVersion}
        onSaveSuccess={handleSaveSuccess}
        onRollbackSuccess={handleRollbackSuccess}
        onCompare={handleCompare}
      />

      {/* Compare Modal */}
      {showCompareModal && selectedVersion && compareVersion && compareMutation.data && (
        <HqlVersionCompare
          isOpen={showCompareModal}
          version1={selectedVersion}
          version2={compareVersion}
          diff={compareMutation.data}
          onClose={() => setShowCompareModal(false)}
        />
      )}
    </div>
  );
};

export default React.memo(HqlVersionManager);