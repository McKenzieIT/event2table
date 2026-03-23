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

import { ToastProvider } from '@shared/ui';
import React from 'react';

import AnimationDemo from './sections/AnimationDemo';
import BadgeShowcase from './sections/BadgeShowcase';
import ButtonShowcase from './sections/ButtonShowcase';
import CardShowcase from './sections/CardShowcase';
import CheckboxRadioShowcase from './sections/CheckboxRadioShowcase';
import InputShowcase from './sections/InputShowcase';
import InteractiveExample from './sections/InteractiveExample';
import ModalShowcase from './sections/ModalShowcase';
import SelectShowcase from './sections/SelectShowcase';
import SpinnerShowcase from './sections/SpinnerShowcase';
import SwitchShowcase from './sections/SwitchShowcase';
import TableShowcase from './sections/TableShowcase';
import TextAreaShowcase from './sections/TextAreaShowcase';
import ToastShowcase from './sections/ToastShowcase';
import './ComponentShowcase.css';

function ComponentShowcaseContent(): React.JSX.Element {
  return (
    <div className="component-showcase">
      <div className="showcase-header">
        <h1 className="showcase-title">Component Library Showcase</h1>
        <p className="showcase-subtitle">Cyberpunk Lab Theme - Interactive Preview</p>
      </div>

      <ButtonShowcase />
      <CardShowcase />
      <InputShowcase />
      <BadgeShowcase />
      <TableShowcase />
      <ModalShowcase />
      <ToastShowcase />
      <TextAreaShowcase />
      <SelectShowcase />
      <CheckboxRadioShowcase />
      <SwitchShowcase />
      <SpinnerShowcase />
      <InteractiveExample />
      <AnimationDemo />
    </div>
  );
}

// Wrap with ToastProvider
function ComponentShowcase(): React.JSX.Element {
  return (
    <ToastProvider>
      <ComponentShowcaseContent />
    </ToastProvider>
  );
}

export default ComponentShowcase;
