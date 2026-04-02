/// WinUIDevKit CLI entry point for Swift.

import Foundation
import WinUIDevKit

let args = CommandLine.arguments

guard args.count >= 2 else {
    print("Usage: winui <init|run> [options]")
    exit(1)
}

switch args[1] {
case "init":
    guard args.count >= 3 else {
        print("Usage: winui init <project-name>")
        exit(1)
    }
    let name = args[2]
    let fm = FileManager.default

    // Create project directory
    let projectDir = fm.currentDirectoryPath + "/" + name
    try fm.createDirectory(atPath: projectDir + "/app", withIntermediateDirectories: true)

    // Write MainWindow.xaml
    let xaml = """
    <Window
      xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
      xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
      Title="\(name)">
      <StackPanel HorizontalAlignment="Center" VerticalAlignment="Center">
        <TextBlock x:Name="greeting" Text="Hello from WinUI3 + Swift!" FontSize="24"/>
        <Button x:Name="myButton" Content="Click me"/>
      </StackPanel>
    </Window>
    """
    try xaml.write(toFile: projectDir + "/app/MainWindow.xaml", atomically: true, encoding: .utf8)

    // Write main.swift
    let mainSwift = """
    import WinUIDevKit

    try initializeBootstrap()

    let xaml = try String(contentsOfFile: "app/MainWindow.xaml", encoding: .utf8)
    let content = try loadXaml(xaml)
    let window = try createWindow(content: content)

    // Find named elements
    let bindings = buildBindings(root: content, xaml: xaml)
    print("Found elements: \\(bindings.keys)")

    shutdownBootstrap()
    """
    try mainSwift.write(toFile: projectDir + "/app/main.swift", atomically: true, encoding: .utf8)

    print("Created \(name)/ — open in Swift for Windows and build")

case "run":
    print("Running Swift WinUI app...")
    let process = Process()
    process.executableURL = URL(fileURLWithPath: "/usr/bin/swift")
    process.arguments = ["run"]
    try process.run()
    process.waitUntilExit()

default:
    print("Unknown command: \(args[1])")
    print("Usage: winui <init|run>")
    exit(1)
}
