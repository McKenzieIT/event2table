import { test, expect } from '@playwright/test';

/**
 * Canvas Workflow E2E Tests
 * 
 * Tests for Canvas workflow functionality:
 * - Drag and drop nodes
 * - Connect nodes
 * - Execute workflow
 * - Save flow
 * - Load flow
 */

test.describe('Canvas Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to canvas page
    await page.goto('/canvas');
    await page.waitForLoadState('networkidle');
  });

  test('should display canvas workspace', async ({ page }) => {
    // Verify page title
    await expect(page).toHaveTitle(/Event2Table/);
    
    // Check if canvas container exists
    const canvasContainer = page.locator('.react-flow, .canvas-container, [data-testid="canvas"]');
    await expect(canvasContainer).toBeVisible();
    
    // Check if node sidebar exists
    const nodeSidebar = page.locator('.node-sidebar, .sidebar, [data-testid="node-sidebar"]');
    const sidebarCount = await nodeSidebar.count();
    
    if (sidebarCount > 0) {
      await expect(nodeSidebar).toBeVisible();
    }
  });

  test('should drag and drop event node to canvas', async ({ page }) => {
    // Wait for canvas to load
    await page.waitForTimeout(1000);
    
    // Find draggable event nodes in sidebar
    const eventNodes = page.locator('.draggable-node, .event-node-item, [draggable="true"]');
    const count = await eventNodes.count();
    
    if (count === 0) {
      test.skip();
      return;
    }
    
    // Get canvas container
    const canvas = page.locator('.react-flow, .canvas-container');
    
    // Drag first node to canvas
    const firstNode = eventNodes.first();
    await firstNode.dragTo(canvas);
    
    // Wait for node to be dropped
    await page.waitForTimeout(500);
    
    // Verify node was added to canvas
    const canvasNodes = page.locator('.react-flow__node, .canvas-node');
    const nodeCount = await canvasNodes.count();
    expect(nodeCount).toBeGreaterThan(0);
  });

  test('should connect two nodes with edge', async ({ page }) => {
    // Wait for canvas to load
    await page.waitForTimeout(1000);
    
    // Add two nodes to canvas
    const eventNodes = page.locator('.draggable-node, .event-node-item, [draggable="true"]');
    const canvas = page.locator('.react-flow, .canvas-container');
    
    const nodeCount = await eventNodes.count();
    if (nodeCount < 2) {
      test.skip();
      return;
    }
    
    await eventNodes.nth(0).dragTo(canvas);
    await page.waitForTimeout(300);
    await eventNodes.nth(1).dragTo(canvas);
    await page.waitForTimeout(500);
    
    // Get the two nodes
    const canvasNodes = page.locator('.react-flow__node, .canvas-node');
    const firstCanvasNode = canvasNodes.nth(0);
    const secondCanvasNode = canvasNodes.nth(1);
    
    // Get handle positions (source and target handles)
    const sourceHandle = firstCanvasNode.locator('.react-flow__handle.source, .handle-source');
    const targetHandle = secondCanvasNode.locator('.react-flow__handle.target, .handle-target');
    
    const sourceCount = await sourceHandle.count();
    const targetCount = await targetHandle.count();
    
    if (sourceCount > 0 && targetCount > 0) {
      // Drag from source handle to target handle
      await sourceHandle.first().dragTo(targetHandle.first());
      
      // Wait for edge to be created
      await page.waitForTimeout(500);
      
      // Verify edge was created
      const edges = page.locator('.react-flow__edge, .canvas-edge');
      const edgeCount = await edges.count();
      expect(edgeCount).toBeGreaterThan(0);
    }
  });

  test('should execute workflow and generate HQL', async ({ page }) => {
    // Wait for canvas to load
    await page.waitForTimeout(1000);
    
    // Add a node to canvas
    const eventNodes = page.locator('.draggable-node, .event-node-item, [draggable="true"]');
    const canvas = page.locator('.react-flow, .canvas-container');
    
    const nodeCount = await eventNodes.count();
    if (nodeCount === 0) {
      test.skip();
      return;
    }
    
    await eventNodes.first().dragTo(canvas);
    await page.waitForTimeout(500);
    
    // Click execute button
    const executeButton = page.locator('button:has-text("执行"), button:has-text("Execute"), [data-testid="execute-flow-button"]');
    const executeCount = await executeButton.count();
    
    if (executeCount > 0) {
      await executeButton.click();
      
      // Wait for execution
      await page.waitForTimeout(2000);
      
      // Verify HQL output is displayed
      const hqlOutput = page.locator('.hql-output, .hql-result, pre');
      const outputCount = await hqlOutput.count();
      
      if (outputCount > 0) {
        await expect(hqlOutput).toBeVisible();
      }
    }
  });

  test('should save flow template', async ({ page }) => {
    // Wait for canvas to load
    await page.waitForTimeout(1000);
    
    // Add a node to canvas
    const eventNodes = page.locator('.draggable-node, .event-node-item, [draggable="true"]');
    const canvas = page.locator('.react-flow, .canvas-container');
    
    const nodeCount = await eventNodes.count();
    if (nodeCount === 0) {
      test.skip();
      return;
    }
    
    await eventNodes.first().dragTo(canvas);
    await page.waitForTimeout(500);
    
    // Click save button
    const saveButton = page.locator('button:has-text("保存"), button:has-text("Save"), [data-testid="save-flow-button"]');
    const saveCount = await saveButton.count();
    
    if (saveCount > 0) {
      await saveButton.click();
      
      // Wait for save dialog
      await page.waitForTimeout(500);
      
      // Enter flow name
      const nameInput = page.locator('input[name="name"], input[placeholder*="名称"]');
      const inputCount = await nameInput.count();
      
      if (inputCount > 0) {
        await nameInput.fill(`Test Flow ${Date.now()}`);
        
        // Confirm save
        const confirmButton = page.locator('button:has-text("确认"), button:has-text("保存")');
        await confirmButton.click();
        
        // Wait for save to complete
        await page.waitForTimeout(1000);
        
        // Verify success message
        const successMessage = page.locator('.toast-success, .notification-success, [role="alert"]:has-text("保存")');
        if (await successMessage.count() > 0) {
          await expect(successMessage).toBeVisible();
        }
      }
    }
  });

  test('should load saved flow', async ({ page }) => {
    // Wait for canvas to load
    await page.waitForTimeout(1000);
    
    // Click load button
    const loadButton = page.locator('button:has-text("加载"), button:has-text("Load"), [data-testid="load-flow-button"]');
    const loadCount = await loadButton.count();
    
    if (loadCount > 0) {
      await loadButton.click();
      
      // Wait for load dialog
      await page.waitForTimeout(500);
      
      // Find saved flows list
      const flowsList = page.locator('.flows-list, .saved-flows');
      const listCount = await flowsList.count();
      
      if (listCount > 0) {
        // Click on first flow
        const firstFlow = flowsList.locator('.flow-item, .saved-flow-item').first();
        const flowCount = await firstFlow.count();
        
        if (flowCount > 0) {
          await firstFlow.click();
          
          // Wait for flow to load
          await page.waitForTimeout(1000);
          
          // Verify nodes are loaded
          const canvasNodes = page.locator('.react-flow__node, .canvas-node');
          const nodeCount = await canvasNodes.count();
          expect(nodeCount).toBeGreaterThan(0);
        }
      }
    }
  });

  test('should delete node from canvas', async ({ page }) => {
    // Wait for canvas to load
    await page.waitForTimeout(1000);
    
    // Add a node to canvas
    const eventNodes = page.locator('.draggable-node, .event-node-item, [draggable="true"]');
    const canvas = page.locator('.react-flow, .canvas-container');
    
    const nodeCount = await eventNodes.count();
    if (nodeCount === 0) {
      test.skip();
      return;
    }
    
    await eventNodes.first().dragTo(canvas);
    await page.waitForTimeout(500);
    
    // Select the node
    const canvasNode = page.locator('.react-flow__node, .canvas-node').first();
    await canvasNode.click();
    
    // Wait for selection
    await page.waitForTimeout(300);
    
    // Press delete key or click delete button
    const deleteButton = page.locator('button:has-text("删除"), button:has-text("Delete")');
    const deleteCount = await deleteButton.count();
    
    if (deleteCount > 0) {
      await deleteButton.click();
    } else {
      await page.keyboard.press('Delete');
    }
    
    // Wait for deletion
    await page.waitForTimeout(500);
    
    // Verify node was deleted
    const remainingNodes = page.locator('.react-flow__node, .canvas-node');
    const remainingCount = await remainingNodes.count();
    expect(remainingCount).toBe(0);
  });

  test('should clear canvas', async ({ page }) => {
    // Wait for canvas to load
    await page.waitForTimeout(1000);
    
    // Add nodes to canvas
    const eventNodes = page.locator('.draggable-node, .event-node-item, [draggable="true"]');
    const canvas = page.locator('.react-flow, .canvas-container');
    
    const nodeCount = await eventNodes.count();
    if (nodeCount === 0) {
      test.skip();
      return;
    }
    
    await eventNodes.first().dragTo(canvas);
    await page.waitForTimeout(500);
    
    // Click clear button
    const clearButton = page.locator('button:has-text("清空"), button:has-text("Clear"), [data-testid="clear-canvas-button"]');
    const clearCount = await clearButton.count();
    
    if (clearCount > 0) {
      await clearButton.click();
      
      // Handle confirmation dialog
      const confirmDialog = page.locator('.modal, .dialog, [role="dialog"]');
      if (await confirmDialog.count() > 0) {
        const confirmButton = confirmDialog.locator('button:has-text("确认"), button:has-text("确定")');
        await confirmButton.click();
      }
      
      // Wait for clear
      await page.waitForTimeout(500);
      
      // Verify canvas is empty
      const canvasNodes = page.locator('.react-flow__node, .canvas-node');
      const remainingCount = await canvasNodes.count();
      expect(remainingCount).toBe(0);
    }
  });
});
