# Table Component

## Overview

The Table component provides a powerful data table with sorting, filtering, pagination, and selection capabilities.

## Features

- **Sorting**: Column-based sorting (asc/desc)
- **Filtering**: Global and column-specific filtering
- **Pagination**: Configurable page size and navigation
- **Selection**: Single or multi-row selection
- **Responsive**: Adapts to different screen sizes
- **Virtual Scrolling**: Efficient rendering for large datasets
- **Accessibility**: Keyboard navigation and ARIA support

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `data` | `T[]` | `[]` | Table data |
| `columns` | `Column<T>[]` | `[]` | Column definitions |
| `sortable` | `boolean` | `false` | Enable sorting |
| `filterable` | `boolean` | `false` | Enable filtering |
| `selectable` | `boolean \| 'single' \| 'multiple'` | `false` | Enable selection |
| `pagination` | `boolean \| PaginationConfig` | `false` | Enable pagination |
| `loading` | `boolean` | `false` | Show loading state |
| `emptyMessage` | `string` | `'No data'` | Message when no data |

## Column Definition

```typescript
interface Column<T> {
  id: string;
  header: string;
  accessor: keyof T | ((row: T) => any);
  sortable?: boolean;
  filterable?: boolean;
  width?: number | string;
  cell?: (value: any, row: T) => ReactNode;
}
```

## Usage Examples

### Basic Table

```tsx
import { Table } from '@ui-components/Table';

const data = [
  { id: 1, name: 'John', age: 30 },
  { id: 2, name: 'Jane', age: 25 },
];

const columns = [
  { id: 'name', header: 'Name', accessor: 'name' },
  { id: 'age', header: 'Age', accessor: 'age' },
];

function Example() {
  return <Table data={data} columns={columns} />;
}
```

### Sortable Table

```tsx
const columns = [
  { 
    id: 'name', 
    header: 'Name', 
    accessor: 'name',
    sortable: true 
  },
  { 
    id: 'age', 
    header: 'Age', 
    accessor: 'age',
    sortable: true 
  },
];

<Table 
  data={data} 
  columns={columns}
  sortable
/>
```

### Table with Custom Cell Renderer

```tsx
const columns = [
  { 
    id: 'status', 
    header: 'Status', 
    accessor: 'status',
    cell: (value) => (
      <span className={`badge ${value}`}>
        {value}
      </span>
    )
  },
];
```

### Table with Selection

```tsx
<Table
  data={data}
  columns={columns}
  selectable="multiple"
  onSelectionChange={(selected) => console.log(selected)}
/>
```

### Table with Pagination

```tsx
<Table
  data={data}
  columns={columns}
  pagination={{
    pageSize: 10,
    pageSizeOptions: [10, 25, 50, 100],
  }}
/>
```

### Table with Filtering

```tsx
<Table
  data={data}
  columns={columns}
  filterable
  onFilterChange={(filters) => console.log(filters)}
/>
```

## Advanced Features

### Virtual Scrolling

For large datasets (1000+ rows), enable virtual scrolling:

```tsx
<Table
  data={largeData}
  columns={columns}
  virtualScroll
  rowHeight={50}
/>
```

### Server-Side Operations

```tsx
<Table
  data={data}
  columns={columns}
  pagination
  onServerSideChange={({ page, pageSize, sort, filter }) => {
    fetchData(page, pageSize, sort, filter);
  }}
/>
```

### Custom Row Actions

```tsx
const columns = [
  // ... other columns
  {
    id: 'actions',
    header: 'Actions',
    cell: (_, row) => (
      <div className="flex gap-2">
        <button onClick={() => editRow(row)}>Edit</button>
        <button onClick={() => deleteRow(row)}>Delete</button>
      </div>
    ),
  },
];
```

## Accessibility

- Keyboard navigation (Arrow keys, Enter, Space)
- ARIA attributes: `aria-sort`, `aria-selected`, `aria-rowcount`
- Screen reader announcements
- Focus management

## Performance Tips

- Use virtual scrolling for large datasets
- Implement server-side pagination/filtering for big data
- Memoize custom cell renderers
- Avoid complex computations in cell renderers
- Use stable column definitions

## Best Practices

- Keep column headers concise
- Provide clear empty states
- Use appropriate data types
- Test with various data sizes
- Implement loading states
- Provide feedback for user actions
