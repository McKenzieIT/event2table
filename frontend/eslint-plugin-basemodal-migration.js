/**
 * ESLint Plugin - BaseModal Migration Rules
 *
 * Rules to ensure BaseModal is used correctly after migration
 */

const WRONG_SIZE_VALUES = ['modal-sm', 'modal-md', 'modal-lg', 'modal-xl', 'modal-fullscreen'];
const CORRECT_SIZE_VALUES = ['sm', 'md', 'lg', 'xl', 'full'];

module.exports = {
  meta: {
    name: 'eslint-plugin-basemodal-migration',
    version: '1.0.0',
    type: 'problem',
    docs: {
      description: 'BaseModal migration rules',
    },
    messages: {
      useContentClassName: 'Use contentClassName instead of className for BaseModal components',
      invalidSizeValue: 'BaseModal size must be one of: sm, md, lg, xl, full. Found: "{{value}}"',
      useModalBody: 'Use .modal-body instead of .cyber-modal__body for BaseModal content styling',
    },
  },
  create(context) {
    return {
      // Check JSXElement for BaseModal usage
      JSXElement(node) {
        if (!node.openingElement || !node.openingElement.name) return;
        
        const name = node.openingElement.name;
        if (name.type !== 'JSXIdentifier') return;
        
        // Check if this is a BaseModal component
        const componentName = name.name;
        if (componentName !== 'BaseModal') return;

        // Check attributes
        const attributes = node.openingElement.attributes || [];
        
        for (const attr of attributes) {
          if (attr.type !== 'JSXAttribute') continue;
          
          const attrName = attr.name?.name;
          if (!attrName) continue;

          // Check for className usage
          if (attrName === 'className') {
            context.report({
              node: attr,
              messageId: 'useContentClassName',
            });
          }

          // Check for invalid size values
          if (attrName === 'size' && attr.value?.type === 'JSXExpressionContainer') {
            const value = attr.value.expression.value;
            if (typeof value === 'string' && WRONG_SIZE_VALUES.includes(value)) {
              const correctValue = value.replace('modal-', '');
              context.report({
                node: attr,
                messageId: 'invalidSizeValue',
                data: { value },
              });
            }
          }
        }
      },

      // Check CSS files for old class names
      'Literal'(node) {
        if (!node.value || typeof node.value !== 'string') return;
        
        const filename = context.filename || '';
        if (!filename.endsWith('.css') && !filename.endsWith('.scss')) return;

        // Check for .cyber-modal__body
        if (node.value.includes('.cyber-modal__body')) {
          context.report({
            node,
            messageId: 'useModalBody',
          });
        }
      },
    };
  },
};
