//! Build script — generate WinAppSDK (WinUI 3) bindings from `.winmd` metadata.
//!
//! The `windows` crate only ships Windows SDK types.  Microsoft.UI.Xaml and other
//! Windows App SDK types must be generated from the WinAppSDK `.winmd` files using
//! `windows-bindgen`.
//!
//! Before building, download the metadata:
//!   pwsh -File scripts/download-metadata.ps1   (or see CI workflow)

fn main() {
    let metadata_dir = std::path::Path::new("metadata");

    if !metadata_dir.exists() || metadata_dir.read_dir().map_or(true, |mut d| d.next().is_none())
    {
        panic!(
            "WinAppSDK metadata not found.\n\
             Run `scripts/download-metadata.ps1` (or the CI step) to download \
             the .winmd files into src/rust/metadata/ before building."
        );
    }

    let out_dir = std::env::var("OUT_DIR").expect("OUT_DIR not set");
    let output = std::path::PathBuf::from(&out_dir).join("bindings.rs");

    let result = windows_bindgen::bindgen([
        "--in",
        metadata_dir.to_str().unwrap(),
        "--out",
        output.to_str().unwrap(),
        "--filter",
        "Microsoft.UI.Xaml",
        "--filter",
        "Microsoft.UI.Xaml.Controls",
        "--filter",
        "Microsoft.UI.Xaml.Markup",
        "--filter",
        "Microsoft.UI.Xaml.Input",
        "--filter",
        "Microsoft.Windows.ApplicationModel.DynamicDependency",
    ]);

    match result {
        Ok(msg) => {
            if !msg.is_empty() {
                println!("cargo:warning={msg}");
            }
        }
        Err(e) => panic!("Failed to generate WinAppSDK bindings: {e}"),
    }

    println!("cargo:rerun-if-changed=metadata");
}
