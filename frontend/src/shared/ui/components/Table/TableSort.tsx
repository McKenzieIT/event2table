export const TableSort = React.memo(({
  direction,
  onSort,
}: TableSortProps) => {
  const handleClick = () => {
    if (direction === 'asc') {
      onSort('desc');
    } else if (direction === 'desc') {
      onSort('asc');
    } else {
      onSort('asc');
    }
  };

  const getSortIcon = () => {
    if (direction === 'asc') return '↑';
    if (direction === 'desc') return '↓';
    return '↕';
  };

  return (
    <button
      className="table-sort-button"
      onClick={handleClick}
      aria-label={`Sort ${direction || 'unsorted'}`}
    >
      <span className="table-sort-icon">{getSortIcon()}</span>
    </button>
  );
}) as (props: TableSortProps) => React.JSX.Element;
