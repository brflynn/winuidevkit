//! WinUIDevKit Rust language pack — bootstrap, XAML loading, and binder.
//!
//! Uses the `windows` crate (microsoft/windows-rs) for all WinRT/COM access.
//! WinUI 3 types (Microsoft.UI.Xaml.*) are generated at build time from
//! WinAppSDK `.winmd` metadata via `windows-bindgen`.

/// Auto-generated WinAppSDK bindings (Microsoft.UI.Xaml, etc.).
#[allow(
    non_snake_case,
    non_upper_case_globals,
    non_camel_case_types,
    dead_code,
    clippy::all
)]
pub mod bindings {
    include!(concat!(env!("OUT_DIR"), "/bindings.rs"));
}

pub mod bootstrap;
pub mod binder;
pub mod xaml_loader;
