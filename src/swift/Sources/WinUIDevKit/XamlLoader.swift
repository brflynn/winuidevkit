/// WinUIDevKit Swift XAML Loader — parses XAML markup into WinUI3 element trees.
///
/// Uses swift-winrt projections for XamlReader and Window.

import WinRT
import WinUI  // swift-winrt generated projection for Microsoft.UI.Xaml

/// Load XAML markup string into a UIElement tree.
/// - Parameter xaml: Raw XAML string with WinUI3 namespace.
/// - Returns: The parsed UIElement.
public func loadXaml(_ xaml: String) throws -> Any {
    // Inject WinUI3 default namespace if not present
    var content = xaml
    if !content.contains("http://schemas.microsoft.com/winfx/2006/xaml/presentation") {
        content = content.replacingOccurrences(
            of: "<Window",
            with: "<Window xmlns=\"http://schemas.microsoft.com/winfx/2006/xaml/presentation\""
        )
    }

    guard let element = try Microsoft.UI.Xaml.Markup.XamlReader.load(content) else {
        throw WinUIError.xamlLoadFailed("XamlReader.Load returned nil")
    }
    return element
}

/// Load XAML from a file path.
/// - Parameter path: Absolute or relative file path to a .xaml file.
/// - Returns: The parsed UIElement.
public func loadXamlFile(_ path: String) throws -> Any {
    let content = try String(contentsOfFile: path, encoding: .utf8)
    return try loadXaml(content)
}

/// Create and activate a Window with the given content.
/// - Parameter content: A UIElement to set as the window's Content.
/// - Returns: The Window instance.
public func createWindow(content: Any) throws -> Microsoft.UI.Xaml.Window {
    let window = Microsoft.UI.Xaml.Window()
    if let uiElement = content as? Microsoft.UI.Xaml.UIElement {
        window.content = uiElement
    }
    try window.activate()
    return window
}
