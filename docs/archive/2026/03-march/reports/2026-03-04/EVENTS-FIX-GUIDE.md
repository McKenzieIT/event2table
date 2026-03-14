# EventForm GraphQL Migration Guide

## Problem

EventForm component uses REST API (TanStack Query) while EventsList uses GraphQL (Apollo Client), causing event creation to fail.

## Solution

Migrate EventForm to use GraphQL mutations.

---

## Step-by-Step Migration

### Step 1: Update Imports

**File**: `frontend/src/analytics/pages/EventForm.tsx`

**Remove**:
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
```

**Add**:
```typescript
import { useMutation } from '@apollo/client/react';
import { CREATE_EVENT, UPDATE_EVENT } from '@/graphql/mutations';
```

---

### Step 2: Check GraphQL Mutations Exist

**File**: `frontend/src/graphql/mutations.ts`

**Verify these mutations exist**:
```typescript
export const CREATE_EVENT = gql`
  mutation CreateEvent(
    $gameGid: Int!
    $eventName: String!
    $eventNameCn: String!
    $categoryId: Int!
    $description: String
  ) {
    createEvent(
      gameGid: $gameGid
      eventName: $eventName
      eventNameCn: $eventNameCn
      categoryId: $categoryId
      description: $description
    ) {
      ok
      errors
      event {
        id
        eventName
        eventNameCn
        categoryId
        description
      }
    }
  }
`;

export const UPDATE_EVENT = gql`
  mutation UpdateEvent(
    $id: Int!
    $gameGid: Int!
    $eventName: String!
    $eventNameCn: String!
    $categoryId: Int!
    $description: String
  ) {
    updateEvent(
      id: $id
      gameGid: $gameGid
      eventName: $eventName
      eventNameCn: $eventNameCn
      categoryId: $categoryId
      description: $description
    ) {
      ok
      errors
      event {
        id
        eventName
        eventNameCn
        categoryId
        description
      }
    }
  }
`;
```

**If mutations don't exist, add them to `frontend/src/graphql/mutations.ts`**

---

### Step 3: Replace Query Client Mutation

**Find** (around line 100-150):
```typescript
const queryClient = useQueryClient();

