//! WinUIDevKit Rust language pack — bootstrap, XAML loading, and binder.
//!
//! Uses raw FFI for Windows App SDK (WinUI 3) types that are not in the
//! `windows` crate. The bootstrap is a plain C export from the DDLM DLL;
//! XAML loading and element lookup use WinRT activation + COM vtables.

pub mod bootstrap;
pub mod binder;
pub mod xaml_loader;
