//! Bootstrap — initialize Windows App Runtime via DDLM.
//!
//! Calls `MddBootstrapInitialize` from the windows crate.
//! This is the Rust equivalent of the Python `ensure_windows_app_runtime()`.

use windows::core::Result;
use windows::Microsoft::Windows::ApplicationModel::DynamicDependency::Bootstrap;

const SDK_VERSION_MAJOR_MINOR: u32 = 0x00010008; // 1.8

/// Initialize the Windows App Runtime bootstrap.
/// Must be called before any WinUI3 types are used.
pub fn initialize() -> Result<()> {
    unsafe {
        Bootstrap::Initialize(SDK_VERSION_MAJOR_MINOR)?;
    }
    Ok(())
}

/// Shutdown the bootstrap (call on app exit).
pub fn shutdown() {
    unsafe {
        let _ = Bootstrap::Shutdown();
    }
}
