// Bootstrap — initialize Windows App Runtime from C++/WinRT, exposed via N-API.

#include <napi.h>
#include <winrt/Microsoft.Windows.ApplicationModel.DynamicDependency.h>

namespace winuidevkit {

constexpr uint32_t SDK_VERSION_MAJOR_MINOR = 0x00010008; // 1.8

static bool g_bootstrapped = false;

Napi::Value Initialize(const Napi::CallbackInfo& info) {
    if (g_bootstrapped) {
        return info.Env().Undefined();
    }

    try {
        auto result = winrt::Microsoft::Windows::ApplicationModel::DynamicDependency::
            Bootstrap::Initialize(SDK_VERSION_MAJOR_MINOR);
        g_bootstrapped = true;
        return Napi::Boolean::New(info.Env(), true);
    } catch (const winrt::hresult_error& ex) {
        Napi::Error::New(info.Env(),
            "Bootstrap failed: " + winrt::to_string(ex.message()))
            .ThrowAsJavaScriptException();
        return info.Env().Undefined();
    }
}

Napi::Value Shutdown(const Napi::CallbackInfo& info) {
    if (g_bootstrapped) {
        winrt::Microsoft::Windows::ApplicationModel::DynamicDependency::
            Bootstrap::Shutdown();
        g_bootstrapped = false;
    }
    return info.Env().Undefined();
}

void RegisterBootstrap(Napi::Env env, Napi::Object exports) {
    exports.Set("bootstrapInitialize", Napi::Function::New(env, Initialize));
    exports.Set("bootstrapShutdown", Napi::Function::New(env, Shutdown));
}

} // namespace winuidevkit
