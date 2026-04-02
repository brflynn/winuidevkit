/// WinUIDevKit Swift Binder — finds named elements and wires events.
///
/// Uses swift-winrt projections for FrameworkElement.FindName.

import WinRT
import WinUI  // swift-winrt generated projection for Microsoft.UI.Xaml

/// Find a named element in the XAML visual tree.
/// - Parameters:
///   - root: The root UIElement (typically Window.Content).
///   - name: The x:Name of the element to find.
/// - Returns: The found element, or nil.
public func findElement(in root: Any, named name: String) -> Any? {
    guard let frameworkElement = root as? Microsoft.UI.Xaml.FrameworkElement else {
        return nil
    }
    return frameworkElement.findName(name)
}

/// Extract all x:Name values from XAML markup.
/// - Parameter xaml: Raw XAML string.
/// - Returns: Array of element names.
public func extractNames(from xaml: String) -> [String] {
    var names: [String] = []
    // Simple regex-based extraction
    let pattern = "x:Name=\"([^\"]+)\""
    guard let regex = try? NSRegularExpression(pattern: pattern) else { return names }
    let range = NSRange(xaml.startIndex..., in: xaml)
    regex.enumerateMatches(in: xaml, range: range) { match, _, _ in
        if let match = match, let captureRange = Range(match.range(at: 1), in: xaml) {
            names.append(String(xaml[captureRange]))
        }
    }
    return names
}

/// A convenience wrapper that builds a dictionary of named elements.
/// - Parameters:
///   - root: The root UIElement.
///   - xaml: The XAML markup (used to discover x:Name attributes).
/// - Returns: Dictionary mapping element names to their WinUI objects.
public func buildBindings(root: Any, xaml: String) -> [String: Any] {
    var bindings: [String: Any] = [:]
    for name in extractNames(from: xaml) {
        if let element = findElement(in: root, named: name) {
            bindings[name] = element
        }
    }
    return bindings
}
