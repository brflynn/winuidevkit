// N-API addon entry point — registers all native exports.

#include <napi.h>

// Forward declarations from individual modules
namespace winuidevkit {
    Napi::Value Initialize(const Napi::CallbackInfo& info);
    Napi::Value Shutdown(const Napi::CallbackInfo& info);
    Napi::Value LoadXaml(const Napi::CallbackInfo& info);
    Napi::Value CreateWindow(const Napi::CallbackInfo& info);
    Napi::Value FindName(const Napi::CallbackInfo& info);
}

Napi::Object Init(Napi::Env env, Napi::Object exports) {
    // Bootstrap
    exports.Set("initialize", Napi::Function::New(env, winuidevkit::Initialize));
    exports.Set("shutdown", Napi::Function::New(env, winuidevkit::Shutdown));

    // XAML
    exports.Set("loadXaml", Napi::Function::New(env, winuidevkit::LoadXaml));
    exports.Set("createWindow", Napi::Function::New(env, winuidevkit::CreateWindow));

    // Binder
    exports.Set("findName", Napi::Function::New(env, winuidevkit::FindName));

    return exports;
}

NODE_API_MODULE(winuidevkit, Init)
