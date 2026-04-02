/// WinUIDevKit Swift Bootstrap — initializes WinAppSDK via DDLM.
///
/// Uses swift-winrt projections (no custom bridge code).

import WinRT
import WinAppSDK  // swift-winrt generated projection

/// Major.Minor packed as UInt32: 1.8 → 0x0001_0008
private let sdkVersionTag: UInt32 = 0x0001_0008

/// Initialize the Windows App SDK Dynamic Dependency Lifetime Manager.
/// Must be called before any WinUI3 APIs.
public func initializeBootstrap() throws {
    let hr = MddBootstrapInitialize2(
        majorMinorVersion: sdkVersionTag,
        versionTag: nil,
        minVersion: .init(),
        options: .none
    )
    guard hr >= 0 else {
        throw WinUIError.bootstrapFailed(hresult: hr)
    }
}

/// Shut down the Dynamic Dependency Lifetime Manager.
public func shutdownBootstrap() {
    MddBootstrapShutdown()
}

public enum WinUIError: Error {
    case bootstrapFailed(hresult: Int32)
    case xamlLoadFailed(String)
    case elementNotFound(String)
}
