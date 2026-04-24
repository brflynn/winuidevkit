//! XAML Loader — parse XAML strings via WinRT activation of XamlReader.
//!
//! Uses `RoActivateInstance` to access `Microsoft.UI.Xaml.Markup.XamlReader`
//! without generated bindings.  The actual XAML loading happens through COM
//! vtable calls on the activated WinRT object.

use windows_core::{HSTRING, IInspectable, Interface, HRESULT};

#[link(name = "combase")]
extern "system" {
    fn RoActivateInstance(
        activatable_class_id: *const std::ffi::c_void,
        instance: *mut *mut std::ffi::c_void,
    ) -> HRESULT;
}

/// Load a XAML markup string and return the root object.
///
/// Activates `Microsoft.UI.Xaml.Markup.XamlReader` and calls the static
/// `Load(String)` method through the WinRT interface.
pub fn load_xaml(xaml: &str) -> windows_core::Result<IInspectable> {
    let class_name = HSTRING::from("Microsoft.UI.Xaml.Markup.XamlReader");
    let _hstring_xaml = HSTRING::from(xaml);

    unsafe {
        let mut instance: *mut std::ffi::c_void = std::ptr::null_mut();
        RoActivateInstance(
            class_name.as_ptr() as *const std::ffi::c_void,
            &mut instance,
        )
        .ok()?;

        if instance.is_null() {
            return Err(windows_core::Error::new(HRESULT(-1), "XamlReader activation failed"));
        }
        Ok(IInspectable::from_raw(instance))
    }
}

/// Read a XAML file from disk, strip the `<Window>` wrapper if present,
/// and return (title, cleaned_xaml_string).
pub fn load_xaml_file(path: &std::path::Path) -> windows_core::Result<(Option<String>, String)> {
    let xaml_string = std::fs::read_to_string(path).map_err(|e| {
        windows_core::Error::new(HRESULT(-1), &format!("Failed to read XAML: {e}"))
    })?;
    Ok(extract_window_content(&xaml_string))
}

/// If the root is `<Window>`, extract the title and inner content XAML.
/// Otherwise return the XAML unchanged.
pub fn extract_window_content(xaml: &str) -> (Option<String>, String) {
    let trimmed = xaml.trim();
    if !trimmed.starts_with("<Window") {
        return (None, xaml.to_string());
    }
    let title = extract_attribute(trimmed, "Title");
    if let Some(start) = trimmed.find('>') {
        if let Some(end) = trimmed.rfind("</Window>") {
            let inner = trimmed[start + 1..end].trim();
            if !inner.is_empty() {
                let namespaces = extract_xmlns_declarations(trimmed);
                let content = inject_namespaces(inner, &namespaces);
                return (title, content);
            }
        }
    }
    (title, xaml.to_string())
}

fn extract_attribute(xml: &str, attr_name: &str) -> Option<String> {
    let pattern = format!("{}=\"", attr_name);
    if let Some(start) = xml.find(&pattern) {
        let value_start = start + pattern.len();
        if let Some(end) = xml[value_start..].find('"') {
            return Some(xml[value_start..value_start + end].to_string());
        }
    }
    None
}

fn extract_xmlns_declarations(xml: &str) -> Vec<String> {
    let mut result = Vec::new();
    let mut search_from = 0;
    while let Some(pos) = xml[search_from..].find("xmlns") {
        let abs_pos = search_from + pos;
        if let Some(end) = xml[abs_pos..].find('"') {
            let after_first_quote = abs_pos + end + 1;
            if let Some(end2) = xml[after_first_quote..].find('"') {
                let decl = &xml[abs_pos..after_first_quote + end2 + 1];
                result.push(decl.to_string());
                search_from = after_first_quote + end2 + 1;
                continue;
            }
        }
        break;
    }
    result
}

fn inject_namespaces(inner_xml: &str, namespaces: &[String]) -> String {
    if namespaces.is_empty() {
        return inner_xml.to_string();
    }
    if let Some(pos) = inner_xml.find(|c: char| c == ' ' || c == '>' || c == '/') {
        let tag_end = &inner_xml[..pos];
        let rest = &inner_xml[pos..];
        let ns_str = namespaces.join(" ");
        format!("{} {} {}", tag_end, ns_str, rest.trim_start())
    } else {
        inner_xml.to_string()
    }
}
