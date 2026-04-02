//! WinUIDevKit Rust language pack — bootstrap, XAML loading, and binder.
//!
//! Uses the `windows` crate (microsoft/windows-rs) for all WinRT/COM access.
//! No custom bridge code — just the app lifecycle layer on top.

pub mod bootstrap;
pub mod binder;
pub mod xaml_loader;
