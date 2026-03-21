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

import React from 'react';
import { ToastProvider } from '@shared/ui';
import ButtonShowcase from './sections/ButtonShowcase';
import CardShowcase from './sections/CardShowcase';
import InputShowcase from './sections/InputShowcase';
import BadgeShowcase from './sections/BadgeShowcase';
import TableShowcase from './sections/TableShowcase';
import ModalShowcase from './sections/ModalShowcase';
import ToastShowcase from './sections/ToastShowcase';
import TextAreaShowcase from './sections/TextAreaShowcase';
import SelectShowcase from './sections/SelectShowcase';
import CheckboxRadioShowcase from './sections/CheckboxRadioShowcase';
import SwitchShowcase from './sections/SwitchShowcase';
import SpinnerShowcase from './sections/SpinnerShowcase';
import InteractiveExample from './sections/InteractiveExample';
import AnimationDemo from './sections/AnimationDemo';
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
