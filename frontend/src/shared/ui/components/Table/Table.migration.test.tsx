import { render, screen } from '@testing-library/react';
import { Table } from '../Table';

describe('Table Migration', () => {
  const mockData = [
    { id: 1, name: 'Test 1' },
    { id: 2, name: 'Test 2' },
  ];

  const mockColumns = [
    { id: 'id', header: 'ID', accessorKey: 'id' },
    { id: 'name', header: 'Name', accessorKey: 'name' },
  ];

  it('new Table should render data correctly', () => {
    render(<Table data={mockData} columns={mockColumns} />);
    expect(screen.getByText('Test 1')).toBeInTheDocument();
    expect(screen.getByText('Test 2')).toBeInTheDocument();
  });

  it('new Table should support virtual scrolling', () => {
    const largeData = Array.from({ length: 1000 }, (_, i) => ({
      id: i + 1,
      name: `Test ${i + 1}`,
    }));
    
    const { container } = render(
      <Table data={largeData} columns={mockColumns} virtual maxHeight={500} />
    );
    
    expect(container.querySelector('[data-virtualizer]')).toBeInTheDocument();
  });
});
