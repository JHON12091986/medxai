/**
 * Converts an unknown value to a string with a fallback.
 * @param value - The value to convert.
 * @param fallback - The fallback value if conversion fails (default: '').
 * @returns A string.
 */
export function toString(value: unknown, fallback: string = ''): string {
  // Si es null o undefined, devuelve el fallback
  if (value === null || value === undefined) {
    return fallback;
  }

  // Si ya es string, lo devuelve directamente
  if (typeof value === 'string') {
    return value;
  }

  // Si es número o booleano, lo convierte a string
  if (typeof value === 'number' || typeof value === 'boolean') {
    return String(value);
  }

  // Si es un objeto, intenta convertirlo a JSON
  if (typeof value === 'object') {
    try {
      return JSON.stringify(value);
    } catch {
      return fallback;
    }
  }

  // Para cualquier otro tipo (symbol, function, etc.)
  return fallback;
}