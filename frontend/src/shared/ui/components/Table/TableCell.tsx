export const TableCell = React.memo(<TData extends RowData, TValue = unknown>({
  className = '',
  children,
  align = 'left',
  onClick,
  onDoubleClick,
  pinned = false,
  pinnedLeft = false,
  pinnedRight = false,
  style,
}: TableCellProps<TData, TValue>) => {
  const cellClasses = [
    'table-td',
    align && `table-td--${align}`,
    pinned && 'table-td--pinned',
    pinnedLeft && 'table-td--pinned-left',
    pinnedRight && 'table-td--pinned-right',
    className,
  ].filter(Boolean).join(' ');

  return (
    <td
      className={cellClasses}
      style={style}
      onClick={onClick}
      onDoubleClick={onDoubleClick}
    >
      {children}
    </td>
  );
}) as <TData extends RowData, TValue = unknown>(props: TableCellProps<TData, TValue>) => React.JSX.Element;
