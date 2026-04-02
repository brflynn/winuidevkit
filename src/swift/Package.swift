// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "WinUIDevKit",
    platforms: [
        .custom("windows", versionString: "10.0")
    ],
    products: [
        .library(name: "WinUIDevKit", targets: ["WinUIDevKit"]),
        .executable(name: "winui", targets: ["WinUICLI"]),
    ],
    dependencies: [
        // swift-winrt — generates WinRT projections from .winmd metadata
        .package(url: "https://github.com/thebrowsercompany/swift-winrt", from: "0.20.0"),
    ],
    targets: [
        .target(
            name: "WinUIDevKit",
            dependencies: [
                .product(name: "WinRT", package: "swift-winrt"),
            ],
            path: "Sources/WinUIDevKit"
        ),
        .executableTarget(
            name: "WinUICLI",
            dependencies: ["WinUIDevKit"],
            path: "Sources/WinUICLI"
        ),
    ]
)
