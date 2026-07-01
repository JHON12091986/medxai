/**
 * Checks if a value is a function.
 * @param value - The value to check.
 * @returns True if the value is a function, false otherwise.
 */
export function isFunction(value: unknown): value is (...args: unknown[]) => unknown {
  return typeof value === 'function';
}