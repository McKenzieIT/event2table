/**
 * Component Showcase Page
 *
 * Interactive preview of all Cyberpunk Lab themed components.
 * Use this page to verify component styles and interactions before migration.
 *
 * @example
 * // Import and use in your app
 * import ComponentShowcase from '@shared/ui/__showcase__/ComponentShowcase';
 *
 * function App() {
 *   return <ComponentShowcase />;
 * }
 */

import React, { useState } from 'react';
import { Button } from '../Button/Button';
import { Card } from '../Card/Card';
import { Input } from '../Input/Input';
import { Table } from '../Table/Table';
import { Modal } from '../Modal/Modal';
import { Badge } from '../Badge/Badge';
import { useToast, ToastProvider } from '../Toast/Toast';
import { TextArea } from '../TextArea/TextArea';
import { Select } from '../Select/Select';
import { Checkbox } from '../Checkbox/Checkbox';
import { Radio } from '../Radio/Radio';
import { Switch } from '../Switch/Switch';
import { Spinner } from '../Spinner/Spinner';
import './ComponentShowcase.css';

function ComponentShowcaseContent() {
  const [inputValue, setInputValue] = useState('');
  const [isloading, setIsLoading] = useState(false);
  const { success, error, warning, info } = useToast();

  // New component states
  const [textAreaValue, setTextAreaValue] = useState('');
  const [selectedGame, setSelectedGame] = useState('');
  const [checkboxChecked, setCheckboxChecked] = useState(false);
  const [checkboxIndeterminate, setCheckboxIndeterminate] = useState(true);
  const [selectedRadio, setSelectedRadio] = useState('football');
  const [switchEnabled, setSwitchEnabled] = useState(false);
  const [switchAutoSave, setSwitchAutoSave] = useState(true);

  const handleClick = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  };

  const [modalOpen, setModalOpen] = useState(false);

  const sampleData = [
    { id: 1, name: 'Game of Thrones', events: 17, status: 'active', lastUpdate: '2024-02-10' },
    { id: 2, name: 'Breaking Bad', events: 12, status: 'draft', lastUpdate: '2024-02-09' },
    { id: 3, name: 'Stranger Things', events: 23, status: 'active', lastUpdate: '2024-02-08' },
    { id: 4, name: 'The Crown', events: 8, status: 'archived', lastUpdate: '2024-02-07' },
    { id: 5, name: 'The Witcher', events: 15, status: 'active', lastUpdate: '2024-02-06' },
  ];

  const gameOptions = [
    { value: 'football', label: 'Football' },
    { value: 'basketball', label: 'Basketball' },
    { value: 'baseball', label: 'Baseball' },
    { value: 'hockey', label: 'Hockey' },
    { value: 'soccer', label: 'Soccer' },
  ];

  const radioOptions = [
    { value: 'football', label: 'Football' },
    { value: 'basketball', label: 'Basketball' },
    { value: 'baseball', label: 'Baseball' },
  ];

  const getStatusBadge = (status) => {
    const variants = {
      active: 'success',
      draft: 'warning',
      archived: 'default'
    };
    return <Badge variant={variants[status]}>{status}</Badge>;
  };

  return (
    <div className="component-showcase">
      <div className="showcase-header">
        <h1 className="showcase-title">Component Library Showcase</h1>
        <p className="showcase-subtitle">Cyberpunk Lab Theme - Interactive Preview</p>
      </div>

      {/* Buttons Section */}
      <section className="showcase-section">
        <h2 className="section-title">Buttons</h2>
        <div className="showcase-row">
          <Button variant="primary">Primary Button</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost Button</Button>
          <Button variant="danger">Danger Button</Button>
        </div>
        <div className="showcase-row">
          <Button size="sm">Small Primary</Button>
          <Button size="md">Medium Primary</Button>
          <Button size="lg">Large Primary</Button>
        </div>
        <div className="showcase-row">
          <Button loading>Loading...</Button>
          <Button disabled>Disabled</Button>
        </div>
      </section>

      {/* Cards Section */}
      <section className="showcase-section">
        <h2 className="section-title">Cards</h2>
        <div className="cards-grid">
          <Card>
            <Card.Header>
              <Card.Title>Default Card</Card.Title>
            </Card.Header>
            <Card.Body>
              <p>Default glassmorphism card with subtle border.</p>
            </Card.Body>
          </Card>

          <Card hoverable>
            <Card.Header>
              <Card.Title>Hoverable Card</Card.Title>
            </Card.Header>
            <Card.Body>
              <p>Hover to see the lift effect and cyan glow.</p>
            </Card.Body>
          </Card>

          <Card glowing>
            <Card.Header>
              <Card.Title>Glowing Card</Card.Title>
            </Card.Header>
            <Card.Body>
              <p>Continuous cyan glow effect.</p>
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Header>
              <Card.Title>Outlined Card</Card.Title>
            </Card.Header>
            <Card.Body>
              <p>Minimal style with stronger border.</p>
            </Card.Body>
          </Card>
        </div>
      </section>

      {/* Inputs Section */}
      <section className="showcase-section">
        <h2 className="section-title">Inputs</h2>
        <div className="inputs-grid">
          <div>
            <Input
              label="Text Input"
              placeholder="Enter game name..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
            />
            <Input
              label="With Helper Text"
              placeholder="Enter description..."
              helperText="This field supports markdown formatting."
            />
            <Input
              label="Error State"
              placeholder="This field has an error..."
              error="This field is required"
              required
            />
            <Input
              label="Disabled Input"
              placeholder="Cannot edit..."
              disabled
            />
          </div>

          <div>
            <Input
              type="password"
              label="Password Input"
              placeholder="Enter password..."
            />
            <Input
              type="number"
              label="Number Input"
              placeholder="Enter number..."
            />
          </div>
        </div>
      </section>

      {/* Badges Section */}
      <section className="showcase-section">
        <h2 className="section-title">Badges</h2>
        <div className="showcase-row">
          <Badge variant="default">Default</Badge>
          <Badge variant="primary">Primary</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="danger">Danger</Badge>
          <Badge variant="info">Info</Badge>
        </div>
        <div className="showcase-row">
          <Badge variant="success" dot>Active</Badge>
          <Badge variant="warning" dot>Draft</Badge>
          <Badge variant="default" dot>Archived</Badge>
        </div>
        <div className="showcase-row">
          <Badge variant="primary" pill>Pill Badge</Badge>
          <Badge variant="success" pill>Success Pill</Badge>
        </div>
      </section>

      {/* Table Section */}
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

      {/* Modal Section */}
      <section className="showcase-section">
        <h2 className="section-title">Modal</h2>
        <div className="showcase-row">
          <Button variant="primary" onClick={() => setModalOpen(true)}>
            Open Modal
          </Button>
          <Button variant="danger" onClick={() => setModalOpen(true)}>
            Delete Confirmation
          </Button>
        </div>
      </section>

      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Confirm Action"
        size="md"
        showFooter
        footerActions={
          <>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={() => setModalOpen(false)}>
              Confirm
            </Button>
          </>
        }
      >
        <p style={{ marginBottom: '16px' }}>
          This is a modal dialog with glassmorphism effect and backdrop blur.
        </p>
        <p>
          Modals support different sizes (sm, md, lg, xl, full) and variants (default, danger, warning).
        </p>
      </Modal>

      {/* Toast Section */}
      <section className="showcase-section">
        <h2 className="section-title">Toast Notifications</h2>
        <Card>
          <Card.Body>
            <p style={{ marginBottom: '16px', color: 'var(--text-secondary, #94A3B8)' }}>
              Click the buttons below to see toast notifications with different variants.
            </p>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <Button variant="primary" onClick={() => success('Operation completed successfully!')}>
                Success Toast
              </Button>
              <Button variant="danger" onClick={() => error('An error occurred. Please try again.')}>
                Error Toast
              </Button>
              <Button variant="warning" onClick={() => warning('Warning: This action cannot be undone.')}>
                Warning Toast
              </Button>
              <Button variant="ghost" onClick={() => info('Here is some useful information for you.')}>
                Info Toast
              </Button>
            </div>
          </Card.Body>
        </Card>
      </section>

      {/* TextArea Section */}
      <section className="showcase-section">
        <h2 className="section-title">TextArea</h2>
        <div className="inputs-grid">
          <div>
            <TextArea
              label="Description"
              placeholder="Enter game description..."
              value={textAreaValue}
              onChange={(e) => setTextAreaValue(e.target.value)}
              rows={4}
            />
            <TextArea
              label="With Character Count"
              placeholder="Enter description (max 200 chars)..."
              maxLength={200}
              showCount
              rows={3}
              helperText="This field has a character limit."
            />
            <TextArea
              label="Error State"
              placeholder="This field has an error..."
              error="Description is required"
              required
              rows={3}
            />
          </div>
          <div>
            <TextArea
              label="Disabled TextArea"
              placeholder="Cannot edit..."
              disabled
              rows={4}
            />
            <TextArea
              label="Non-resizable"
              placeholder="This textarea cannot be resized..."
              resize="none"
              rows={3}
              helperText="Resize handle is disabled."
            />
          </div>
        </div>
      </section>

      {/* Select Section */}
      <section className="showcase-section">
        <h2 className="section-title">Select</h2>
        <div className="inputs-grid">
          <div>
            <Select
              label="Game Type"
              options={gameOptions}
              value={selectedGame}
              onChange={setSelectedGame}
              placeholder="Select a game..."
            />
            <Select
              label="With Helper Text"
              options={gameOptions}
              placeholder="Choose game type..."
              helperText="Select the primary game type for this event."
            />
            <Select
              label="Error State"
              options={gameOptions}
              placeholder="Select an option..."
              error="Please select a game type"
              required
            />
          </div>
          <div>
            <Select
              label="Searchable Select"
              options={gameOptions}
              placeholder="Search games..."
              searchable
              helperText="Type to search through options."
            />
            <Select
              label="Disabled Select"
              options={gameOptions}
              value="football"
              disabled
              helperText="This field is disabled."
            />
          </div>
        </div>
      </section>

      {/* Checkbox & Radio Section */}
      <section className="showcase-section">
        <h2 className="section-title">Checkbox & Radio</h2>
        <div className="inputs-grid">
          <Card>
            <Card.Header>
              <Card.Title>Checkboxes</Card.Title>
            </Card.Header>
            <Card.Body>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <Checkbox
                  label="Enable notifications"
                  checked={checkboxChecked}
                  onChange={setCheckboxChecked}
                />
                <Checkbox
                  label="Accept terms and conditions"
                  required
                />
                <Checkbox
                  label="Indeterminate state"
                  checked={checkboxIndeterminate}
                  indeterminate={checkboxIndeterminate}
                  onChange={() => setCheckboxIndeterminate(!checkboxIndeterminate)}
                  helperText="Click to toggle through states"
                />
                <Checkbox
                  label="Disabled checkbox"
                  disabled
                  checked={true}
                />
                <Checkbox
                  label="Error state"
                  error="This field is required"
                  required
                />
              </div>
            </Card.Body>
          </Card>

          <Card>
            <Card.Header>
              <Card.Title>Radio Buttons</Card.Title>
            </Card.Header>
            <Card.Body>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <p style={{ color: 'var(--text-secondary, #94A3B8)', marginBottom: '8px' }}>
                  Select your favorite game:
                </p>
                {radioOptions.map((option) => (
                  <Radio
                    key={option.value}
                    label={option.label}
                    name="game"
                    value={option.value}
                    checked={selectedRadio === option.value}
                    onChange={(value) => setSelectedRadio(value)}
                  />
                ))}
                <div style={{ marginTop: '16px' }}>
                  <Radio
                    label="Disabled option"
                    name="game"
                    value="tennis"
                    disabled
                  />
                </div>
              </div>
            </Card.Body>
          </Card>
        </div>
      </section>

      {/* Switch Section */}
      <section className="showcase-section">
        <h2 className="section-title">Switch</h2>
        <Card>
          <Card.Body>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <Switch
                label="Enable Notifications"
                checked={switchEnabled}
                onChange={setSwitchEnabled}
              />
              <Switch
                label="Auto-save"
                description="Automatically save changes every 30 seconds"
                checked={switchAutoSave}
                onChange={setSwitchAutoSave}
              />
              <Switch
                label="Dark Mode"
                description="Enable dark theme for the application"
                checked={true}
              />
              <Switch
                label="Disabled Switch"
                description="This switch is disabled"
                disabled
                checked={false}
              />
              <Switch
                label="Required Setting"
                required
                checked={true}
              />
            </div>
          </Card.Body>
        </Card>
      </section>

      {/* Spinner Section */}
      <section className="showcase-section">
        <h2 className="section-title">Spinner</h2>
        <Card>
          <Card.Body>
            <p style={{ marginBottom: '24px', color: 'var(--text-secondary, #94A3B8)' }}>
              Loading indicators in different sizes:
            </p>
            <div style={{ display: 'flex', alignItems: 'center', gap: '48px', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                <Spinner size="sm" />
                <span style={{ fontSize: '14px', color: 'var(--text-secondary, #94A3B8)' }}>Small</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                <Spinner size="md" />
                <span style={{ fontSize: '14px', color: 'var(--text-secondary, #94A3B8)' }}>Medium</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                <Spinner size="lg" />
                <span style={{ fontSize: '14px', color: 'var(--text-secondary, #94A3B8)' }}>Large</span>
              </div>
            </div>
            <div style={{ marginTop: '32px' }}>
              <Spinner size="md" label="Loading data..." />
            </div>
          </Card.Body>
        </Card>
      </section>

      {/* Interactive Example */}
      <section className="showcase-section">
        <h2 className="section-title">Interactive Example</h2>
        <Card>
          <Card.Header>
            <Card.Title>Generate HQL</Card.Title>
          </Card.Header>
          <Card.Body>
            <div style={{ marginBottom: '16px' }}>
              <Input
                label="Game Name"
                placeholder="Enter game name..."
              />
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <Button variant="primary" onClick={handleClick} loading={isloading}>
                {isloading ? 'Generating...' : 'Generate'}
              </Button>
              <Button variant="ghost">Cancel</Button>
            </div>
          </Card.Body>
        </Card>
      </section>

      {/* Animation Demo */}
      <section className="showcase-section">
        <h2 className="section-title">Animations</h2>
        <Button onClick={() => window.location.reload()}>
          Reload Page to See Entrance Animations
        </Button>
        <p className="text-sm text-gray-400" style={{ marginTop: '8px' }}>
          Cards will animate in with staggered delay.
        </p>
      </section>
    </div>
  );
}

// Wrap with ToastProvider
function ComponentShowcase() {
  return (
    <ToastProvider>
      <ComponentShowcaseContent />
    </ToastProvider>
  );
}

export default ComponentShowcase;
