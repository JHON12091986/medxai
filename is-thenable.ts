/**
 * Checks if a value is thenable (has a then method).
 * @param value - The value to check.
 * @returns True if the value is thenable, false otherwise.
 */
export function isThenable(value: unknown): value is PromiseLike<unknown> {
  return typeof value === 'object' &&
    value !== null &&
    'then' in value &&
    typeof (value as { then: unknown }).then === 'function';
}