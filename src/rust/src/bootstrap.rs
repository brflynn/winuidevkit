//! Bootstrap — initialize Windows App Runtime via DDLM.
//!
//! Calls `MddBootstrapInitialize2` / `MddBootstrapShutdown` from the
//! Microsoft.WindowsAppRuntime.Bootstrap DLL.  These are plain C exports,
//! so no WinRT projection or code generation is needed.

use windows_core::{HRESULT, PCWSTR};

#[link(name = "Microsoft.WindowsAppRuntime.Bootstrap")]
extern "system" {
    fn MddBootstrapInitialize2(
        major_minor_version: u32,
        version_tag: PCWSTR,
        min_version: PackageVersion,
    ) -> HRESULT;

    fn MddBootstrapShutdown();
}

/// Mirrors the PACKAGE_VERSION struct expected by MddBootstrapInitialize2.
#[repr(C)]
#[derive(Clone, Copy)]
struct PackageVersion {
    pub revision: u16,
    pub build: u16,
    pub minor: u16,
    pub major: u16,
}

/// Initialize the Windows App Runtime bootstrap.
/// Must be called before any WinUI3 types are used.
pub fn initialize() -> windows_core::Result<()> {
    let version = PackageVersion {
        major: 1,
        minor: 8,
        build: 0,
        revision: 0,
    };
    unsafe {
        MddBootstrapInitialize2(0x00010008, PCWSTR::null(), version).ok()
    }
}

/// Shutdown the bootstrap (call on app exit).
pub fn shutdown() {
    unsafe {
        MddBootstrapShutdown();
    }
}
