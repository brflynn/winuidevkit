/**
 * WinUIDevKit Node.js binder — maps XAML x:Name elements to JS objects
 * and wires event handlers using the "elementName.EventName" convention.
 */

export interface BindingMap {
  [elementName: string]: any;
}

/**
 * Extract all x:Name attributes from XAML content.
 */
export function extractNames(xamlContent: string): string[] {
  const regex = /x:Name="([^"]+)"/g;
  const names: string[] = [];
  let match: RegExpExecArray | null;
  while ((match = regex.exec(xamlContent)) !== null) {
    names.push(match[1]);
  }
  return names;
}

/**
 * Build a binding map from named elements.
 */
export function buildBindings(
  names: string[],
  findFn: (name: string) => any
): BindingMap {
  const bindings: BindingMap = {};
  for (const name of names) {
    try {
      bindings[name] = findFn(name);
    } catch {
      // Element not found — skip
    }
  }
  return bindings;
}

/**
 * Wire event handlers from a handler map.
 * Keys are "elementName.EventName", values are callback functions.
 */
export function wireEvents(
  bindings: BindingMap,
  handlers: Map<string, Function>
): void {
  for (const [key, handler] of handlers) {
    const dotIndex = key.indexOf(".");
    if (dotIndex < 0) continue;

    const elementName = key.substring(0, dotIndex);
    const eventName = key.substring(dotIndex + 1);
    const element = bindings[elementName];

    if (element) {
      // Native event subscription would go through the N-API addon
      // element.addEventListener(eventName, handler);
    }
  }
}
