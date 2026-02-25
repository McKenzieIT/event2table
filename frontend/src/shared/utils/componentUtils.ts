export function ensureArray<T>(value: T | T[] | undefined | null, defaultValue: T[] = []): T[] {
  return Array.isArray(value) ? value : defaultValue;
}

export function safeLength(value: unknown): number {
  return Array.isArray(value) ? value.length : 0;
}

export function safeFilter<T>(
  value: T | T[] | undefined | null,
  predicate: (value: T, index: number, array: T[]) => boolean
): T[] {
  return Array.isArray(value) ? value.filter(predicate) : [];
}

export function safeMap<T, U>(
  value: T | T[] | undefined | null,
  mapper: (value: T, index: number, array: T[]) => U
): U[] {
  return Array.isArray(value) ? value.map(mapper) : [];
}

export function safeIsEmpty(value: unknown): boolean {
  return !Array.isArray(value) || value.length === 0;
}
