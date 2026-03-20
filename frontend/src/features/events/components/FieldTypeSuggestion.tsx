/**
 * FieldTypeSuggestion Component
 *
 * Displays field type suggestions with confidence indicators
 *
 * @module FieldTypeSuggestion
 */

import React, { useMemo } from 'react';
import type { FieldTypeInferenceData } from '../api/fieldRecommendationApi';

interface FieldTypeSuggestionProps {
  /** Type inference data */
  inferenceData: FieldTypeInferenceData;
  /** Callback when user applies a type */
  onApplyType: (type: string) => void;
  /** Optional: show all possible types */
  showAllTypes?: boolean;
}

/**
 * Component that displays field type suggestions with visual confidence indicators
 */
export const FieldTypeSuggestion: React.FC<FieldTypeSuggestionProps> = React.memo(function FieldTypeSuggestion({
  inferenceData,
  onApplyType,
  showAllTypes = false,
}) {
  // Sort possible types by probability
  const sortedTypes = useMemo(() => {
    return [...inferenceData.possibleTypes].sort((a, b) => b.probability - a.probability);
  }, [inferenceData.possibleTypes]);

  // Get confidence level color
  const getConfidenceColor = (confidence: number): string => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    if (confidence >= 0.4) return 'text-orange-400';
    return 'text-red-400';
  };

  // Get confidence level background
  const getConfidenceBg = (confidence: number): string => {
    if (confidence >= 0.8) return 'bg-green-500/10 border-green-500/20';
    if (confidence >= 0.6) return 'bg-yellow-500/10 border-yellow-500/20';
    if (confidence >= 0.4) return 'bg-orange-500/10 border-orange-500/20';
    return 'bg-red-500/10 border-red-500/20';
  };

  return (
    <div className="field-type-suggestion">
      {/* Main Suggestion */}
      <div className={`p-4 rounded-lg border ${getConfidenceBg(inferenceData.confidence)}`}>
        <div className="flex items-start justify-between mb-3">
          <div>
            <div className="text-xs text-slate-400 mb-1">推荐类型</div>
            <div className={`text-2xl font-bold ${getConfidenceColor(inferenceData.confidence)}`}>
              {inferenceData.inferredType}
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400 mb-1">置信度</div>
            <div className={`text-lg font-semibold ${getConfidenceColor(inferenceData.confidence)}`}>
              {Math.round(inferenceData.confidence * 100)}%
            </div>
          </div>
        </div>

        {/* Confidence Bar */}
        <div className="mb-3">
          <div className="flex items-center gap-2 mb-1">
            <div className="text-xs text-slate-400">置信度</div>
            <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-300 ${
                  inferenceData.confidence >= 0.8
                    ? 'bg-gradient-to-r from-green-500 to-green-400'
                    : inferenceData.confidence >= 0.6
                    ? 'bg-gradient-to-r from-yellow-500 to-yellow-400'
                    : inferenceData.confidence >= 0.4
                    ? 'bg-gradient-to-r from-orange-500 to-orange-400'
                    : 'bg-gradient-to-r from-red-500 to-red-400'
                }`}
                style={{ width: `${inferenceData.confidence * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Reasoning */}
        <div className="p-3 bg-slate-800/50 rounded mb-3">
          <div className="text-xs text-slate-300 leading-relaxed">
            {inferenceData.reasoning}
          </div>
        </div>

        {/* Apply Button */}
        <button
          onClick={() => onApplyType(inferenceData.inferredType)}
          className="w-full py-2.5 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors font-medium text-sm flex items-center justify-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          <span>应用推荐类型</span>
        </button>
      </div>

      {/* Alternative Types */}
      {showAllTypes && sortedTypes.length > 1 && (
        <div className="mt-4">
          <div className="text-xs text-slate-400 mb-2">其他可能类型:</div>
          <div className="space-y-2">
            {sortedTypes.slice(1).map((type, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border ${getConfidenceBg(type.probability)}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className={`text-sm font-medium ${getConfidenceColor(type.probability)}`}>
                    {type.type}
                  </div>
                  <div className={`text-xs font-semibold ${getConfidenceColor(type.probability)}`}>
                    {Math.round(type.probability * 100)}%
                  </div>
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${
                        type.probability >= 0.8
                          ? 'bg-green-500'
                          : type.probability >= 0.6
                          ? 'bg-yellow-500'
                          : type.probability >= 0.4
                          ? 'bg-orange-500'
                          : 'bg-red-500'
                      }`}
                      style={{ width: `${type.probability * 100}%` }}
                    />
                  </div>
                </div>
                <button
                  onClick={() => onApplyType(type.type)}
                  className="w-full py-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded transition-colors text-xs"
                >
                  使用此类型
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

export default FieldTypeSuggestion;
