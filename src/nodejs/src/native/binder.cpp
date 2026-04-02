// Binder — find named elements and register event callbacks via N-API.

#include <napi.h>
#include <winrt/Microsoft.UI.Xaml.h>
#include <winrt/Microsoft.UI.Xaml.Controls.h>

namespace winuidevkit {

// Forward declaration of window's content element (set by xaml_loader)
winrt::Microsoft::UI::Xaml::FrameworkElement GetContentRoot();

Napi::Value FindName(const Napi::CallbackInfo& info) {
    auto env = info.Env();
    if (info.Length() < 1 || !info[0].IsString()) {
        Napi::TypeError::New(env, "Expected element name string").ThrowAsJavaScriptException();
        return env.Undefined();
    }

    std::string name = info[0].As<Napi::String>().Utf8Value();
    try {
        auto root = GetContentRoot();
        auto element = root.FindName(winrt::to_hstring(name));
        if (element) {
            return Napi::Boolean::New(env, true);
        }
        return env.Null();
    } catch (const winrt::hresult_error& ex) {
        Napi::Error::New(env,
            "FindName failed: " + winrt::to_string(ex.message()))
            .ThrowAsJavaScriptException();
        return env.Undefined();
    }
}

void RegisterBinder(Napi::Env env, Napi::Object exports) {
    exports.Set("findName", Napi::Function::New(env, FindName));
}

} // namespace winuidevkit
