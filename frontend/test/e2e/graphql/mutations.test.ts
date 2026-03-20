/**
 * GraphQL Mutations Naming Consistency Test
 *
 * TDD Test: Ensure frontend mutations match backend schema
 *
 * Test Plan:
 * 1. Verify createParameter mutation exists and works
 * 2. Verify updateParameter mutation exists and works
 * 3. Verify deleteParameter mutation exists and works
 */

import { executeMutation, executeQuery } from '@/graphql/client';

describe('GraphQL Mutations - 命名一致性', () => {
  const testGameGid = 90000001; // Test game GID
  let testEventId: number;
  let testCategoryId: number;

  beforeAll(async () => {
    // Setup: Create a test category and event
    const categoryResult = await executeMutation(
      `
      mutation CreateCategory($name: String!) {
        createCategory(name: $name) {
          ok
          category {
            id
            name
          }
          errors
        }
      }
    `,
      { name: 'Test Category for Mutations' }
    );

    expect(categoryResult.errors).toBeUndefined();
    expect(categoryResult.data.createCategory.ok).toBe(true);
    testCategoryId = categoryResult.data.createCategory.category.id;

    // Create a test event
    const eventResult = await executeMutation(
      `
      mutation CreateEvent(
        $gameGid: Int!
        $eventName: String!
        $eventNameCn: String!
        $categoryId: Int!
      ) {
        createEvent(
          gameGid: $gameGid
          eventName: $eventName
          eventNameCn: $eventNameCn
          categoryId: $categoryId
        ) {
          ok
          event {
            id
            eventName
          }
          errors
        }
      }
    `,
      {
        gameGid: testGameGid,
        eventName: 'test_event_mutation',
        eventNameCn: '测试事件变更',
        categoryId: testCategoryId,
      }
    );

    expect(eventResult.errors).toBeUndefined();
    expect(eventResult.data.createEvent.ok).toBe(true);
    testEventId = eventResult.data.createEvent.event.id;
  });

  afterAll(async () => {
    // Cleanup: Delete test data
    try {
      await executeMutation(
        `
        mutation DeleteEvent($id: Int!) {
          deleteEvent(id: $id) {
            ok
            message
          }
        }
      `,
        { id: testEventId }
      );

      await executeMutation(
        `
        mutation DeleteCategory($id: Int!) {
          deleteCategory(id: $id) {
            ok
            message
          }
        }
      `,
        { id: testCategoryId }
      );
    } catch (error) {
      console.warn('Cleanup failed:', error);
    }
  });

  describe('Parameter Mutations', () => {
    it('createParameter mutation应该成功', async () => {
      const mutation = `
        mutation CreateParameter(
          $eventId: Int!
          $paramName: String!
          $paramNameCn: String
        ) {
          createParameter(
            eventId: $eventId
            paramName: $paramName
            paramNameCn: $paramNameCn
          ) {
            ok
            parameter {
              id
              paramName
              paramNameCn
            }
            errors
          }
        }
      `;

      const result = await executeMutation(mutation, {
        eventId: testEventId,
        paramName: 'test_param_mutation',
        paramNameCn: '测试参数变更',
      });

      // ✅ Should pass: Backend has create_parameter, frontend calls createParameter
      expect(result.errors).toBeUndefined();
      expect(result.data.createParameter.ok).toBe(true);
      expect(result.data.createParameter.parameter.paramName).toBe('test_param_mutation');
    });

    it('updateParameter mutation应该成功', async () => {
      // First create a parameter to update
      const createResult = await executeMutation(
        `
        mutation CreateParameter(
          $eventId: Int!
          $paramName: String!
          $paramNameCn: String
        ) {
          createParameter(
            eventId: $eventId
            paramName: $paramName
            paramNameCn: $paramNameCn
          ) {
            ok
            parameter {
              id
              paramName
            }
            errors
          }
        }
      `,
        {
          eventId: testEventId,
          paramName: 'test_param_update',
          paramNameCn: '测试参数更新',
        }
      );

      expect(createResult.errors).toBeUndefined();
      const paramId = createResult.data.createParameter.parameter.id;

      // Now update it
      const mutation = `
        mutation UpdateParameter(
          $id: Int!
          $paramNameCn: String
        ) {
          updateParameter(
            id: $id
            paramNameCn: $paramNameCn
          ) {
            ok
            parameter {
              id
              paramNameCn
            }
            errors
          }
        }
      `;

      const result = await executeMutation(mutation, {
        id: paramId,
        paramNameCn: '更新后的参数名称',
      });

      expect(result.errors).toBeUndefined();
      expect(result.data.updateParameter.ok).toBe(true);
      expect(result.data.updateParameter.parameter.paramNameCn).toBe('更新后的参数名称');
    });

    it('deleteParameter mutation应该成功', async () => {
      // First create a parameter to delete
      const createResult = await executeMutation(
        `
        mutation CreateParameter(
          $eventId: Int!
          $paramName: String!
          $paramNameCn: String
        ) {
          createParameter(
            eventId: $eventId
            paramName: $paramName
            paramNameCn: $paramNameCn
          ) {
            ok
            parameter {
              id
              paramName
            }
            errors
          }
        }
      `,
        {
          eventId: testEventId,
          paramName: 'test_param_delete',
          paramNameCn: '测试参数删除',
        }
      );

      expect(createResult.errors).toBeUndefined();
      const paramId = createResult.data.createParameter.parameter.id;

      // Now delete it
      const mutation = `
        mutation DeleteParameter($id: Int!) {
          deleteParameter(id: $id) {
            ok
            message
            errors
          }
        }
      `;

      const result = await executeMutation(mutation, { id: paramId });

      expect(result.errors).toBeUndefined();
      expect(result.data.deleteParameter.ok).toBe(true);
    });
  });
});
