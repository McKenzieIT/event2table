/**
 * ESLint Plugin - BaseModal Migration Rules
 *
 * Rules to ensure BaseModal is used correctly after migration
 */

const WRONG_SIZE_VALUES = ['modal-sm', 'modal-md', 'modal-lg', 'modal-xl', 'modal-fullscreen'];

const useContentClassName = {
  meta: {
    messages: {
      useContentClassName: 'Use contentClassName instead of className for BaseModal components',
      invalidSizeValue: 'BaseModal size must be one of: sm, md, lg, xl, full. Found: "{{value}}"',
      useModalBody: 'Use .modal-body instead of .cyber-modal__body for BaseModal content styling',
    },
  },
  create(context) {
    return {
      JSXElement(node) {
        if (!node.openingElement || !node.openingElement.name) return;
        
        const name = node.openingElement.name;
        if (name.type !== 'JSXIdentifier') return;
        
        const componentName = name.name;
        if (componentName !== 'BaseModal') return;

        const attributes = node.openingElement.attributes || [];
        
        for (const attr of attributes) {
          if (attr.type !== 'JSXAttribute') continue;
          
          const attrName = attr.name?.name;
          if (!attrName) continue;

          if (attrName === 'className') {
            context.report({
              node: attr,
              messageId: 'useContentClassName',
            });
          }

          if (attrName === 'size' && attr.value?.type === 'JSXExpressionContainer') {
            const value = attr.value.expression.value;
            if (typeof value === 'string' && WRONG_SIZE_VALUES.includes(value)) {
              context.report({
                node: attr,
                messageId: 'invalidSizeValue',
                data: { value },
              });
            }
          }
        }
      },

      'Literal'(node) {
        if (!node.value || typeof node.value !== 'string') return;
        
        const filename = context.filename || '';
        if (!filename.endsWith('.css') && !filename.endsWith('.scss')) return;

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

export const rules = {
  'use-content-class-name': useContentClassName,
};

export const configs = {
  recommended: {
    rules: {
      'basemodal-migration/use-content-class-name': 'error',
    },
  },
};

export default { rules, configs };
