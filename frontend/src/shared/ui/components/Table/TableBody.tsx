export const TableBody = React.memo(<TData extends Record<string, unknown>>({
  className = '',
  children,
}: TableBodyProps) => {
  return <tbody className={`table-tbody ${className}`}>{children}</tbody>;
}) as <TData extends Record<string, unknown>>(props: TableBodyProps) => React.JSX.Element;