const mutation = useMutation({
  mutationFn: async (data: EventFormData) => {
    const url = isEdit
      ? `/api/events/${id}`
      : '/api/events';

    const response = await fetch(url, {
      method: isEdit ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Failed to save event');
    }

    return response.json();
  },
  onSuccess: () => {
    success(isEdit ? 'Event updated successfully' : 'Event created successfully');
    queryClient.invalidateQueries({ queryKey: ['events'] });
    navigate(`/events?game_gid=${game_gid}`);
  },
  onError: (error: Error) => {
    showError(`Failed to save event: ${error.message}`);
  },
});
```

**Replace with**:
```typescript
const [executeMutation, { loading: isSaving }] = useMutation(
  isEdit ? UPDATE_EVENT : CREATE_EVENT,
  {
    onCompleted: (data) => {
      const response = isEdit ? data.updateEvent : data.createEvent;

      if (response.ok) {
        success(isEdit ? 'Event updated successfully' : 'Event created successfully');
        navigate(`/events?game_gid=${game_gid}`);
      } else {
        showError(`Failed to save event: ${response.errors?.join(', ') || 'Unknown error'}`);
      }
    },
    onError: (error) => {
      showError(`Failed to save event: ${error.message}`);
    }
  }
);
```

---

### Step 4: Update Form Submit Handler

**Find** (around line 200-250):
```typescript
const handleSubmit = () => {
  const newErrors: FormErrors = {};

  // Validation logic...

  if (Object.keys(newErrors).length > 0) {
    setErrors(newErrors);
    return;
  }

  mutation.mutate(formData);
};
```

**Replace with**:
```typescript
const handleSubmit = () => {
  const newErrors: FormErrors = {};

  // Keep existing validation logic...

  if (Object.keys(newErrors).length > 0) {
    setErrors(newErrors);
    return;
  }

  // Prepare variables for GraphQL mutation
  const variables = {
    gameGid: parseInt(game_gid),
    eventName: formData.event_name,
    eventNameCn: formData.event_name_cn,
    categoryId: parseInt(formData.category_id) || 1,
    description: formData.description || null
  };

  if (isEdit) {
    executeMutation({
      variables: {
        id: parseInt(id),
        ...variables
      }
    });
  } else {
    executeMutation({
      variables
    });
  }
};
```

---

### Step 5: Update Loading State

**Find**:
```typescript
{isPending && <Spinner />}
```

**Replace with**:
```typescript
{isSaving && <Spinner />}
```

---

### Step 6: Remove Query Client References

**Remove**:
```typescript
const queryClient = useQueryClient();
```

**Remove**:
```typescript
queryClient.invalidateQueries({ queryKey: ['events'] });
```

---

### Step 7: Update Categories Query (Optional but Recommended)

**Find**:
```typescript
const { data: categoriesData, isLoading: categoriesLoading } = useQuery({
  queryKey: ['categories'],
  queryFn: async () => {
    const response = await fetch('/api/categories');
    if (!response.ok) throw new Error('Failed to fetch categories');
    return response.json();
  },
});
```

**Replace with**:
```typescript
import { GET_CATEGORIES } from '@/graphql/queries';

const { data: categoriesData, loading: categoriesLoading } = useQuery(GET_CATEGORIES, {
  variables: { limit: 100, offset: 0 },
  fetchPolicy: 'cache-first',
});
```

**Update categories extraction**:
```typescript
// Old
const categories = categoriesData?.data || [];

// New
const categories = categoriesData?.categories || [];
```

---

## Step 8: Test the Migration

### 1. Build and Run
```bash
cd frontend
npm run build
npm run dev
```

### 2. Test Event Creation
- Navigate to: http://localhost:5173/#/events/create?game_gid=10000147
- Fill in form:
  - 事件名称: `test_graphql_event`
  - 中文名称: `GraphQL测试事件`
  - 分类: Select any category
- Click "保存" (Save)
- Should redirect to Events List
- Verify event appears in list

### 3. Verify Backend
```bash
sqlite3 data/dwd_generator.db "SELECT event_name, event_name_cn FROM log_events WHERE event_name = 'test_graphql_event'"
```

### 4. Test Event Editing
- Click "编辑" on any event
- Modify event name
- Click "保存"
- Verify changes saved

### 5. Test Error Handling
- Try to create event with empty name (should show validation error)
- Try to create duplicate event (should show backend error)

---

## Verification Checklist

- [ ] EventForm imports updated (Apollo Client, not TanStack Query)
- [ ] GraphQL mutations exist in `frontend/src/graphql/mutations.ts`
- [ ] Form submission uses `executeMutation` instead of `mutation.mutate`
- [ ] Categories query uses GraphQL (GET_CATEGORIES)
- [ ] Loading state uses `isSaving` instead of `isPending`
- [ ] No references to `queryClient` remain
- [ ] Event creation works (event saved to database)
- [ ] Event editing works (changes saved)
- [ ] Error handling works (validation + backend errors)
- [ ] Success toast notifications appear

---

## Estimated Time

- Step 1-3 (Import & Setup): 15 minutes
- Step 4-6 (Mutation Logic): 30 minutes
- Step 7 (Categories Query): 15 minutes
- Step 8 (Testing): 30 minutes

**Total**: ~1.5 hours

---

## Troubleshooting

### Issue: "GraphQL mutation not found"

**Solution**: Check that mutations are exported from `frontend/src/graphql/mutations.ts`

### Issue: "Variable '$gameGid' of type 'Int!' is required"

**Solution**: Ensure `gameGid` is converted to integer:
```typescript
gameGid: parseInt(game_gid)  // ✅ Correct
gameGid: game_gid            // ❌ Wrong (string instead of int)
```

### Issue: "Category required"

**Solution**: Ensure categoryId is provided:
```typescript
categoryId: parseInt(formData.category_id) || 1  // ✅ Default to 1 if empty
```

### Issue: "Mutation executed but event not created"

**Solution**: Check browser Network tab for GraphQL response, verify backend GraphQL endpoint is working

---

## Files to Modify

1. `frontend/src/analytics/pages/EventForm.tsx` - Main migration
2. `frontend/src/graphql/mutations.ts` - Add mutations if missing
3. `frontend/src/graphql/queries.ts` - Verify GET_CATEGORIES exists

---

## After Migration

Once migration is complete, the entire Events module will be 100% GraphQL:

| Component | API | Status |
|-----------|-----|--------|
| EventsListGraphQL | GraphQL | ✅ Complete |
| EventDetailGraphQL | GraphQL | ✅ Complete |
| EventForm | GraphQL | ⚠️ In Progress |
| Events module | GraphQL | ⚠️ 95% Complete |

**Target**: 100% GraphQL integration for Events module

---

**Guide Created**: 2026-03-03
**Estimated Completion**: 1.5 hours
**Priority**: HIGH (fixes critical event creation failure)
