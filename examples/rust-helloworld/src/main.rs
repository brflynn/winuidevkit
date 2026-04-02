//! Rust HelloWorld — uses windows-rs (Microsoft's WinRT crate).

use std::sync::atomic::{AtomicU32, Ordering};
use winuidevkit::{bootstrap, xaml_loader, binder};

static CLICK_COUNT: AtomicU32 = AtomicU32::new(0);

fn main() -> windows::core::Result<()> {
    // Initialize WinAppSDK
    bootstrap::initialize()?;

    // Load XAML
    let xaml = std::fs::read_to_string("app/MainWindow.xaml")
        .expect("Failed to read MainWindow.xaml");
    let content = xaml_loader::load_xaml(&xaml)?;

    // Create and show window
    let window = xaml_loader::extract_window_content(&content)?;

    // Find named elements
    let greeting = binder::find_named_element(&content, "greeting")?;
    let counter = binder::find_named_element(&content, "counter")?;
    let button = binder::find_named_element(&content, "clickButton")?;

    // Wire click handler
    // button.Click(TypedEventHandler::new(move |_, _| {
    //     let count = CLICK_COUNT.fetch_add(1, Ordering::SeqCst) + 1;
    //     counter.as_ref().SetText(&format!("Clicks: {count}").into())?;
    //     Ok(())
    // }))?;

    println!("Found elements: greeting, counter, clickButton");

    bootstrap::shutdown();
    Ok(())
}
