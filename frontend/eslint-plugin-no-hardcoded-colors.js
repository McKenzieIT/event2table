export const noHardcodedColors = {
  meta: {
    type: 'suggestion',
    docs: {
      description: 'Warn about hardcoded color values in JSX',
      category: 'Best Practices',
      recommended: false,
    },
    messages: {
      hardcodedColor: 'Hardcoded color "{{color}}" found. Use CSS variable instead (e.g., var(--color-primary), var(--en-field-base), var(--en-field-param)).',
    },
  },
  create(context) {
    const forbiddenColors = [
      '#3B82F6', '#06B6D4', '#1D4ED8', '#2563EB',
      '#22D3EE', '#0891B2', '#60A5FA', '#1E293B',
    ];
    
    return {
      JSXAttribute(node) {
        if (!node.value) return;
        
        if (node.value.type === 'Literal' && typeof node.value.value === 'string') {
          const value = node.value.value;
          for (const color of forbiddenColors) {
            if (value.includes(color)) {
              context.report({
                node: node.value,
                messageId: 'hardcodedColor',
                data: { color },
              });
            }
          }
        }
      },
    };
  },
};

export const plugin = {
  rules: {
    'no-hardcoded-colors': noHardcodedColors,
  },
};
