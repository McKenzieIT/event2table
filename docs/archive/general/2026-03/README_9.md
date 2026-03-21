# Event2Table Component Library

## Overview

The Event2Table Component Library provides a set of reusable, accessible, and performant UI components built on React. These components are designed to maintain consistency across the application while providing flexibility for various use cases.

## Design Principles

- **Consistency**: Uniform design language and behavior across all components
- **Accessibility**: WCAG 2.1 AA compliant with keyboard navigation and screen reader support
- **Performance**: Optimized for rendering performance and bundle size
- **Flexibility**: Highly customizable through props and composition
- **Type Safety**: Full TypeScript support with comprehensive type definitions

## Component Categories

### Core Components

#### Modal
Dialog components for displaying content in an overlay.

**Features:**
- Multiple sizes (small, medium, large, full-screen)
- Keyboard navigation (ESC to close)
- Backdrop click handling
- Customizable header and footer
- Animation support

**Usage:**
```tsx
import { Modal } from '@ui-components/Modal';
```

#### Form
Form components with built-in validation and state management.

**Features:**
- Field-level validation
- Form-level validation
- Error handling
- Accessibility support
- Integration with react-hook-form

**Usage:**
```tsx
import { Form } from '@ui-components/Form';
```

#### Table
Data table components with sorting, filtering, and pagination.

**Features:**
- Column sorting
- Row selection
- Pagination
- Filtering
- Responsive design
- Virtual scrolling for large datasets

**Usage:**
```tsx
import { Table } from '@ui-components/Table';
```

## Hooks

### useModal
Hook for managing modal state and behavior.

### useForm
Hook for form state management and validation.

### useTable
Hook for table state management (sorting, filtering, pagination).

## Utilities

### Validation
Form validation utilities and schemas.

### Format
Data formatting utilities (dates, numbers, strings).

### Constants
Shared constants and configuration values.

## Installation

Components are available through path aliases:

```tsx
// Components
import { Modal } from '@ui-components/Modal';
import { Form } from '@ui-components/Form';
import { Table } from '@ui-components/Table';

// Hooks
import { useModal } from '@ui-hooks/useModal';
import { useForm } from '@ui-hooks/useForm';
import { useTable } from '@ui-hooks/useTable';

// Utilities
import { validation } from '@ui-utils/validation';
import { format } from '@ui-utils/format';
import { constants } from '@ui-utils/constants';

// Types
import type { ModalProps } from '@ui-types';
```

## Contributing

When adding new components:

1. Follow the established directory structure
2. Include TypeScript types
3. Add accessibility attributes
4. Write comprehensive documentation
5. Follow the existing code style

## Roadmap

- [ ] Additional components (Button, Input, Select, etc.)
- [ ] Theming system
- [ ] Component testing utilities
- [ ] Storybook integration
- [ ] Performance monitoring
