/**
 * ParameterFormWithRecommendations Component
 *
 * Complete parameter editing form with intelligent field recommendations
 * This component demonstrates a full integration example for event parameter editing
 *
 * @module ParameterFormWithRecommendations
 */

import { Input, Select, Button, Card, useToast } from '@shared/ui';
import React, { useState, useCallback } from 'react';

import type { FieldRecommendationData, FieldTypeInferenceData, FieldPattern } from '../api/fieldRecommendationApi';

import { FieldRecommendationDropdown } from './FieldRecommendationDropdown';
import { FieldTypeSuggestion } from './FieldTypeSuggestion';
import { ParameterInputWithRecommendation } from './ParameterInputWithRecommendation';


interface ParameterFormWithRecommendationsProps {
  /** Game GID */
  gameGid: number;
  /** Optional: event ID for more specific recommendations */
  eventId?: number;
  /** Callback when form is submitted */
  onSubmit?: (formData: ParameterFormData) => void;
  /** Callback when form is cancelled */
  onCancel?: () => void;
}

interface ParameterFormData {
  paramName: string;
  paramNameCn: string;
  paramType: string;
  paramDescription: string;
}

/**
 * Complete parameter editing form with intelligent recommendations
 */
export const ParameterFormWithRecommendations: React.FC<ParameterFormWithRecommendationsProps> = React.memo(function ParameterFormWithRecommendations({
  gameGid,
  eventId,
  onSubmit,
  onCancel,
}) {
  const { success, error: showError } = useToast();

  // Form state
  const [formData, setFormData] = useState<ParameterFormData>({
    paramName: '',
    paramNameCn: '',
    paramType: 'string',
    paramDescription: '',
  });

  // Type inference state
  const [typeInferenceData, setTypeInferenceData] = useState<FieldTypeInferenceData | null>(null);

  // Selected pattern state
  const [selectedPattern, setSelectedPattern] = useState<FieldPattern | undefined>();

  // Type options
  const typeOptions = [
    { value: 'string', label: '字符串' },
    { value: 'int', label: '整数' },
    { value: 'bigint', label: '大整数' },
    { value: 'float', label: '浮点数' },
    { value: 'boolean', label: '布尔值' },
    { value: 'json', label: 'JSON对象' },
  ];

  // Handle field change
  const handleFieldChange = useCallback((field: keyof ParameterFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  }, []);

  // Handle recommendation application
  const handleApplyRecommendation = useCallback(
    (recommendation: FieldRecommendationData) => {
      setFormData((prev) => ({
        ...prev,
        paramName: recommendation.recommendedName,
        paramType: recommendation.recommendedType,
      }));
      success('已应用字段推荐');
    },
    [success]
  );

  // Handle type inference application
  const handleApplyTypeInference = useCallback(
    (inference: FieldTypeInferenceData) => {
      setFormData((prev) => ({
        ...prev,
        paramType: inference.inferredType,
      }));
      setTypeInferenceData(inference);
      success('已应用类型推断');
    },
    [success]
  );

  // Handle pattern selection
  const handleSelectPattern = useCallback((pattern: FieldPattern) => {
    setSelectedPattern(pattern);
    setFormData((prev) => ({
      ...prev,
      paramType: pattern.fieldType,
    }));
  }, []);

  // Handle form submission
  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();

      // Validation
      if (!formData.paramName.trim()) {
        showError('参数名称不能为空');
        return;
      }

      if (!formData.paramNameCn.trim()) {
        showError('参数中文名不能为空');
        return;
      }

      // Submit form data
      if (onSubmit) {
        onSubmit(formData);
      }
    },
    [formData, onSubmit, showError]
  );

  return (
    <Card className="parameter-form-with-recommendations" padding="lg">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Parameter Name with Recommendations */}
        <div>
          <ParameterInputWithRecommendation
            label="参数名称"
            value={formData.paramName}
            onChange={(value) => handleFieldChange('paramName', value)}
            gameGid={gameGid}
            eventId={eventId}
            placeholder="例如: user_id"
            onApplyRecommendation={handleApplyRecommendation}
            onApplyTypeInference={handleApplyTypeInference}
          />
        </div>

        {/* Parameter Name Chinese */}
        <Input
          label="参数中文名"
          type="text"
          value={formData.paramNameCn}
          onChange={(e) => handleFieldChange('paramNameCn', e.target.value)}
          placeholder="例如: 用户ID"
          required
        />

        {/* Parameter Type */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            参数类型
          </label>
          <Select
            options={typeOptions}
            value={formData.paramType}
            onChange={(value) => handleFieldChange('paramType', value)}
            placeholder="选择参数类型"
          />
        </div>

        {/* Common Patterns Dropdown */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            常用字段模式
          </label>
          <FieldRecommendationDropdown
            selectedPattern={selectedPattern}
            onSelectPattern={handleSelectPattern}
            placeholder="选择常用字段模式..."
          />
          {selectedPattern && (
            <div className="mt-2 p-2 bg-purple-500/10 border border-purple-500/20 rounded">
              <div className="text-xs text-purple-300">{selectedPattern.description}</div>
            </div>
          )}
        </div>

        {/* Type Inference Results */}
        {typeInferenceData && (
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              类型推断结果
            </label>
            <FieldTypeSuggestion
              inferenceData={typeInferenceData}
              onApplyType={handleApplyTypeInference}
              showAllTypes={true}
            />
          </div>
        )}

        {/* Parameter Description */}
        <Input
          label="参数描述"
          type="text"
          value={formData.paramDescription}
          onChange={(e) => handleFieldChange('paramDescription', e.target.value)}
          placeholder="参数的详细描述"
        />

        {/* Action Buttons */}
        <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
          {onCancel && (
            <Button type="button" variant="ghost" onClick={onCancel}>
              取消
            </Button>
          )}
          <Button type="submit" variant="success">
            保存参数
          </Button>
        </div>
      </form>
    </Card>
  );
});

export default ParameterFormWithRecommendations;
