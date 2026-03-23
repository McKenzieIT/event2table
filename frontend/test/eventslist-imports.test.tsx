// Test EventsListGraphQL imports
import { describe, it, expect, vi } from 'vitest';

describe('EventsListGraphQL Import Test', () => {
  it('should import GET_EVENTS from @/graphql/queries', async () => {
    const queries = await import('@/graphql/queries');
    console.log('queries exports:', Object.keys(queries));
    expect(queries.GET_EVENTS).toBeDefined();
    expect(queries.GET_CATEGORIES).toBeDefined();
  });

  it('should import DELETE_EVENT from @shared/graphql/mutations', async () => {
    const mutations = await import('@shared/graphql/mutations');
    console.log('mutations exports:', Object.keys(mutations));
    expect(mutations.DELETE_EVENT).toBeDefined();
  });

  it('should import from @shared/ui', async () => {
    const ui = await import('@shared/ui');
    console.log('@shared/ui has Button:', !!ui.Button);
    console.log('@shared/ui has Input:', !!ui.Input);
    console.log('@shared/ui has SearchInput:', !!ui.SearchInput);
    console.log('@shared/ui has Checkbox:', !!ui.Checkbox);
    console.log('@shared/ui has Select:', !!ui.Select);
    console.log('@shared/ui has Badge:', !!ui.Badge);
    console.log('@shared/ui has Spinner:', !!ui.Spinner);
    console.log('@shared/ui has useToast:', !!ui.useToast);
    console.log('@shared/ui has SelectGamePrompt:', !!ui.SelectGamePrompt);
    
    expect(ui.Button).toBeDefined();
    expect(ui.Input).toBeDefined();
    expect(ui.SearchInput).toBeDefined();
    expect(ui.Checkbox).toBeDefined();
    expect(ui.Select).toBeDefined();
    expect(ui.Badge).toBeDefined();
    expect(ui.Spinner).toBeDefined();
    expect(ui.useToast).toBeDefined();
    expect(ui.SelectGamePrompt).toBeDefined();
  });

  it('should import ConfirmDialog', async () => {
    const { ConfirmDialog } = await import('@shared/ui/ConfirmDialog/ConfirmDialog');
    console.log('ConfirmDialog:', ConfirmDialog);
    expect(ConfirmDialog).toBeDefined();
  });
});
