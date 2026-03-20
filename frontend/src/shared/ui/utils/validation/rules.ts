import { z } from 'zod';

/**
 * Validation Rules Module
 * 
 * Provides reusable validation rules and schemas for form validation.
 * Built on top of Zod for type-safe and composable validation.
 * 
 * DESIGN PRINCIPLES:
 * - Composable: Rules can be combined and extended
 * - Type-safe: Full TypeScript support with inferred types
 * - Flexible: Easy to customize and extend
 * - Performant: Zod's efficient validation engine
 * 
 * @example
 * ```tsx
 * import { validationRules } from '@/shared/ui/utils/validation/rules';
 * 
 * const schema = z.object({
 *   email: validationRules.email,
 *   password: validationRules.password,
 *   age: validationRules.age.min(18),
 * });
 * ```
 */

/**
 * Common validation rules
 */
export const validationRules = {
  /**
   * Email validation rule
   * Validates standard email format
   */
  email: z
    .string({
      required_error: 'Email is required',
      invalid_type_error: 'Email must be a string',
    })
    .min(1, 'Email is required')
    .email('Invalid email format'),

  /**
   * Password validation rule
   * Requires at least 8 characters
   */
  password: z
    .string({
      required_error: 'Password is required',
      invalid_type_error: 'Password must be a string',
    })
    .min(8, 'Password must be at least 8 characters'),

  /**
   * Strong password validation rule
   * Requires:
   * - At least 8 characters
   * - At least 1 uppercase letter
   * - At least 1 lowercase letter
   * - At least 1 number
   * - At least 1 special character
   */
  strongPassword: z
    .string({
      required_error: 'Password is required',
      invalid_type_error: 'Password must be a string',
    })
    .min(8, 'Password must be at least 8 characters')
    .regex(
      /[A-Z]/,
      'Password must contain at least 1 uppercase letter'
    )
    .regex(
      /[a-z]/,
      'Password must contain at least 1 lowercase letter'
    )
    .regex(
      /[0-9]/,
      'Password must contain at least 1 number'
    )
    .regex(
      /[^A-Za-z0-9]/,
      'Password must contain at least 1 special character'
    ),

  /**
   * Name validation rule
   * Allows letters, spaces, hyphens, and apostrophes
   */
  name: z
    .string({
      required_error: 'Name is required',
      invalid_type_error: 'Name must be a string',
    })
    .min(1, 'Name is required')
    .max(100, 'Name must be less than 100 characters')
    .regex(
      /^[a-zA-Z\s'-]+$/,
      'Name can only contain letters, spaces, hyphens, and apostrophes'
    ),

  /**
   * Username validation rule
   * Alphanumeric with underscores and hyphens
   */
  username: z
    .string({
      required_error: 'Username is required',
      invalid_type_error: 'Username must be a string',
    })
    .min(3, 'Username must be at least 3 characters')
    .max(30, 'Username must be less than 30 characters')
    .regex(
      /^[a-zA-Z0-9_-]+$/,
      'Username can only contain letters, numbers, underscores, and hyphens'
    ),

  /**
   * Phone number validation rule
   * Supports various phone formats
   */
  phone: z
    .string({
      required_error: 'Phone number is required',
      invalid_type_error: 'Phone number must be a string',
    })
    .min(10, 'Phone number must be at least 10 digits')
    .regex(
      /^[+]?[(]?[0-9]{1,4}[)]?[-\s.]?[(]?[0-9]{1,4}[)]?[-\s.]?[0-9]{1,9}$/,
      'Invalid phone number format'
    ),

  /**
   * URL validation rule
   * Validates standard URL format
   */
  url: z
    .string({
      required_error: 'URL is required',
      invalid_type_error: 'URL must be a string',
    })
    .min(1, 'URL is required')
    .url('Invalid URL format'),

  /**
   * Age validation rule
   * Must be a positive integer between 0 and 150
   */
  age: z
    .number({
      required_error: 'Age is required',
      invalid_type_error: 'Age must be a number',
    })
    .int('Age must be an integer')
    .min(0, 'Age must be at least 0')
    .max(150, 'Age must be less than 150'),

  /**
   * Date validation rule
   * Validates date string format
   */
  date: z
    .string({
      required_error: 'Date is required',
      invalid_type_error: 'Date must be a string',
    })
    .min(1, 'Date is required')
    .datetime('Invalid date format'),

  /**
   * Required string validation rule
   * Non-empty string
   */
  requiredString: z
    .string({
      required_error: 'This field is required',
      invalid_type_error: 'This field must be a string',
    })
    .min(1, 'This field is required'),

  /**
   * Required number validation rule
   */
  requiredNumber: z
    .number({
      required_error: 'This field is required',
      invalid_type_error: 'This field must be a number',
    })
    .min(0, 'This field is required'),

  /**
   * Required boolean validation rule
   */
  requiredBoolean: z
    .boolean({
      required_error: 'This field is required',
      invalid_type_error: 'This field must be a boolean',
    }),

  /**
   * Optional string validation rule
   * Can be empty or undefined
   */
  optionalString: z
    .string()
    .optional()
    .nullable(),

  /**
   * Optional number validation rule
   */
  optionalNumber: z
    .number()
    .optional()
    .nullable(),

  /**
   * Array validation rule
   * Validates array of strings
   */
  stringArray: z
    .array(z.string())
    .min(1, 'At least one item is required'),

  /**
   * Enum validation rule
   * Validates against allowed values
   */
  enum: <T extends readonly [string, ...string[]]>(values: T) =>
    z.enum(values, {
      required_error: 'This field is required',
      invalid_type_error: 'Invalid value',
    }),
} as const;

/**
 * Common form schemas
 * Pre-built schemas for common use cases
 */
export const formSchemas = {
  /**
   * Login form schema
   */
  login: z.object({
    email: validationRules.email,
    password: validationRules.password,
  }),

  /**
   * Registration form schema
   */
  registration: z.object({
    username: validationRules.username,
    email: validationRules.email,
    password: validationRules.strongPassword,
    confirmPassword: z.string(),
  }).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  }),

  /**
   * Profile form schema
   */
  profile: z.object({
    name: validationRules.name,
    email: validationRules.email,
    phone: validationRules.phone.optional(),
    age: validationRules.age.optional(),
  }),

  /**
   * Contact form schema
   */
  contact: z.object({
    name: validationRules.name,
    email: validationRules.email,
    subject: validationRules.requiredString.min(5, 'Subject must be at least 5 characters'),
    message: validationRules.requiredString.min(10, 'Message must be at least 10 characters'),
  }),
} as const;

/**
 * Type inference helpers
 * Extract types from schemas
 */
export type LoginFormValues = z.infer<typeof formSchemas.login>;
export type RegistrationFormValues = z.infer<typeof formSchemas.registration>;
export type ProfileFormValues = z.infer<typeof formSchemas.profile>;
export type ContactFormValues = z.infer<typeof formSchemas.contact>;

/**
 * Utility functions for validation
 */
export const validationUtils = {
  /**
   * Create a custom validation rule
   */
  createRule: <T>(
    schema: z.ZodType<T>,
    errorMessage?: string
  ) => schema,

  /**
   * Combine multiple rules
   */
  combineRules: <T>(
    ...rules: z.ZodType<T>[]
  ) => {
    return rules.reduce(
      (acc, rule) => acc.and(rule),
      rules[0]
    );
  },

  /**
   * Make a rule optional
   */
  makeOptional: <T>(rule: z.ZodType<T>) =>
    rule.optional().nullable(),

  /**
   * Add custom error message
   */
  withError: <T>(
    rule: z.ZodType<T>,
    message: string
  ) => rule,
} as const;
