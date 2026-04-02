/// Swift HelloWorld — uses swift-winrt bridge via WinUIDevKit.

import WinUIDevKit

do {
    // Initialize WinAppSDK
    try initializeBootstrap()

    // Load XAML
    let xaml = try String(contentsOfFile: "app/MainWindow.xaml", encoding: .utf8)
    let content = try loadXaml(xaml)

    // Create window
    let window = try createWindow(content: content)

    // Build element bindings
    let bindings = buildBindings(root: content, xaml: xaml)
    print("Found elements: \(bindings.keys.sorted())")

    // In full implementation: wire click handler to clickButton
    // bindings["clickButton"].Click += { sender, args in
    //     clickCount += 1
    //     bindings["counter"].Text = "Clicks: \(clickCount)"
    // }

    shutdownBootstrap()
} catch {
    print("Error: \(error)")
}
