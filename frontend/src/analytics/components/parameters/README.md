# Parameter Management Components

This directory contains React components for parameter management in the Event2Table analytics application.

## Components

### 1. CommonParamsModal.jsx

**Purpose**: Drawer modal for displaying common parameters list with statistics.

**Features**:
- Displays all common parameters for a game
- Shows occurrence count and coverage ratio
- Search functionality
- Refresh button
- Type badges with color coding

**Usage**:
```jsx
import { CommonParamsModal } from '@analytics/components/parameters';

function MyComponent() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <CommonParamsModal
      isOpen={isOpen}
      gameGid={10000147}
      onClose={() => setIsOpen(false)}
    />
  );
}
```

**Props**:
- `isOpen` (boolean): Whether the modal is open
- `gameGid` (number): Game GID for filtering parameters
- `onClose` (function): Close handler callback

---

### 2. ParameterFilters.jsx

**Purpose**: Filter component for parameter list with mode selection and event filtering.

**Features**:
- Segmented control for mode selection (all/common/non-common)
- Event dropdown for filtering by event
- "View Common Parameters" button
- Uses GraphQL for event data fetching

**Usage**:
```jsx
import { ParameterFilters } from '@analytics/components/parameters';

function ParametersList() {
  const [mode, setMode] = useState('all');
  const [selectedEvent, setSelectedEvent] = useState(null);

  return (
    <ParameterFilters
      gameGid={10000147}
      mode={mode}
      selectedEvent={selectedEvent}
      onModeChange={setMode}
      onEventChange={setSelectedEvent}
      onViewCommonParams={() => setShowCommonModal(true)}
    />
  );
}
```

**Props**:
- `gameGid` (number): Game GID for filtering
- `mode` (string): Filter mode - 'all' | 'common' | 'non-common'
- `selectedEvent` (string|null): Selected event ID for filtering
- `onModeChange` (function): Callback when mode changes
- `onEventChange` (function): Callback when event selection changes
- `onViewCommonParams` (function): Callback to open common params modal

---

### 3. ParameterCard.jsx

**Purpose**: Individual parameter card component with edit functionality.

**Features**:
- Displays parameter information (name, Chinese name, type)
- Color-coded type badges
- Event count display
- Edit button for type change
- Hover effects

**Usage**:
```jsx
import { ParameterCard } from '@analytics/components/parameters';

function ParametersGrid({ parameters }) {
  const [selectedParam, setSelectedParam] = useState(null);

  return (
    <div className="grid gap-4">
      {parameters.map(param => (
        <ParameterCard
          key={param.id}
          parameter={param}
          onEdit={setSelectedParam}
        />
      ))}
    </div>
  );
}
```

**Props**:
- `parameter` (object): Parameter data object
  - `id` (number): Parameter ID
  - `paramName` (string): Parameter name
  - `paramNameCn` (string): Parameter Chinese name
  - `type` (string): Parameter type (base/param/custom)
  - `gameGid` (number): Game GID
  - `eventCount` (number, optional): Number of events using this parameter
- `onEdit` (function): Edit button click handler

---

### 4. ParameterTypeEditor.jsx

**Purpose**: Modal for editing parameter type with validation.

**Features**:
- Dropdown to select new parameter type
- Type descriptions for user guidance
- Validation before submission
- Warning message about potential impact
- Uses GraphQL mutation for updates

**Usage**:
```jsx
import { ParameterTypeEditor } from '@analytics/components/parameters';

function ParametersList() {
  const [selectedParam, setSelectedParam] = useState(null);
  const queryClient = useQueryClient();

  const handleSuccess = () => {
    setSelectedParam(null);
    queryClient.invalidateQueries({ queryKey: ['parameters'] });
  };

  return (
    <>
      {/* Your parameter list */}
      <ParameterTypeEditor
        isOpen={!!selectedParam}
        parameter={selectedParam}
        onClose={() => setSelectedParam(null)}
        onSuccess={handleSuccess}
      />
    </>
  );
}
```

**Props**:
- `isOpen` (boolean): Whether the modal is open
- `parameter` (object): Parameter object to edit
  - `id` (number): Parameter ID
  - `paramName` (string): Parameter name
  - `type` (string): Current parameter type
  - `gameGid` (number): Game GID
- `onClose` (function): Close handler callback
- `onSuccess` (function): Success callback after type change

---

## GraphQL Dependencies

These components require the following GraphQL queries and mutations:

### Queries
```graphql
# Get events for dropdown
query GetEvents($gameGid: Int!) {
  events(gameGid: $gameGid) {
    id
    eventName
    eventNameCn
  }
}

# Get common parameters
query GetCommonParameters($gameGid: Int!) {
  commonParameters(gameGid: $gameGid) {
    paramName
    paramNameCn
    type
    occurrenceCount
    ratio
  }
}
```

### Mutations
```graphql
# Change parameter type
mutation ChangeParameterType($paramId: Int!, $newType: String!) {
  changeParameterType(paramId: $paramId, newType: $newType) {
    ok
    parameter {
      id
      paramName
      type
    }
    errors
  }
}
```

---

## Styling

All components use Tailwind CSS for styling with the "Cyberpunk Lab" theme:
- Dark mode colors (slate-800, slate-900)
- Accent colors (cyan-400, purple-400, green-400)
- Glassmorphism effects (bg-opacity, backdrop-blur)
- Hover transitions and glow effects

---

## Integration Example

```jsx
import React, { useState } from 'react';
import { useQuery } from '@apollo/client';
import {
  ParameterFilters,
  ParameterCard,
  ParameterTypeEditor,
  CommonParamsModal
} from '@analytics/components/parameters';
import { GET_PARAMETERS } from '@graphql/queries';

function ParametersPage({ gameGid }) {
  const [mode, setMode] = useState('all');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [selectedParam, setSelectedParam] = useState(null);
  const [showCommonModal, setShowCommonModal] = useState(false);

  const { data, loading, error } = useQuery(GET_PARAMETERS, {
    variables: { gameGid, mode, eventId: selectedEvent },
  });

  const parameters = data?.parameters || [];

  return (
    <div className="space-y-6">
      {/* Filters */}
      <ParameterFilters
        gameGid={gameGid}
        mode={mode}
        selectedEvent={selectedEvent}
        onModeChange={setMode}
        onEventChange={setSelectedEvent}
        onViewCommonParams={() => setShowCommonModal(true)}
      />

      {/* Parameters Grid */}
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div className="grid gap-4">
          {parameters.map(param => (
            <ParameterCard
              key={param.id}
              parameter={param}
              onEdit={setSelectedParam}
            />
          ))}
        </div>
      )}

      {/* Common Parameters Modal */}
      <CommonParamsModal
        isOpen={showCommonModal}
        gameGid={gameGid}
        onClose={() => setShowCommonModal(false)}
      />

      {/* Type Editor Modal */}
      <ParameterTypeEditor
        isOpen={!!selectedParam}
        parameter={selectedParam}
        onClose={() => setSelectedParam(null)}
        onSuccess={() => {
          setSelectedParam(null);
          // Refetch parameters
        }}
      />
    </div>
  );
}
```

---

## Notes

- All components use Apollo Client for GraphQL operations
- Components follow the existing design patterns in `frontend/src/analytics/components/`
- Type safety is maintained with proper PropTypes/TypeScript types
- Error handling is implemented with toast notifications
- Loading states are handled with Spinner components
