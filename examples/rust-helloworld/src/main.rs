//! Rust HelloWorld — WinUI3 app using winuidevkit + raw FFI.

use winuidevkit::{bootstrap, xaml_loader, binder};

fn main() -> windows_core::Result<()> {
    // Initialize WinAppSDK
    bootstrap::initialize()?;

    // Load XAML file and extract window content
    let (title, content_xaml) = xaml_loader::load_xaml_file(std::path::Path::new("app/MainWindow.xaml"))?;
    println!("Window title: {:?}", title);

    // Load the XAML content into a WinRT object
    let root = xaml_loader::load_xaml(&content_xaml)?;

    // Find named elements via x:Name
    let _greeting = binder::find_named_element(&root, "greeting")?;
    let _counter = binder::find_named_element(&root, "counter")?;
    let _button = binder::find_named_element(&root, "clickButton")?;

    // Extract x:Name values from the XAML
    let names = binder::extract_xnames(&content_xaml);
    println!("Found x:Name elements: {:?}", names);

    bootstrap::shutdown();
    Ok(())
}
