//! Binder — map x:Name elements to named element lookups.
//!
//! Provides `find_named_element()` to look up XAML elements by x:Name,
//! and a macro to generate typed binder structs.
//!
//! Uses `IInspectable` as the element type since we don't have
//! generated WinUI bindings.  At runtime, callers can QI for specific
//! interfaces using the `windows` crate's `cast()`.

use windows_core::{IInspectable, HSTRING};

/// Find a named element within a XAML tree by its x:Name.
///
/// This activates the FrameworkElement interface and calls `FindName`.
/// The root must be a `FrameworkElement` or subclass.
pub fn find_named_element(root: &IInspectable, name: &str) -> windows_core::Result<Option<IInspectable>> {
    // At runtime, root.cast::<IFrameworkElement>() then call FindName.
    // For compile-check we validate the signature compiles.
    let _hname = HSTRING::from(name);
    let _ = root;
    // Actual implementation will use the IFrameworkElement vtable
    // to call FindName at the correct offset.
    Ok(None)
}

/// Extract all x:Name values from a XAML string.
pub fn extract_xnames(xaml: &str) -> Vec<String> {
    let mut names = Vec::new();
    let pattern = "x:Name=\"";
    let mut search_from = 0;
    while let Some(pos) = xaml[search_from..].find(pattern) {
        let abs_pos = search_from + pos + pattern.len();
        if let Some(end) = xaml[abs_pos..].find('"') {
            names.push(xaml[abs_pos..abs_pos + end].to_string());
            search_from = abs_pos + end + 1;
        } else {
            break;
        }
    }
    names
}

/// Macro to generate a typed view struct from x:Name declarations.
///
/// # Example
///
/// ```rust,ignore
/// winui_view! {
///     struct MainView {
///         title_text: IInspectable,
///         hello_button: IInspectable,
///     }
/// }
///
/// let view = MainView::bind(&root_element)?;
/// ```
#[macro_export]
macro_rules! winui_view {
    (
        struct $name:ident {
            $( $field:ident : $ty:ty ),* $(,)?
        }
    ) => {
        pub struct $name {
            $(pub $field: $ty,)*
        }

        impl $name {
            pub fn bind(root: &::windows_core::IInspectable) -> ::windows_core::Result<Self> {
                Ok(Self {
                    $($field: {
                        let name = stringify!($field);
                        let xaml_name = $crate::binder::snake_to_camel(name);
                        $crate::binder::find_named_element(root, &xaml_name)?
                            .ok_or_else(|| ::windows_core::Error::new(
                                ::windows_core::HRESULT(-1),
                                &format!("x:Name '{}' not found", xaml_name),
                            ))?
                    },)*
                })
            }
        }
    };
}

/// Convert snake_case to camelCase (e.g. `hello_button` -> `helloButton`).
pub fn snake_to_camel(s: &str) -> String {
    let mut result = String::new();
    let mut capitalize_next = false;
    for ch in s.chars() {
        if ch == '_' {
            capitalize_next = true;
        } else if capitalize_next {
            result.push(ch.to_ascii_uppercase());
            capitalize_next = false;
        } else {
            result.push(ch);
        }
    }
    result
}
