//! XAML Loader — parse XAML strings via XamlReader::Load().

use windows::core::{Result, HSTRING};
use crate::bindings::Microsoft::UI::Xaml::Markup::XamlReader;
use crate::bindings::Microsoft::UI::Xaml::UIElement;

/// Load a XAML string and return the root UIElement.
pub fn load_xaml(xaml: &str) -> Result<UIElement> {
    let hstring = HSTRING::from(xaml);
    let obj = XamlReader::Load(&hstring)?;
    obj.cast::<UIElement>()
}

/// Read a XAML file from disk, strip the `<Window>` wrapper if present,
/// and return (title, content_element).
pub fn load_xaml_file(path: &std::path::Path) -> Result<(Option<String>, UIElement)> {
    let xaml_string = std::fs::read_to_string(path)
        .map_err(|e| windows::core::Error::new(
            windows::core::HRESULT(-1),
            HSTRING::from(format!("Failed to read XAML: {e}"))
        ))?;

    let (title, content_xaml) = extract_window_content(&xaml_string);
    let element = load_xaml(&content_xaml)?;
    Ok((title, element))
}

/// If the root is `<Window>`, extract the title and inner content XAML.
/// Otherwise return the XAML unchanged.
fn extract_window_content(xaml: &str) -> (Option<String>, String) {
    // Simple heuristic: check if it starts with <Window
    let trimmed = xaml.trim();
    if !trimmed.starts_with("<Window") {
        return (None, xaml.to_string());
    }

    // Extract Title attribute
    let title = extract_attribute(trimmed, "Title");

    // Extract inner content between first > and last </Window>
    if let Some(start) = trimmed.find('>') {
        if let Some(end) = trimmed.rfind("</Window>") {
            let inner = trimmed[start + 1..end].trim();
            if !inner.is_empty() {
                // Re-inject xmlns declarations from the outer Window
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
    // Find the end of the first tag name
    if let Some(first_space_or_gt) = inner_xml.find(|c: char| c == ' ' || c == '>' || c == '/') {
        let tag_end = &inner_xml[..first_space_or_gt];
        let rest = &inner_xml[first_space_or_gt..];
        let ns_str = namespaces.join(" ");
        format!("{} {} {}", tag_end, ns_str, rest.trim_start())
    } else {
        inner_xml.to_string()
    }
}
