import React, { useState } from 'react';
import { TableFilterProps, RowData } from './Table.types';

/**
 * TableFilter Component
 * 
 * Renders filter controls for a column with support for:
 * - Text filtering
 * - Select filtering
 * - Date filtering
 * - Number filtering
 */
export const TableFilter = React.memo(<TData extends RowData>({
  column,
  value,
  onChange,
}: TableFilterProps<TData>) => {
  const [localValue, setLocalValue] = useState(value as string || '');

  const handleChange = (newValue: unknown) => {
    setLocalValue(newValue as string);
    onChange(newValue);
  };

  const filterType = column.filterType || 'text';

  if (filterType === 'select' && column.filterOptions) {
    return (
      <select
        value={localValue as string}
        onChange={(e) => handleChange(e.target.value)}
        className="table-filter-select"
      >
        <option value="">All</option>
        {column.filterOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    );
  }

  if (filterType === 'date') {
    return (
      <input
        type="date"
        value={localValue as string}
        onChange={(e) => handleChange(e.target.value)}
        className="table-filter-input"
      />
    );
  }

  if (filterType === 'number') {
    return (
      <input
        type="number"
        value={localValue as string}
        onChange={(e) => handleChange(e.target.value)}
        className="table-filter-input"
        placeholder="Filter..."
      />
    );
  }

  // Default: text filter
  return (
    <input
      type="text"
      value={localValue as string}
      onChange={(e) => handleChange(e.target.value)}
      className="table-filter-input"
      placeholder="Filter..."
    />
  );
};

TableFilter.displayName = 'TableFilter';
