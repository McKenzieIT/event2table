// @ts-nocheck - TypeScript strict mode disabled for test files
/**
 * Categories Hooks 单元测试
 */

import { MockedProvider } from '@apollo/client/testing/react';
import { renderHook, waitFor, act } from '@test/test-utils';
import React from 'react';
import { describe, it, expect } from 'vitest';

import {
  useCategories,
  useCategory,
  useCreateCategory,
  useUpdateCategory,
  useDeleteCategory,
} from '../../../shared/graphql/hooks';
import {
  CREATE_CATEGORY,
  UPDATE_CATEGORY,
  DELETE_CATEGORY,
} from '../../../shared/graphql/mutations';
import {
  GET_CATEGORIES,
  GET_CATEGORY,
} from '../../../shared/graphql/queries';

// Mock数据
const mockCategories = [
  { __typename: 'Category', id: 1, name: '用户行为', eventCount: 10 },
  { __typename: 'Category', id: 2, name: '支付相关', eventCount: 5 },
  { __typename: 'Category', id: 3, name: '游戏事件', eventCount: 15 },
];

const mockCategory = { __typename: 'Category', id: 1, name: '用户行为', eventCount: 10 };

// 测试wrapper - 使用 addTypename={false} 避免类型名不匹配问题
const createWrapper = (mocks: any[] = []) => {
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <MockedProvider mocks={mocks} addTypename={false}>
        {children}
      </MockedProvider>
    );
  };
};

describe('Categories Hooks', () => {
  describe('useCategories', () => {
    it('should fetch categories list', async () => {
      const mocks = [
        {
          request: {
            query: GET_CATEGORIES,
            variables: { limit: 50, offset: 0 },
          },
          result: {
            data: {
              categories: mockCategories,
            },
          },
        },
      ];

      const { result } = renderHook(() => useCategories(50, 0), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.categories).toEqual(mockCategories);
    });

    it('should fetch categories with custom limit and offset', async () => {
      const mocks = [
        {
          request: {
            query: GET_CATEGORIES,
            variables: { limit: 20, offset: 10 },
          },
          result: {
            data: {
              categories: [mockCategories[0]],
            },
          },
        },
      ];

      const { result } = renderHook(() => useCategories(20, 10), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.categories).toHaveLength(1);
    });
  });

  describe('useCategory', () => {
    it('should fetch a single category', async () => {
      const mocks = [
        {
          request: {
            query: GET_CATEGORY,
            variables: { id: 1 },
          },
          result: {
            data: {
              category: mockCategory,
            },
          },
        },
      ];

      const { result } = renderHook(() => useCategory(1), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.data?.category).toEqual(mockCategory);
    });

    it('should skip query when id is null', () => {
      const { result } = renderHook(() => useCategory(null as any), {
        wrapper: createWrapper([]),
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeUndefined();
    });

    it('should skip query when id is 0', () => {
      const { result } = renderHook(() => useCategory(0), {
        wrapper: createWrapper([]),
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('useCreateCategory', () => {
    it('should create a category', async () => {
      // Mock for the refetch query triggered by refetchQueries in useCreateCategory
      const refetchMock = {
        request: {
          query: GET_CATEGORIES,
          variables: { limit: 50, offset: 0 },
        },
        result: {
          data: {
            categories: [...mockCategories, { id: 4, name: '新分类', eventCount: 0 }],
          },
        },
      };

      const mocks = [
        {
          request: {
            query: CREATE_CATEGORY,
            variables: { name: '新分类' },
          },
          result: {
            data: {
              createCategory: {
                __typename: 'CreateCategoryPayload',
                ok: true,
                category: { __typename: 'Category', id: 4, name: '新分类' },
                errors: null,
              },
            },
          },
        },
        refetchMock,
      ];

      const { result } = renderHook(() => useCreateCategory(), {
        wrapper: createWrapper(mocks),
      });

      // Wait for the mutation hook to be ready
      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      const [createCategory] = result.current;

      // Execute mutation within act() to properly handle state updates
      let response;
      await act(async () => {
        response = await createCategory({
          variables: { name: '新分类' },
        });
      });

      expect(response.data?.createCategory?.ok).toBe(true);
      expect(response.data?.createCategory?.category?.name).toBe('新分类');
    });
  });

  describe('useUpdateCategory', () => {
    it('should update a category', async () => {
      const mocks = [
        {
          request: {
            query: UPDATE_CATEGORY,
            variables: { id: 1, name: '更新后的分类' },
          },
          result: {
            data: {
              updateCategory: {
                __typename: 'UpdateCategoryPayload',
                ok: true,
                category: { __typename: 'Category', id: 1, name: '更新后的分类' },
                errors: null,
              },
            },
          },
        },
      ];

      const { result } = renderHook(() => useUpdateCategory(), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      const [updateCategory] = result.current;

      // Execute mutation within act() to properly handle state updates
      let response;
      await act(async () => {
        response = await updateCategory({
          variables: { id: 1, name: '更新后的分类' },
        });
      });

      expect(response.data?.updateCategory?.ok).toBe(true);
      expect(response.data?.updateCategory?.category?.name).toBe('更新后的分类');
    });
  });

  describe('useDeleteCategory', () => {
    it('should delete a category', async () => {
      // Mock for the refetch query triggered by refetchQueries in useDeleteCategory
      const refetchMock = {
        request: {
          query: GET_CATEGORIES,
          variables: { limit: 50, offset: 0 },
        },
        result: {
          data: {
            categories: mockCategories.filter(c => c.id !== 1),
          },
        },
      };

      const mocks = [
        {
          request: {
            query: DELETE_CATEGORY,
            variables: { id: 1 },
          },
          result: {
            data: {
              deleteCategory: {
                __typename: 'DeleteCategoryPayload',
                ok: true,
                message: 'Category deleted successfully',
                errors: null,
              },
            },
          },
        },
        refetchMock,
      ];

      const { result } = renderHook(() => useDeleteCategory(), {
        wrapper: createWrapper(mocks),
      });

      await waitFor(() => {
        expect(result.current[0]).toBeDefined();
      });

      const [deleteCategory] = result.current;

      // Execute mutation within act() to properly handle state updates
      let response;
      await act(async () => {
        response = await deleteCategory({
          variables: { id: 1 },
        });
      });

      expect(response.data?.deleteCategory?.ok).toBe(true);
      expect(response.data?.deleteCategory?.message).toBe('Category deleted successfully');
    });
  });
});
