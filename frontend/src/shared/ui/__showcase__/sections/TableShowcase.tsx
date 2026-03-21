import React, { useMemo } from 'react';
import { Card, Badge } from '@shared/ui';
import Table from '@shared/ui/components/Table';

interface SampleData {
  id: number;
  name: string;
  events: number;
  status: 'active' | 'draft' | 'archived';
  lastUpdate: string;
}

const TableShowcase: React.FC = React.memo(() => {
  const sampleData: SampleData[] = useMemo(() => [
    { id: 1, name: 'Game of Thrones', events: 17, status: 'active', lastUpdate: '2024-02-10' },
    { id: 2, name: 'Breaking Bad', events: 12, status: 'draft', lastUpdate: '2024-02-09' },
    { id: 3, name: 'Stranger Things', events: 23, status: 'active', lastUpdate: '2024-02-08' },
    { id: 4, name: 'The Crown', events: 8, status: 'archived', lastUpdate: '2024-02-07' },
    { id: 5, name: 'The Witcher', events: 15, status: 'active', lastUpdate: '2024-02-06' },
  ], []);

  const getStatusBadge = React.useCallback((status: SampleData['status']): React.JSX.Element => {
    const variants: Record<string, 'success' | 'warning' | 'default'> = {
      active: 'success',
      draft: 'warning',
      archived: 'default'
    };
    return <Badge variant={variants[status]}>{status}</Badge>;
  }, []);

  return (
    <section className="showcase-section">
      <h2 className="section-title">Tables</h2>
      <Card>
        <Card.Body>
          <Table striped hoverable>
            <Table.Header>
              <Table.Row>
                <Table.Head sortable>Game Name</Table.Head>
                <Table.Head sortable align="center">Events</Table.Head>
                <Table.Head sortable>Status</Table.Head>
                <Table.Head sortable align="right">Last Update</Table.Head>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {sampleData.map((game) => (
                <Table.Row key={game.id}>
                  <Table.Cell>{game.name}</Table.Cell>
                  <Table.Cell align="center">{game.events}</Table.Cell>
                  <Table.Cell>{getStatusBadge(game.status)}</Table.Cell>
                  <Table.Cell align="right">{game.lastUpdate}</Table.Cell>
                </Table.Row>
              ))}
            </Table.Body>
          </Table>
        </Card.Body>
      </Card>
    </section>
  );
});

TableShowcase.displayName = 'TableShowcase';

export default TableShowcase;
