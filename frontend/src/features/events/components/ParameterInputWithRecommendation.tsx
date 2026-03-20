/**
 * ParameterInputWithRecommendation Component
 *
 * Integrated parameter input field with intelligent field recommendations
 * This component demonstrates how to integrate field recommendation features
 * into event parameter editing pages
 *
 * @module ParameterInputWithRecommendation
 */

import React, { useState, useCallback } from 'react';
import { Input } from '@shared/ui';
import { FieldRecommendation } from './FieldRecommendation';
import type { FieldRecommendationData, FieldTypeInferenceData } from '../api/fieldRecommendationApi';

interface ParameterInputWithRecommendationProps {
  /** Current parameter name value */
  value: string;
  /** Callback when parameter name changes */
  onChange: (value: string) => void;
  /** Game GID */
  gameGid: number;
  /** Optional: event ID for more specific recommendations */
  eventId?: number;
  /** Input label */
  label?: string;
  /** Input placeholder */
  placeholder?: string;
  /** Input error message */
  error?: string;
  /** Callback when recommendation is applied */
  onApplyRecommendation?: (recommendation: FieldRecommendationData) => void;
  /** Callback when type inference is applied */
  onApplyTypeInference?: (inference: FieldTypeInferenceData) => void;
}

/**
 * Parameter input component with integrated intelligent recommendations
 */
export const ParameterInputWithRecommendation: React.FC<ParameterInputWithRecommendationProps> = React.memo(function ParameterInputWithRecommendation({
  value,
  onChange,
  gameGid,
  eventId,
  label = '参数名称',
  placeholder = '例如: user_id',
  error,
  onApplyRecommendation,
  onApplyTypeInference,
}) {
  const [showRecommendations, setShowRecommendations] = useState(false);

  // Handle recommendation application
  const handleApplyRecommendation = useCallback(
    (recommendation: FieldRecommendationData) => {
      // Update parameter name with recommended name
      onChange(recommendation.recommendedName);
      
      // Call parent callback if provided
      if (onApplyRecommendation) {
        onApplyRecommendation(recommendation);
      }
    },
    [onChange, onApplyRecommendation]
  );

  // Handle type inference application
  const handleApplyTypeInference = useCallback(
    (inference: FieldTypeInferenceData) => {
      // Call parent callback if provided
      if (onApplyTypeInference) {
        onApplyTypeInference(inference);
      }
    },
    [onApplyTypeInference]
  );

  // Toggle recommendations visibility
  const toggleRecommendations = useCallback(() => {
    setShowRecommendations((prev) => !prev);
  }, []);

  return (
    <div className="parameter-input-with-recommendation">
      {/* Parameter Name Input */}
      <Input
        label={label}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        error={error}
        required
      />

      {/* Intelligent Recommendations */}
      <div className="mt-2">
        <button
          onClick={toggleRecommendations}
          className="text-xs text-cyan-400 hover:text-cyan-300 transition-colors flex items-center gap-1"
        >
          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>智能推荐</span>
          <svg
            className={`w-3 h-3 transition-transform ${showRecommendations ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {showRecommendations && (
          <div className="mt-2">
            <FieldRecommendation
              paramName={value}
              gameGid={gameGid}
              eventId={eventId}
              onApplyRecommendation={handleApplyRecommendation}
              onApplyTypeInference={handleApplyTypeInference}
            />
          </div>
        )}
      </div>
    </div>
  );
});

export default ParameterInputWithRecommendation;
