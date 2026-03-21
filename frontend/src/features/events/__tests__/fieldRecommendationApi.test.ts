/**
 * Field Recommendation API Tests
 *
 * Unit tests for field recommendation API client
 */

import { vi, describe, it, expect, beforeEach } from 'vitest';
import {
  getRecommendations,
  getCommonPatterns,
  inferFieldType,
  type FieldRecommendationRequest,
  type FieldTypeInferenceRequest,
} from '../api/fieldRecommendationApi';

// Mock fetch globally
global.fetch = vi.fn();

describe('fieldRecommendationApi', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('getRecommendations', () => {
    it('should fetch field recommendations successfully', async () => {
      const mockResponse = {
        success: true,
        data: {
          recommendedName: 'user_id',
          recommendedType: 'string',
          confidence: 0.95,
          alternatives: [],
          reason: 'Matches common user ID pattern',
        },
      };

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const request: FieldRecommendationRequest = {
        paramName: 'userId',
        gameGid: 10000147,
      };

      const result = await getRecommendations(request);

      expect(result).toEqual(mockResponse.data);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/field-recommendations/recommend',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
        })
      );
    });

    it('should throw error when API request fails', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        statusText: 'Internal Server Error',
      });

      const request: FieldRecommendationRequest = {
        paramName: 'userId',
        gameGid: 10000147,
      };

      await expect(getRecommendations(request)).rejects.toThrow(
        'Failed to get field recommendations: Internal Server Error'
      );
    });

    it('should throw error when response indicates failure', async () => {
      const mockResponse = {
        success: false,
        message: 'Invalid parameter name',
      };

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const request: FieldRecommendationRequest = {
        paramName: 'userId',
        gameGid: 10000147,
      };

      await expect(getRecommendations(request)).rejects.toThrow(
        'Invalid parameter name'
      );
    });
  });

  describe('getCommonPatterns', () => {
    it('should fetch common patterns successfully', async () => {
      const mockResponse = {
        success: true,
        data: [
          {
            name: 'user_id',
            description: 'User identifier',
            examples: ['123', '456'],
            fieldType: 'string',
          },
          {
            name: 'timestamp',
            description: 'Timestamp value',
            examples: ['1234567890'],
            fieldType: 'bigint',
          },
        ],
      };

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await getCommonPatterns();

      expect(result).toEqual(mockResponse.data);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/field-recommendations/patterns'
      );
    });

    it('should throw error when API request fails', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        statusText: 'Not Found',
      });

      await expect(getCommonPatterns()).rejects.toThrow(
        'Failed to get common patterns: Not Found'
      );
    });

    it('should throw error when data is not an array', async () => {
      const mockResponse = {
        success: true,
        data: 'not an array',
      };

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      await expect(getCommonPatterns()).rejects.toThrow(
        'Invalid API response: data is not an array'
      );
    });
  });

  describe('inferFieldType', () => {
    it('should infer field type successfully', async () => {
      const mockResponse = {
        success: true,
        data: {
          inferredType: 'int',
          confidence: 0.9,
          possibleTypes: [
            { type: 'int', probability: 0.9 },
            { type: 'string', probability: 0.1 },
          ],
          reasoning: 'Values are numeric integers',
        },
      };

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const request: FieldTypeInferenceRequest = {
        paramName: 'userId',
        gameGid: 10000147,
        sampleValues: ['123', '456', '789'],
      };

      const result = await inferFieldType(request);

      expect(result).toEqual(mockResponse.data);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/field-recommendations/types',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(request),
        })
      );
    });

    it('should throw error when API request fails', async () => {
      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: false,
        statusText: 'Bad Request',
      });

      const request: FieldTypeInferenceRequest = {
        paramName: 'userId',
        gameGid: 10000147,
      };

      await expect(inferFieldType(request)).rejects.toThrow(
        'Failed to infer field type: Bad Request'
      );
    });

    it('should throw error when response indicates failure', async () => {
      const mockResponse = {
        success: false,
        message: 'Invalid sample values',
      };

      (global.fetch as ReturnType<typeof vi.fn>).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const request: FieldTypeInferenceRequest = {
        paramName: 'userId',
        gameGid: 10000147,
      };

      await expect(inferFieldType(request)).rejects.toThrow(
        'Invalid sample values'
      );
    });
  });
});
