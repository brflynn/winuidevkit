// XamlLoader — load XAML strings via XamlReader::Load, exposed via N-API.

#include <napi.h>
#include <winrt/Microsoft.UI.Xaml.h>
#include <winrt/Microsoft.UI.Xaml.Markup.h>
#include <winrt/Microsoft.UI.Xaml.Controls.h>

namespace winuidevkit {

// Store the current Window handle for JS access
static winrt::Microsoft::UI::Xaml::Window g_window{ nullptr };

Napi::Value LoadXaml(const Napi::CallbackInfo& info) {
    auto env = info.Env();
    if (info.Length() < 1 || !info[0].IsString()) {
        Napi::TypeError::New(env, "Expected XAML string").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    std::string xaml = info[0].As<Napi::String>().Utf8Value();
    try {
        winrt::hstring hxaml = winrt::to_hstring(xaml);
        auto element = winrt::Microsoft::UI::Xaml::Markup::XamlReader::Load(hxaml);
        // Store as an opaque handle — JS accesses via binder API
        return Napi::Boolean::New(env, true);
    } catch (const winrt::hresult_error& ex) {
        Napi::Error::New(env,
            "XamlReader::Load failed: " + winrt::to_string(ex.message()))
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }
}

Napi::Value CreateWindow(const Napi::CallbackInfo& info) {
    auto env = info.Env();
    try {
        g_window = winrt::Microsoft::UI::Xaml::Window();
        if (info.Length() > 0 && info[0].IsString()) {
            g_window.Title(winrt::to_hstring(info[0].As<Napi::String>().Utf8Value()));
        }
        return Napi::Boolean::New(env, true);
    } catch (const winrt::hresult_error& ex) {
        Napi::Error::New(env,
            "Window creation failed: " + winrt::to_string(ex.message()))
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }
}

Napi::Value ActivateWindow(const Napi::CallbackInfo& info) {
    auto env = info.Env();
    if (!g_window) {
        Napi::Error::New(env, "No window created").ThrowAsJavaScriptException();
        return env.Undefined();
    }
    g_window.Activate();
    return Napi::Boolean::New(env, true);
}

void RegisterXamlLoader(Napi::Env env, Napi::Object exports) {
    exports.Set("loadXaml", Napi::Function::New(env, LoadXaml));
    exports.Set("createWindow", Napi::Function::New(env, CreateWindow));
    exports.Set("activateWindow", Napi::Function::New(env, ActivateWindow));
}

} // namespace winuidevkit
