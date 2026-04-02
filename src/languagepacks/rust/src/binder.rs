//! Binder — map x:Name elements to a NamedElements struct.
//!
//! Provides `find_named_element()` to look up XAML elements by x:Name,
//! and a macro to generate typed binder structs.

use windows::core::{Result, HSTRING};
use windows::Microsoft::UI::Xaml::{DependencyObject, FrameworkElement};

/// Find a named element within a XAML tree by its x:Name.
pub fn find_named_element(root: &FrameworkElement, name: &str) -> Result<Option<DependencyObject>> {
    let hname = HSTRING::from(name);
    match root.FindName(&hname) {
        Ok(obj) => Ok(Some(obj)),
        Err(_) => Ok(None),
    }
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
///         title_text: TextBlock,
///         hello_button: Button,
///     }
/// }
///
/// // Then bind it:
/// let view = MainView::bind(&root_element)?;
/// view.hello_button.SetContent("Clicked!")?;
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
            pub fn bind(root: &::windows::Microsoft::UI::Xaml::FrameworkElement) -> ::windows::core::Result<Self> {
                Ok(Self {
                    $($field: {
                        let name = stringify!($field);
                        // Convert snake_case to camelCase for x:Name lookup
                        let xaml_name = $crate::binder::snake_to_camel(name);
                        let obj = $crate::binder::find_named_element(root, &xaml_name)?
                            .ok_or_else(|| ::windows::core::Error::new(
                                ::windows::core::HRESULT(-1),
                                ::windows::core::HSTRING::from(format!("x:Name '{}' not found", xaml_name)),
                            ))?;
                        obj.cast::<$ty>()?
                    },)*
                })
            }
        }
    };
}

/// Convert snake_case to camelCase (e.g. `hello_button` → `helloButton`).
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
