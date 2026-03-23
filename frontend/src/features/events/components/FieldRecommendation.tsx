/**
 * FieldRecommendation Component
 *
 * Displays intelligent field recommendations for event parameters
 *
 * @module FieldRecommendation
 */

import React, { useState, useCallback } from 'react';

import type { FieldRecommendationData, FieldTypeInferenceData } from '../api/fieldRecommendationApi';
import { useFieldRecommendations } from '../hooks/useFieldRecommendations';
import { useFieldTypeInference } from '../hooks/useFieldTypeInference';

interface FieldRecommendationProps {
  /** Current parameter name */
  paramName: string;
  /** Game GID */
  gameGid: number;
  /** Optional: event ID for more specific recommendations */
  eventId?: number;
  /** Callback when user applies a recommendation */
  onApplyRecommendation: (recommendation: FieldRecommendationData) => void;
  /** Callback when user applies type inference */
  onApplyTypeInference: (inference: FieldTypeInferenceData) => void;
}

/**
 * Field recommendation component that shows AI-powered suggestions
 */
export const FieldRecommendation: React.FC<FieldRecommendationProps> = React.memo(function FieldRecommendation({
  paramName,
  gameGid,
  eventId,
  onApplyRecommendation,
  onApplyTypeInference,
}) {
  const [showRecommendations, setShowRecommendations] = useState(false);

  // Field recommendation mutation
  const {
    mutate: getRecommendations,
    data: recommendationData,
    isLoading: isRecommendationLoading,
    error: recommendationError,
  } = useFieldRecommendations();

  // Field type inference mutation
  const {
    mutate: inferType,
    data: typeInferenceData,
    isLoading: isInferenceLoading,
    error: inferenceError,
  } = useFieldTypeInference();

  // Handle getting recommendations
  const handleGetRecommendations = useCallback(() => {
    if (!paramName.trim()) return;
    getRecommendations({ paramName, gameGid, eventId });
    setShowRecommendations(true);
  }, [paramName, gameGid, eventId, getRecommendations]);

  // Handle getting type inference
  const handleInferType = useCallback(() => {
    if (!paramName.trim()) return;
    inferType({ paramName, gameGid });
  }, [paramName, gameGid, inferType]);

  // Handle applying recommendation
  const handleApplyRecommendation = useCallback(() => {
    if (recommendationData) {
      onApplyRecommendation(recommendationData);
      setShowRecommendations(false);
    }
  }, [recommendationData, onApplyRecommendation]);

  // Handle applying type inference
  const handleApplyTypeInference = useCallback(() => {
    if (typeInferenceData) {
      onApplyTypeInference(typeInferenceData);
    }
  }, [typeInferenceData, onApplyTypeInference]);

  const isLoading = isRecommendationLoading || isInferenceLoading;

  return (
    <div className="field-recommendation">
      {/* Action Buttons */}
      <div className="flex gap-2">
        <button
          onClick={handleGetRecommendations}
          disabled={!paramName.trim() || isLoading}
          className="px-3 py-1.5 text-sm bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
          title="获取智能字段推荐"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>智能推荐</span>
        </button>

        <button
          onClick={handleInferType}
          disabled={!paramName.trim() || isLoading}
          className="px-3 py-1.5 text-sm bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1.5"
          title="推断字段类型"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span>类型推断</span>
        </button>
      </div>

      {/* Recommendation Results */}
      {showRecommendations && recommendationData && (
        <div className="mt-3 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
          <div className="flex items-start justify-between mb-3">
            <h4 className="text-sm font-medium text-slate-300">字段推荐</h4>
            <button
              onClick={() => setShowRecommendations(false)}
              className="text-slate-400 hover:text-slate-300 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Main Recommendation */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs text-slate-400 mb-1">推荐字段名</div>
                <div className="text-lg font-semibold text-cyan-400">
                  {recommendationData.recommendedName}
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-slate-400 mb-1">推荐类型</div>
                <div className="text-sm font-medium text-purple-400">
                  {recommendationData.recommendedType}
                </div>
              </div>
            </div>

            {/* Confidence */}
            <div className="flex items-center gap-2">
              <div className="text-xs text-slate-400">置信度:</div>
              <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-300"
                  style={{ width: `${recommendationData.confidence * 100}%` }}
                />
              </div>
              <div className="text-xs text-slate-300">
                {Math.round(recommendationData.confidence * 100)}%
              </div>
            </div>

            {/* Reason */}
            <div className="p-2 bg-blue-500/10 border border-blue-500/20 rounded">
              <div className="text-xs text-blue-300">{recommendationData.reason}</div>
            </div>

            {/* Alternative Suggestions */}
            {recommendationData.alternatives.length > 0 && (
              <div>
                <div className="text-xs text-slate-400 mb-2">备选方案:</div>
                <div className="space-y-1">
                  {recommendationData.alternatives.map((alt, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-slate-700/50 rounded text-xs"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-slate-300">{alt.name}</span>
                        <span className="text-purple-400">({alt.type})</span>
                      </div>
                      <span className="text-slate-400">
                        {Math.round(alt.confidence * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Apply Button */}
            <button
              onClick={handleApplyRecommendation}
              className="w-full py-2 bg-cyan-500 hover:bg-cyan-600 text-white rounded-lg transition-colors font-medium text-sm"
            >
              应用推荐
            </button>
          </div>
        </div>
      )}

      {/* Type Inference Results */}
      {typeInferenceData && (
        <div className="mt-3 p-4 bg-slate-800/50 rounded-lg border border-slate-700">
          <div className="flex items-start justify-between mb-3">
            <h4 className="text-sm font-medium text-slate-300">类型推断</h4>
            <button
              onClick={() => {
                // Clear inference data by re-rendering
                window.location.reload();
              }}
              className="text-slate-400 hover:text-slate-300 transition-colors"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Inferred Type */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs text-slate-400 mb-1">推断类型</div>
                <div className="text-lg font-semibold text-purple-400">
                  {typeInferenceData.inferredType}
                </div>
              </div>
              <div className="text-right">
                <div className="text-xs text-slate-400 mb-1">置信度</div>
                <div className="text-sm font-medium text-slate-300">
                  {Math.round(typeInferenceData.confidence * 100)}%
                </div>
              </div>
            </div>

            {/* Reasoning */}
            <div className="p-2 bg-purple-500/10 border border-purple-500/20 rounded">
              <div className="text-xs text-purple-300">{typeInferenceData.reasoning}</div>
            </div>

            {/* Possible Types */}
            {typeInferenceData.possibleTypes.length > 1 && (
              <div>
                <div className="text-xs text-slate-400 mb-2">可能类型:</div>
                <div className="space-y-1">
                  {typeInferenceData.possibleTypes.map((type, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 bg-slate-700/50 rounded text-xs"
                    >
                      <span className="text-slate-300">{type.type}</span>
                      <span className="text-slate-400">
                        {Math.round(type.probability * 100)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Apply Button */}
            <button
              onClick={handleApplyTypeInference}
              className="w-full py-2 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors font-medium text-sm"
            >
              应用类型
            </button>
          </div>
        </div>
      )}

      {/* Error Messages */}
      {recommendationError && (
        <div className="mt-2 p-2 bg-red-500/10 border border-red-500/20 rounded">
          <div className="text-xs text-red-400">
            {recommendationError.message || '获取推荐失败'}
          </div>
        </div>
      )}

      {inferenceError && (
        <div className="mt-2 p-2 bg-red-500/10 border border-red-500/20 rounded">
          <div className="text-xs text-red-400">
            {inferenceError.message || '类型推断失败'}
          </div>
        </div>
      )}
    </div>
  );
});

export default FieldRecommendation;
